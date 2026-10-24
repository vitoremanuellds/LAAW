"""Tests for laaw.core.render_cmd (render)."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.domain.status import Status


def _state() -> ProjectState:
    state = ProjectState()
    state.add_task(
        Task(id="t01", name="Alpha", desc="d", type="simple", status=Status.PLANNING, deps=[])
    )
    return state


class RenderCmdTest(unittest.TestCase):
    cwd: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = str(Path(self.tmp.name) / ".ai" / "tasks")
        Path(self.dir).mkdir(parents=True)
        self.cwd = os.getcwd()
        os.chdir(self.tmp.name)

    def tearDown(self) -> None:
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def _write_state(self, state: ProjectState) -> None:
        path = Path(self.dir) / "tasks.json"
        path.write_text(json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8")

    def _files(self) -> dict[str, bytes]:
        return {p.name: p.read_bytes() for p in Path(self.dir).iterdir() if p.is_file()}

    def test_given_state_when_render_then_files_written(self) -> None:
        from laaw.core.render_cmd import render

        self._write_state(_state())
        message, code = render()
        self.assertEqual(code, 0)
        tasks_md = Path(self.dir) / "tasks.md"
        self.assertTrue(tasks_md.is_file())
        self.assertIn("t01", tasks_md.read_text(encoding="utf-8"))

    def test_given_render_twice_when_no_changes_then_identical_output(self) -> None:
        from laaw.core.render_cmd import render

        self._write_state(_state())
        render()
        first = self._files()
        render()
        second = self._files()
        self.assertEqual(first, second)

    def given_missing_state_when_render_then_empty_state_rendered(self) -> None:
        from laaw.core.render_cmd import render

        message, code = render()
        self.assertEqual(code, 0)
        tasks_md = Path(self.dir) / "tasks.md"
        self.assertTrue(tasks_md.is_file())


if __name__ == "__main__":
    unittest.main()
