"""Persistence + lookup: Store + State round-trip and find().

The only tests that touch the filesystem for state I/O — everything else
in the suite exercises the in-memory machine directly.
"""

import tempfile
import unittest
from pathlib import Path

from laaw_tasks.errors import TaskError
from laaw_tasks.persistence import Store
from laaw_tasks.state import State, Task


class StateIOTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.store = Store(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def test_save_then_load_roundtrip(self):
        st = State(self.store, {"roots": [{"id": "t1", "name": "Leaf", "status": "draft", "file": "t1_leaf.md"}]})
        st.save()
        self.assertTrue(self.store.state_path.exists())
        self.assertEqual(self.store.load_state(), st.to_dict())
        self.assertEqual(State.load(self.store).roots[0].name, "Leaf")

    def test_save_creates_missing_dirs(self):
        deep = self.root / "a" / "b"
        State(Store(deep), {"roots": []}).save()
        self.assertTrue(Store(deep).state_path.exists())

    def test_super_children_key_survives_roundtrip(self):
        """A super-task with no subtasks yet must stay a super-task after
        save/load (the 'children' key must survive even when empty)."""
        st = State(
            self.store,
            {"roots": [{"id": "t1", "name": "Super", "status": "draft", "file": "t1_super/task.md", "children": []}]},
        )
        st.save()
        self.assertEqual(self.store.load_state()["roots"][0]["children"], [])
        self.assertTrue(State.load(self.store).roots[0].is_super)

    def test_missing_state_raises(self):
        with self.assertRaises(TaskError) as ctx:
            State.load(self.store)
        self.assertIn("not bootstrapped", str(ctx.exception))

    def test_corrupt_state_raises(self):
        self.store.state_path.parent.mkdir(parents=True)
        self.store.state_path.write_text("{not json")
        with self.assertRaises(TaskError) as ctx:
            State.load(self.store)
        self.assertIn("corrupt", str(ctx.exception))

    def test_invalid_shape_raises(self):
        self.store.save_state({"no_roots": True})
        with self.assertRaises(TaskError) as ctx:
            State.load(self.store)
        self.assertIn("not a valid LAAW state", str(ctx.exception))

    def test_find_root_and_child(self):
        st = State(
            self.store,
            {
                "roots": [
                    {"id": "t1", "name": "Leaf", "status": "draft", "file": "t1_leaf.md"},
                    {
                        "id": "t2",
                        "name": "Super",
                        "status": "draft",
                        "file": "t2_super/task.md",
                        "children": [{"id": "t2.1", "name": "Child", "status": "draft", "file": "t2_super/t2.1_child.md"}],
                    },
                ]
            },
        )
        task, parent = st.find("t1")
        self.assertIsInstance(task, Task)
        self.assertEqual(task.id, "t1")
        self.assertIsNone(parent)
        task, parent = st.find("t2.1")
        self.assertEqual(task.id, "t2.1")
        self.assertIsInstance(parent, Task)
        self.assertEqual(parent.id, "t2")
        self.assertEqual(st.find("t9"), (None, None))


if __name__ == "__main__":
    unittest.main()
