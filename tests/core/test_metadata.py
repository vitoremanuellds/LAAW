"""Tests for laaw.core.metadata (rename, desc, dep-add, dep-remove, promote)."""

import tempfile
import unittest
from pathlib import Path

from laaw.core import metadata
from laaw.core.base import Refuse
from laaw.constants import DESC_MAX_CHARS
from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.domain.status import Status


def _task(
    id: str,
    name: str,
    status: Status,
    deps: list[str] | None = None,
    type: str = "simple",
) -> Task:
    return Task(id=id, name=name, desc="d", type=type, status=status, deps=deps or [])


def _supertask_with_subtask() -> ProjectState:
    from laaw.model.subtask import Subtask

    return ProjectState(tasks=[
        Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.PLANNING,
             subtasks=[Subtask(id="t07.1", name="JWT", desc="d", status=Status.PLANNING)]),
    ])


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


    # --- promote ---------------------------------------------------------------

    def test_given_simple_planning_when_promote_then_supertask(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))

        # act
        message, code = run_in_dir(metadata.promote, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].type, "supertask")

    def test_given_in_progress_when_promote_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.IN_PROGRESS)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(metadata.promote, self.dir, "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_supertask_when_promote_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(
            self.dir,
            ProjectState(tasks=[_task("t01", "A", Status.PLANNING, type="supertask")]),
        )
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(metadata.promote, self.dir, "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_unknown_id_when_promote_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(metadata.promote, self.dir, "t99")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_subtask_when_promote_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, _supertask_with_subtask())
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(metadata.promote, self.dir, "t07.1")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    # --- subtask ids ------------------------------------------------------------

    def test_given_subtask_when_rename_then_folder_moved_inside_parent_and_name_updated(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        state = _supertask_with_subtask()
        write_state(self.dir, state)
        parent_folder = Path(self.dir) / "t07_auth"
        old_folder = parent_folder / "t07.1_jwt"
        old_folder.mkdir(parents=True)

        # act
        message, code = run_in_dir(metadata.rename, self.dir, "t07.1", "Token service")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].subtasks[0].name, "Token service")
        self.assertTrue((parent_folder / "t07.1_token-service").is_dir())
        self.assertFalse(old_folder.is_dir())

    def test_given_subtask_when_desc_then_updated_and_clamped(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, _supertask_with_subtask())

        # act
        message, code = run_in_dir(metadata.desc, self.dir, "t07.1", "x" * 200)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(len(loaded.tasks[0].subtasks[0].desc), DESC_MAX_CHARS)

    def test_given_subtask_when_dep_add_then_sibling_dep_added(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import read_state, run_in_dir, write_state

        state = ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.PLANNING,
                 subtasks=[
                     Subtask(id="t07.1", name="a", desc="d", status=Status.DONE),
                     Subtask(id="t07.2", name="b", desc="d", status=Status.PLANNING),
                 ]),
        ])
        write_state(self.dir, state)

        # act
        message, code = run_in_dir(metadata.dep_add, self.dir, "t07.2", "t07.1")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertIn("t07.1", loaded.tasks[0].subtasks[1].deps)

    def test_given_subtask_when_dep_add_cross_scope_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        state = ProjectState(tasks=[
            _task("t01", "A", Status.DONE),
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.PLANNING,
                 subtasks=[]),
        ])
        from laaw.model.subtask import Subtask
        state.tasks[1].subtasks.append(Subtask(id="t07.1", name="a", desc="d", status=Status.PLANNING))
        write_state(self.dir, state)
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(metadata.dep_add, self.dir, "t07.1", "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_subtask_when_dep_remove_then_removed(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import read_state, run_in_dir, write_state

        state = ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.PLANNING,
                 subtasks=[
                     Subtask(id="t07.1", name="a", desc="d", status=Status.DONE),
                     Subtask(id="t07.2", name="b", desc="d", status=Status.PLANNING, deps=["t07.1"]),
                 ]),
        ])
        write_state(self.dir, state)

        # act
        message, code = run_in_dir(metadata.dep_remove, self.dir, "t07.2", "t07.1")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertNotIn("t07.1", loaded.tasks[0].subtasks[1].deps)


if __name__ == "__main__":
    unittest.main()
