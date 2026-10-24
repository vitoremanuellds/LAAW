"""Tests for laaw.cli.done."""

import argparse
import tempfile
import unittest

from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.status import Status


def _task(id: str, name: str, status: Status) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status)


class DoneTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_propagating_context_when_done_then_status_done(self):
        # arrange
        from laaw.cli import done
        from tests.cli.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PROPAGATING_CONTEXT)]))

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(done, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.DONE)

    def test_given_in_progress_when_done_then_refused(self):
        # arrange
        from laaw.cli import done
        from tests.cli.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.IN_PROGRESS)]))
        before = state_json_bytes(self.dir)

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(done, args, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertEqual(state_json_bytes(self.dir), before)


if __name__ == "__main__":
    unittest.main()
