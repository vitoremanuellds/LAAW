"""Tests for laaw.cli.register."""

import argparse
import tempfile
import unittest
from pathlib import Path

from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.status import Status


def _task(id: str, name: str, desc: str = "d", status: Status = Status.NOT_PLANNED) -> Task:
    return Task(id=id, name=name, desc=desc, type="simple", status=status)


class RegisterTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_empty_state_when_register_then_creates_task_and_folder(self):
        # arrange
        from laaw.cli import register
        from tests.cli.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState())

        # act
        args = argparse.Namespace(name="Add login", desc="Adds a login endpoint.", deps=[])
        code = run_in_dir(register, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(len(loaded.tasks), 1)
        task = loaded.tasks[0]
        self.assertEqual(task.id, "t01")
        self.assertEqual(task.name, "Add login")
        self.assertEqual(task.status, Status.NOT_PLANNED)
        self.assertTrue((Path(self.dir) / "t01_add-login").is_dir())

    def test_given_existing_task_when_register_then_next_id_and_distinct_folder(self):
        # arrange
        from laaw.cli import register
        from tests.cli.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "Add login")]))

        # act
        args = argparse.Namespace(name="Add auth", desc="", deps=[])
        code = run_in_dir(register, args, self.dir)

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[1].id, "t02")
        self.assertTrue((Path(self.dir) / "t02_add-auth").is_dir())

    def test_given_unknown_dep_when_register_then_refused_no_write(self):
        # arrange
        from laaw.cli import register
        from tests.cli.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState())
        before = state_json_bytes(self.dir)

        # act
        args = argparse.Namespace(name="X", desc="", deps=["t99"])
        code = run_in_dir(register, args, self.dir)

        # assert
        self.assertEqual(code, 1)
        self.assertEqual(state_json_bytes(self.dir), before)


if __name__ == "__main__":
    unittest.main()
