"""Tests for laaw.core.metadata (rename, desc, dep-add, dep-remove)."""

import tempfile
import unittest
from pathlib import Path

from laaw.core import metadata
from laaw.core.base import Refuse
from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.domain.status import Status


def _task(id: str, name: str, status: Status, deps: list[str] | None = None) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status, deps=deps or [])


class MetadataTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # --- rename ---------------------------------------------------------------

    def test_given_planning_when_rename_then_folder_moved_and_name_updated(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        state = ProjectState(tasks=[_task("t01", "Old name", Status.PLANNING)])
        write_state(self.dir, state)
        folder = Path(self.dir) / "t01_old-name"
        folder.mkdir(parents=True)

        # act
        message, code = run_in_dir(metadata.rename, self.dir, "t01", "New name")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].name, "New name")
        self.assertTrue((Path(self.dir) / "t01_new-name").is_dir())
        self.assertFalse((Path(self.dir) / "t01_old-name").exists())

    def test_given_in_progress_when_rename_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.IN_PROGRESS)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(metadata.rename, self.dir, "t01", "B")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    # --- desc -------------------------------------------------------------------

    def test_given_planning_when_desc_then_updated_and_clamped(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))

        # act
        message, code = run_in_dir(metadata.desc, self.dir, "t01", "x" * 200)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(len(loaded.tasks[0].desc), 180)

    def test_given_done_when_desc_then_refused_terminal(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.DONE)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(metadata.desc, self.dir, "t01", "x")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    # --- dep-add ------------------------------------------------------------------

    def test_given_planning_when_dep_add_done_then_dep_added(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(
            self.dir,
            ProjectState(tasks=[_task("t01", "Dep", Status.DONE), _task("t02", "Main", Status.PLANNING)]),
        )

        # act
        message, code = run_in_dir(metadata.dep_add, self.dir, "t02", "t01")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[1].deps, ["t01"])

    def test_given_planning_when_dep_add_undone_then_added_with_warning(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(
            self.dir,
            ProjectState(tasks=[_task("t01", "Dep", Status.PLANNING), _task("t02", "Main", Status.PLANNING)]),
        )

        # act
        message, code = run_in_dir(metadata.dep_add, self.dir, "t02", "t01")

        # assert
        self.assertEqual(code, 0)
        self.assertIn("warning", message)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[1].deps, ["t01"])

    def test_given_planning_when_dep_add_cycle_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(
            self.dir,
            ProjectState(
                tasks=[_task("t01", "A", Status.PLANNING, deps=["t02"]), _task("t02", "B", Status.PLANNING)]
            ),
        )
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(metadata.dep_add, self.dir, "t02", "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_planning_when_dep_add_out_of_scope_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(
            self.dir,
            ProjectState(tasks=[_task("t01", "A", Status.PLANNING), _task("t02", "B", Status.PLANNING)]),
        )
        before = state_json_bytes(self.dir)

        # act — t02 depends on a subtask of another supertask (out of scope)
        with self.assertRaises(Refuse):
            run_in_dir(metadata.dep_add, self.dir, "t02", "t99.1")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    # --- dep-remove ----------------------------------------------------------------

    def test_given_planning_when_dep_remove_then_dep_removed(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(
            self.dir,
            ProjectState(tasks=[_task("t01", "A", Status.PLANNING, deps=["t02"]), _task("t02", "B", Status.DONE)]),
        )

        # act
        message, code = run_in_dir(metadata.dep_remove, self.dir, "t01", "t02")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].deps, [])

    def test_given_planning_when_dep_remove_not_present_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(metadata.dep_remove, self.dir, "t01", "t99")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)


if __name__ == "__main__":
    unittest.main()
