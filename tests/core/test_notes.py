"""Tests for laaw.core.notes (append tagged note, re-render)."""

import tempfile
import unittest
from pathlib import Path

from laaw.constants import NOTE_WORD_CAP
from laaw.core import notes
from laaw.core.base import Refuse
from laaw.model.state import ProjectState
from laaw.model.task import Task
from laaw.domain.status import Status


def _task(id: str, name: str, status: Status = Status.IN_PROGRESS) -> Task:
    return Task(id=id, name=name, desc="d", type="simple", status=status)


class CoreNotesTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_in_progress_when_note_then_appended_and_rendered(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A")]))
        folder = Path(self.dir) / "t01_a"
        folder.mkdir(parents=True)

        # act
        message, code = run_in_dir(notes.add_note, self.dir, "t01", "progress", "did the thing")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].notes[0].tag, "progress")
        rendered = (folder / "notes.md").read_text()
        self.assertIn("## progress", rendered)
        self.assertIn("- did the thing", rendered)

    def test_given_over_cap_when_note_then_refused(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A")]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(notes.add_note, self.dir, "t01", "other", " ".join(["w"] * (NOTE_WORD_CAP + 1)))

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_two_notes_when_render_then_both_in_notes_md(self):
        # arrange
        from tests.core.helpers import run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A")]))
        folder = Path(self.dir) / "t01_a"
        folder.mkdir(parents=True)

        # act
        run_in_dir(notes.add_note, self.dir, "t01", "decision", "chose X")
        run_in_dir(notes.add_note, self.dir, "t01", "gotcha", "watch out for Y")

        # assert
        rendered = (folder / "notes.md").read_text()
        self.assertIn("## decision", rendered)
        self.assertIn("## gotcha", rendered)

    def test_given_not_planned_when_note_then_refused_no_write(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.NOT_PLANNED)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(notes.add_note, self.dir, "t01", "progress", "x")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_done_when_note_then_refused_no_write(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.DONE)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(notes.add_note, self.dir, "t01", "progress", "x")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_cancelled_when_note_then_refused_no_write(self):
        # arrange
        from tests.core.helpers import run_in_dir, state_json_bytes, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.CANCELLED)]))
        before = state_json_bytes(self.dir)

        # act
        with self.assertRaises(Refuse):
            run_in_dir(notes.add_note, self.dir, "t01", "progress", "x")

        # assert
        self.assertEqual(state_json_bytes(self.dir), before)

    def test_given_planning_when_note_then_appended_and_rendered(self):
        # arrange
        from tests.core.helpers import read_state, run_in_dir, write_state

        write_state(self.dir, ProjectState(tasks=[_task("t01", "A", Status.PLANNING)]))
        folder = Path(self.dir) / "t01_a"
        folder.mkdir(parents=True)

        # act
        message, code = run_in_dir(notes.add_note, self.dir, "t01", "progress", "planning step")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(loaded.tasks[0].notes[0].tag, "progress")
        rendered = (folder / "notes.md").read_text()
        self.assertIn("## progress", rendered)

    def test_given_subtask_when_add_note_then_note_stored_and_rendered_in_subtask_folder(self):
        # arrange
        from laaw.model.subtask import Subtask
        from tests.core.helpers import read_state, run_in_dir, write_state

        state = ProjectState(tasks=[
            Task(id="t07", name="Auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t07.1", name="JWT", desc="d", status=Status.PLANNING)]),
        ])
        write_state(self.dir, state)

        # act
        message, code = run_in_dir(notes.add_note, self.dir, "t07.1", "progress", "step done")

        # assert
        self.assertEqual(code, 0)
        loaded = read_state(self.dir)
        self.assertEqual(len(loaded.tasks[0].subtasks[0].notes), 1)
        rendered = (Path(self.dir) / "t07_auth" / "t07.1_jwt" / "notes.md").read_text()
        self.assertIn("## progress", rendered)


if __name__ == "__main__":
    unittest.main()
