"""Tests for laaw.core.lifecycle (register, plan, implement, propagate, done, cancel)."""

import tempfile
import unittest
from pathlib import Path

from laaw.core import lifecycle
from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.domain.status import Status


def _task(id: str, name: str, status: Status = Status.NOT_PLANNED, deps: list[str] | None = None) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status, deps=deps or [])


class LifecycleTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # --- register -----------------------------------------------------------

    def test_given_empty_state_when_register_then_creates_task_and_folder(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState())

        # act
        message, code = run_in_dir(lifecycle.register, self.dir, "Add login", "Adds a login endpoint.", [])

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].id, "t01")
        self.assertEqual(loaded.tasks[0].status, Status.NOT_PLANNED)
        self.assertTrue((Path(self.dir) / "t01_add-login").is_dir())

    def test_given_existing_task_when_register_then_next_id_and_distinct_folder(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login")]))

        # act
        message, code = run_in_dir(lifecycle.register, self.dir, "Add auth", "", [])

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[1].id, "t02")
        self.assertTrue((Path(self.dir) / "t02_add-auth").is_dir())

    def test_given_unknown_dep_when_register_then_refused_no_write(self):
        # arrange
        from laaw.core.base import Refuse
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState())
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.register, self.dir, "X", "", ["t99"])

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_supertask_when_register_subtask_of_then_row_appended_not_planned(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import read_state, run_in_dir, write_state

        supertask = Task(id="t07", name="Auth", desc="d", type="supertask",
                        status=Status.PLANNING,
                        subtasks=[Subtask(id="t07.1", name="a", desc="", status=Status.DONE)])
        write_state(self.dir, ProjectState(tasks=[supertask]))

        # act
        message, code = run_in_dir(
            lifecycle.register, self.dir, "JWT service", "d", [], subtask_of="t07"
        )

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        subs = loaded.tasks[0].subtasks
        self.assertEqual(len(subs), 2)
        self.assertEqual(subs[1].id, "t07.2")
        self.assertEqual(subs[1].status, Status.NOT_PLANNED)
        self.assertIn("t07.2", message)

    def test_given_unknown_parent_when_register_subtask_of_then_refused(self):
        # arrange
        from laaw.core.base import Refuse
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState())
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.register, self.dir, "X", "d", [], subtask_of="t99")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_simple_parent_when_register_subtask_of_then_refused(self):
        # arrange
        from laaw.core.base import Refuse
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A")]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.register, self.dir, "X", "d", [], subtask_of="t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    # --- plan -----------------------------------------------------------------

    def test_given_not_planned_when_plan_then_status_planning_and_scaffolded_files(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login", Status.NOT_PLANNED)]))

        # act
        message, code = run_in_dir(lifecycle.plan, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.PLANNING)
        folder = Path(self.dir) / "t01_add-login"
        self.assertTrue((folder / "task.md").is_file())
        content = (folder / "task.md").read_text()
        self.assertIn("## Title", content)

    def test_given_done_when_plan_then_refused(self):
        # arrange
        from laaw.core.base import Refuse
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login", Status.DONE)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.plan, self.dir, "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_in_progress_when_plan_then_replan_to_planning(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login", Status.IN_PROGRESS)]))

        # act
        message, code = run_in_dir(lifecycle.plan, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.PLANNING)

    # --- implement ------------------------------------------------------------

    def test_given_planning_no_deps_when_implement_then_in_progress(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))

        # act
        message, code = run_in_dir(lifecycle.implement, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.IN_PROGRESS)

    def test_given_planning_with_undone_dep_when_implement_then_refused(self):
        # arrange
        from laaw.core.base import Refuse
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(
            self.dir,
            ProjectState(
                tasks=[
                    _task("t01", "Dep", Status.PLANNING),
                    _task("t02", "Main", Status.PLANNING, deps=["t01"]),
                ]
            ),
        )
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.implement, self.dir, "t02")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_propagating_context_when_implement_then_resume_to_in_progress(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PROPAGATING_CONTEXT)]))

        # act
        message, code = run_in_dir(lifecycle.implement, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.IN_PROGRESS)

    # --- propagate / done -----------------------------------------------------

    def test_given_in_progress_when_propagate_then_propagating_context(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.IN_PROGRESS)]))

        # act
        message, code = run_in_dir(lifecycle.propagate, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.PROPAGATING_CONTEXT)

    def test_given_propagating_context_when_done_then_status_done(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PROPAGATING_CONTEXT)]))

        # act
        message, code = run_in_dir(lifecycle.done, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.DONE)

    def test_given_in_progress_when_done_then_refused(self):
        # arrange
        from laaw.core.base import Refuse
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.IN_PROGRESS)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.done, self.dir, "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    # --- cancel -----------------------------------------------------------------

    def test_given_planning_when_cancel_then_cancelled_and_reports_dependents(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(
            self.dir,
            ProjectState(
                tasks=[
                    _task("t01", "A", Status.PLANNING),
                    _task("t02", "B", Status.PLANNING, deps=["t01"]),
                ]
            ),
        )

        # act
        message, code = run_in_dir(lifecycle.cancel, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        self.assertIn("t02", message)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.CANCELLED)

    def test_given_done_when_cancel_then_refused_terminal_wall(self):
        # arrange
        from laaw.core.base import Refuse
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.DONE)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(lifecycle.cancel, self.dir, "t01")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    # --- subtask ids ------------------------------------------------------------

    def _supertask_with_subtask(self) -> ProjectState:
        from laaw.model.subtask import Subtask
        return ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.PLANNING,
                 subtasks=[Subtask(id="t07.1", name="JWT", desc="d", status=Status.NOT_PLANNED)]),
        ])

    def test_given_subtask_when_plan_then_folder_scaffolded_and_supertask_in_progress(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, self._supertask_with_subtask())

        # act
        message, code = run_in_dir(lifecycle.plan, self.dir, "t07.1")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].subtasks[0].status, Status.PLANNING)
        self.assertEqual(loaded.tasks[0].status, Status.IN_PROGRESS)
        folder = Path(self.dir) / "t07_auth" / "t07.1_jwt"
        self.assertTrue((folder / "task.md").is_file())
        self.assertTrue((folder / "notes.md").is_file())

    def test_given_subtask_when_implement_then_in_progress(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t07.1", name="JWT", desc="d", status=Status.PLANNING)]),
        ]))

        # act
        message, code = run_in_dir(lifecycle.implement, self.dir, "t07.1")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].subtasks[0].status, Status.IN_PROGRESS)

    def test_given_subtask_when_propagate_then_propagating_context(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t07.1", name="JWT", desc="d", status=Status.IN_PROGRESS)]),
        ]))

        # act
        message, code = run_in_dir(lifecycle.propagate, self.dir, "t07.1")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].subtasks[0].status, Status.PROPAGATING_CONTEXT)

    def test_given_subtask_when_done_then_done(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t07.1", name="JWT", desc="d", status=Status.PROPAGATING_CONTEXT)]),
        ]))

        # act
        message, code = run_in_dir(lifecycle.done, self.dir, "t07.1")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].subtasks[0].status, Status.DONE)

    def test_given_subtask_with_sibling_dep_when_cancel_then_reports_blocked(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[
                     Subtask(id="t07.1", name="a", desc="d", status=Status.PLANNING),
                     Subtask(id="t07.2", name="b", desc="d", status=Status.PLANNING, deps=["t07.1"]),
                 ]),
        ]))

        # act
        message, code = run_in_dir(lifecycle.cancel, self.dir, "t07.1")

        # assert
        self.assertEqual(code, 0)
        self.assertIn("t07.2", message)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].subtasks[0].status, Status.CANCELLED)


if __name__ == "__main__":
    unittest.main()
