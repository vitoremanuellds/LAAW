"""Tests for laaw.cli.propagate."""

import argparse
import tempfile
import unittest

from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.status import Status


def _task(id: str, name: str, status: Status) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status)


class PropagateTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_in_progress_when_propagate_then_propagating_context(self):
        # arrange
        from laaw.cli import propagate
        from tests.cli.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.IN_PROGRESS)]))

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(propagate, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.PROPAGATING_CONTEXT)

    def test_given_planning_when_propagate_then_refused(self):
        # arrange
        from laaw.cli import propagate
        from tests.cli.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))
        before = state_json_bytes(self.dir)

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(propagate, args, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertEqual(state_json_bytes(self.dir), before)


if __name__ == "__main__":
    unittest.main()
