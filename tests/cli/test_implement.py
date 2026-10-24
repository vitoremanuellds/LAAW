"""Tests for laaw.cli.implement."""

import argparse
import tempfile
import unittest

from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.status import Status


def _task(id: str, name: str, status: Status, deps: list[str] | None = None) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status, deps=deps or [])


class ImplementTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_planning_no_deps_when_implement_then_in_progress(self):
        # arrange
        from laaw.cli import implement
        from tests.cli.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(implement, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.IN_PROGRESS)

    def test_given_planning_with_done_dep_when_implement_then_in_progress(self):
        # arrange
        from laaw.cli import implement
        from tests.cli.helpers import read_state, run_in_dir, write_state

        write_state(
            self.dir,
            ProjectState(
                tasks=[
                    _task("t01", "Dep", Status.DONE),
                    _task("t02", "Main", Status.PLANNING, deps=["t01"]),
                ]
            ),
        )

        # act
        args = argparse.Namespace(id="t02")
        code = run_in_dir(implement, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[1].status, Status.IN_PROGRESS)

    def test_given_planning_with_undone_dep_when_implement_then_refused_lists_dep(self):
        # arrange
        from laaw.cli import implement
        from tests.cli.helpers import run_in_dir, state_json_bytes, write_state

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
        args = argparse.Namespace(id="t02")
        code = run_in_dir(implement, args, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_propagating_context_when_implement_then_resume_to_in_progress(self):
        # arrange
        from laaw.cli import implement
        from tests.cli.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PROPAGATING_CONTEXT)]))

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(implement, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.IN_PROGRESS)


if __name__ == "__main__":
    unittest.main()
