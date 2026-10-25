"""Tests for laaw.core.lifecycle.remove."""

import tempfile
import unittest
from pathlib import Path

from laaw.core import lifecycle
from laaw.core.base import Refuse
from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.domain.status import Status
from tests.core.helpers import read_state, run_in_dir, state_json_bytes, write_state


def _task(id: str, name: str, status: Status = Status.CANCELLED, deps: list[str] | None = None) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status, deps=deps or [])


class RemoveTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_cancelled_task_when_remove_then_removed_from_state_and_folder_deleted(self):
        # arrange: cancelled task with an existing folder and files
        from laaw.model.subtask import Subtask

        state = ProjectState(tasks=[
            _task("t01", "Add login"),
            Task(id="t02", name="Auth", desc="d", type="supertask", status=Status.DONE),
        ])
        write_state(self.dir, state)
        folder = Path(self.dir) / "t01_add-login"
        folder.mkdir(parents=True)
        (folder / "task.md").write_text("x")

        # act
        message, code = run_in_dir(lifecycle.remove, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        self.assertIn("removed", message)
        loaded = read_state(self.dir)
        self.assertNotIn("t01", [t.id for t in loaded.tasks])
        self.assertFalse(folder.is_dir())
        tasks_md = (Path(self.dir) / "tasks.md").read_text()
        self.assertNotIn("t01", tasks_md)

    def test_given_non_cancelled_task_when_remove_then_refused_no_write(self):
        # arrange
        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login", Status.PLANNING)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.remove, self.dir, "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_cancelled_task_with_dependents_when_remove_then_refused_no_write(self):
        # arrange: t02 depends on cancelled t01
        write_state(self.dir, ProjectState(tasks=[
            _task("t01", "Add login"),
            _task("t02", "Auth", status=Status.NOT_PLANNED, deps=["t01"]),
        ]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.remove, self.dir, "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_cancelled_supertask_with_subtasks_when_remove_then_refused_no_write(self):
        # arrange
        from laaw.model.subtask import Subtask

        write_state(self.dir, ProjectState(tasks=[
            Task(id="t01", name="Auth", desc="d", type="supertask", status=Status.CANCELLED,
                 subtasks=[Subtask(id="t01.1", name="JWT", desc="d", status=Status.NOT_PLANNED)]),
        ]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.remove, self.dir, "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_cancelled_subtask_when_remove_then_removed_from_parent_and_folder_deleted(self):
        # arrange: cancelled subtask with nested folder and files
        from laaw.model.subtask import Subtask

        state = ProjectState(tasks=[
            Task(id="t01", name="Auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t01.1", name="JWT", desc="d", status=Status.CANCELLED)]),
        ])
        write_state(self.dir, state)
        folder = Path(self.dir) / "t01_auth" / "t01.1_jwt"
        folder.mkdir(parents=True)
        (folder / "task.md").write_text("x")

        # act
        message, code = run_in_dir(lifecycle.remove, self.dir, "t01.1")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertNotIn("t01.1", [s.id for s in loaded.tasks[0].subtasks])
        self.assertFalse(folder.is_dir())
        subtasks_md = (Path(self.dir) / "t01_auth" / "subtasks.md").read_text()
        self.assertNotIn("t01.1", subtasks_md)

    def test_given_unknown_id_when_remove_then_refused_no_write(self):
        # arrange
        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login")]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.remove, self.dir, "t99")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)


if __name__ == "__main__":
    unittest.main()
