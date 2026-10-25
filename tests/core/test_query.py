"""Tests for laaw.core.query (deps, dependents, check). Read-only."""

import tempfile
import unittest
from pathlib import Path

from laaw.core import query
from laaw.core.base import Refuse
from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.domain.status import Status


def _task(id: str, name: str, status: Status, deps: list[str] | None = None) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status, deps=deps or [])


class QueryTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # --- deps -------------------------------------------------------------------

    def test_given_planning_with_done_dep_when_deps_then_implementable(self):
        # arrange
        from tests.core.helpers import run_in_dir, write_state

        write_state(
            self.dir,
            ProjectState(tasks=[_task("t01", "Dep", Status.DONE), _task("t02", "Main", Status.PLANNING, deps=["t01"])]),
        )

        # act
        message, code = run_in_dir(query.deps, self.dir, "t02")

        # assert
        self.assertEqual(code, 0)
        self.assertIn("implementable", message)

    def test_given_planning_with_undone_dep_when_deps_then_blocked(self):
        # arrange
        from tests.core.helpers import run_in_dir, write_state

        write_state(
            self.dir,
            ProjectState(tasks=[_task("t01", "Dep", Status.PLANNING), _task("t02", "Main", Status.PLANNING, deps=["t01"])]),
        )

        # act
        message, code = run_in_dir(query.deps, self.dir, "t02")

        # assert
        self.assertIn("t01", message)
        self.assertIn("blocked", message)

    def test_given_planning_when_deps_json_then_json_output(self):
        # arrange
        import json

        from tests.core.helpers import run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))

        # act
        message, code = run_in_dir(query.deps, self.dir, "t01", as_json=True)

        # assert
        payload = json.loads(message)
        self.assertEqual(payload["id"], "t01")
        self.assertTrue(payload["implementable"])

    def test_given_unknown_id_when_deps_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, write_state

        write_state(self.dir, ProjectState())

        # act
        with self.assertRaises(Refuse):
            run_in_dir(query.deps, self.dir, "t99")

    # --- dependents -----------------------------------------------------------------

    def test_given_planning_with_dependent_when_dependents_then_lists_it(self):
        # arrange
        from tests.core.helpers import run_in_dir, write_state

        write_state(
            self.dir,
            ProjectState(tasks=[_task("t01", "A", Status.PLANNING), _task("t02", "B", Status.PLANNING, deps=["t01"])]),
        )

        # act
        message, code = run_in_dir(query.dependents, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        self.assertIn("t02", message)

    def test_given_planning_no_dependents_when_dependents_then_none(self):
        # arrange
        from tests.core.helpers import run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))

        # act
        message, code = run_in_dir(query.dependents, self.dir, "t01")

        # assert
        self.assertEqual(code, 0)
        self.assertIn("no dependents", message)

    # --- check ----------------------------------------------------------------------

    def test_given_consistent_state_when_check_then_no_drift(self):
        # arrange
        from tests.core.helpers import run_in_dir, write_state

        state = ProjectState(tasks=[_task("t01", "A", Status.PLANNING)])
        write_state(self.dir, state)
        folder = Path(self.dir) / "t01_a"
        folder.mkdir(parents=True)
        (folder / "task.md").write_text("# A\n")

        # act
        message, code = run_in_dir(query.check, self.dir)

        # assert
        self.assertEqual(code, 0)
        self.assertIn("no drift", message)

    def test_given_planning_without_task_md_when_check_then_drift(self):
        # arrange
        from tests.core.helpers import run_in_dir, write_state

        state = ProjectState(tasks=[_task("t01", "A", Status.PLANNING)])
        write_state(self.dir, state)
        (Path(self.dir) / "t01_a").mkdir(parents=True)

        # act
        message, code = run_in_dir(query.check, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertIn("task.md", message)

    def test_given_unknown_dep_when_check_then_drift(self):
        # arrange
        from tests.core.helpers import run_in_dir, write_state

        state = ProjectState(tasks=[_task("t01", "A", Status.PLANNING, deps=["t99"])])
        write_state(self.dir, state)
        (Path(self.dir) / "t01_a").mkdir(parents=True)
        (Path(self.dir) / "t01_a" / "task.md").write_text("# A\n")

        # act
        message, code = run_in_dir(query.check, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertIn("unknown dep t99", message)

    def test_given_planning_subtask_without_task_md_when_check_then_drift(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import run_in_dir, write_state

        state = ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t07.1", name="JWT", desc="d", status=Status.PLANNING)]),
        ])
        write_state(self.dir, state)
        (Path(self.dir) / "t07_auth").mkdir(parents=True)

        # act
        message, code = run_in_dir(query.check, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertIn("t07.1", message)

    def test_given_orphan_subtask_folder_when_check_then_drift(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import run_in_dir, write_state

        state = ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.PLANNING,
                 subtasks=[Subtask(id="t07.1", name="JWT", desc="d", status=Status.NOT_PLANNED)]),
        ])
        write_state(self.dir, state)
        parent = Path(self.dir) / "t07_auth"
        parent.mkdir(parents=True)
        (parent / "task.md").write_text("# Auth\n")
        (parent / "t07.1_jwt").mkdir(parents=True)
        (parent / "t09.9_orphan").mkdir(parents=True)

        # act
        message, code = run_in_dir(query.check, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertIn("subtask folder t07_auth/t09.9_orphan has no matching task in state", message)

    def test_given_subtask_when_deps_then_implementable(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import run_in_dir, write_state

        state = ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[
                     Subtask(id="t07.1", name="a", desc="d", status=Status.DONE),
                     Subtask(id="t07.2", name="b", desc="d", status=Status.PLANNING, deps=["t07.1"]),
                 ]),
        ])
        write_state(self.dir, state)

        # act
        message, code = run_in_dir(query.deps, self.dir, "t07.2")

        # assert
        self.assertEqual(code, 0)
        self.assertIn("implementable", message)

    def test_given_subtask_when_dependents_then_lists_sibling(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import run_in_dir, write_state

        state = ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[
                     Subtask(id="t07.1", name="a", desc="d", status=Status.PLANNING),
                     Subtask(id="t07.2", name="b", desc="d", status=Status.PLANNING, deps=["t07.1"]),
                 ]),
        ])
        write_state(self.dir, state)

        # act
        message, code = run_in_dir(query.dependents, self.dir, "t07.1")

        # assert
        self.assertEqual(code, 0)
        self.assertIn("t07.2", message)


if __name__ == "__main__":
    unittest.main()
