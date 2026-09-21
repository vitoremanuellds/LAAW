"""Scaffolding: Slugifier, TaskTemplate rendering, State lifecycle file
side-effects, and CLI init.

TaskTemplate.render is pure — no filesystem needed to assert on rendered
content. State.add_root/add_subtask exercise the file side-effects through
a temp-dir Store; CLI.cmd_init covers project bootstrap.
"""

import json
import tempfile
import unittest
from pathlib import Path

import laaw_tasks.scaffold as scaffold
from laaw_tasks.cli import CLI
from laaw_tasks.errors import TaskError
from laaw_tasks.persistence import Store
from laaw_tasks.state import State


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(scaffold.Slugifier.slugify("Add login form"), "add-login-form")

    def test_punctuation_collapse(self):
        self.assertEqual(scaffold.Slugifier.slugify("  Spaced  Out!! "), "spaced-out")

    def test_long_names_truncated(self):
        s = scaffold.Slugifier.slugify("A very long task name that goes on and on forever")
        self.assertLessEqual(len(s), 30)
        self.assertTrue(s and not s.endswith("-"))

    def test_no_slug_returns_task(self):
        self.assertEqual(scaffold.Slugifier.slugify("???"), "task")


class TestRenderTemplate(unittest.TestCase):
    def setUp(self):
        self.template = scaffold.TaskTemplate()

    def test_leaf(self):
        body = self.template.render("t7", "Add login", "Let users in.", False)
        self.assertIn("# t7 — Add login", body)
        self.assertIn("Description: Let users in.", body)
        self.assertNotIn("t{N}", body)
        self.assertNotIn("{name}", body)

    def test_default_description(self):
        body = self.template.render("t7", "Add login", None, False)
        self.assertIn(scaffold.DESCRIPTION_DEFAULT, body)

    def test_super(self):
        body = self.template.render("t2", "Auth flow", None, True)
        self.assertIn("# t2 — Auth flow", body)
        self.assertIn("Subtasks:", body)


class LifecycleScaffoldTests(unittest.TestCase):
    """File side-effects of State.add_root / State.add_subtask."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.store = Store(self.root)
        self.st = State(self.store, {"roots": []})

    def tearDown(self):
        self._tmp.cleanup()

    def test_add_root_writes_file(self):
        task, rel = self.st.add_root("Leaf")
        self.assertEqual(task.id, "t1")
        f = self.root / ".ai" / "tasks" / "t1_leaf.md"
        self.assertTrue(f.exists())
        self.assertIn("# t1 — Leaf", f.read_text())

    def test_add_subtask_creates_parent_dirs(self):
        self.st.add_root("Super", is_super=True)
        child, rel = self.st.add_subtask("t1", "Child")
        self.assertEqual(rel, "t1_super/t1.1_child.md")
        self.assertTrue((self.root / ".ai" / "tasks" / "t1_super" / "t1.1_child.md").exists())

    def test_refuses_overwrite(self):
        self.store.write("t1_leaf.md", "existing")
        with self.assertRaises(TaskError) as ctx:
            self.st.add_root("Leaf")
        self.assertIn("already exists", str(ctx.exception))

    def test_add_subtask_refused_after_root_left_draft(self):
        """Shape is fixed at plan time (workflow.md §4): no new subtasks once live."""
        task, _ = self.st.add_root("Super", is_super=True)
        task.status = "in-progress"
        with self.assertRaises(TaskError) as ctx:
            self.st.add_subtask("t1", "Late child")
        self.assertIn("left draft", str(ctx.exception))

    def test_rename_child_refused_when_sibling_live(self):
        self.st.add_root("Super", is_super=True)
        first, _ = self.st.add_subtask("t1", "One")
        self.st.add_subtask("t1", "Two")
        first.status = "in-progress"
        with self.assertRaises(TaskError) as ctx:
            self.st.rename("t1.2", "Two renamed")
        self.assertIn("child t1.1 is not draft", str(ctx.exception))

    def test_remove_missing_file_raises_task_error(self):
        self.st.add_root("Leaf")
        (self.root / ".ai" / "tasks" / "t1_leaf.md").unlink()
        with self.assertRaises(TaskError) as ctx:
            self.st.remove("t1")
        self.assertIn("does not exist", str(ctx.exception))

    def test_rename_missing_file_raises_task_error(self):
        self.st.add_root("Leaf")
        (self.root / ".ai" / "tasks" / "t1_leaf.md").unlink()
        with self.assertRaises(TaskError) as ctx:
            self.st.rename("t1", "Other")
        self.assertIn("does not exist", str(ctx.exception))


class TestInitProject(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.store = Store(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_creates_layout(self):
        CLI(self.store.root).cmd_init(None)
        td, cd = self.store.tasks_dir, self.store.context_dir
        self.assertTrue(td.joinpath("state.json").exists())
        self.assertEqual((td / ".gitignore").read_text(), "*\n")
        self.assertTrue(cd.joinpath("index.md").exists())
        self.assertEqual(json.loads(self.store.state_path.read_text()), {"roots": []})

    def test_init_is_not_idempotent(self):
        cli = CLI(self.store.root)
        cli.cmd_init(None)
        with self.assertRaises(TaskError) as ctx:
            cli.cmd_init(None)
        self.assertIn("already initialized", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
