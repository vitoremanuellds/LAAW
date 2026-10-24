"""Tests for laaw.cli.cancel."""

import argparse
import tempfile
import unittest

from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.status import Status


def _task(id: str, name: str, status: Status, deps: list[str] | None = None) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status, deps=deps or [])


class CancelTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_planning_when_cancel_then_cancelled_and_reports_dependents(self):
        # arrange
        from laaw.cli import cancel
        from tests.cli.helpers import read_state, run_in_dir, write_state

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
        args = argparse.Namespace(id="t01")
        code = run_in_dir(cancel, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.CANCELLED)

    def test_given_done_when_cancel_then_refused_terminal_wall(self):
        # arrange
        from laaw.cli import cancel
        from tests.cli.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.DONE)]))
        before = state_json_bytes(self.dir)

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(cancel, args, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_cancelled_when_cancel_then_refused_terminal_wall(self):
        # arrange
        from laaw.cli import cancel
        from tests.cli.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.CANCELLED)]))
        before = state_json_bytes(self.dir)

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(cancel, args, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertEqual(state_json_bytes(self.dir), before)


if __name__ == "__main__":
    unittest.main()
