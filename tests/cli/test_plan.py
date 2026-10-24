"""Tests for laaw.cli.plan."""

import argparse
import tempfile
import unittest
from pathlib import Path

from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.status import Status


def _task(id: str, name: str, status: Status) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status)


class PlanTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_not_planned_when_plan_then_status_planning_and_scaffolded_files(self):
        # arrange
        from laaw.cli import plan
        from tests.cli.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login", Status.NOT_PLANNED)]))

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(plan, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.PLANNING)
        folder = Path(self.dir) / "t01_add-login"
        self.assertTrue((folder / "task.md").is_file())
        self.assertTrue((folder / "notes.md").is_file())
        content = (folder / "task.md").read_text()
        self.assertIn("## Title", content)
        self.assertIn("## Steps", content)

    def test_given_done_when_plan_then_refused(self):
        # arrange
        from laaw.cli import plan
        from tests.cli.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login", Status.DONE)]))
        before = state_json_bytes(self.dir)

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(plan, args, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_in_progress_when_plan_then_replan_to_planning(self):
        # arrange
        from laaw.cli import plan
        from tests.cli.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login", Status.IN_PROGRESS)]))

        # act
        args = argparse.Namespace(id="t01")
        code = run_in_dir(plan, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].status, Status.PLANNING)


if __name__ == "__main__":
    unittest.main()
