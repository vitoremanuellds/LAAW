"""Tests for laaw.persistence (uses a temp dir; no files written outside it)."""

import tempfile
import unittest
from typing import override

from laaw import persistence
from laaw.model.state import ProjectState
from laaw.model.subtask import Subtask
from laaw.model.task import Task
from laaw.status import Status


class SaveLoadTextTest(unittest.TestCase):
    dir: str = ""

    @override
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def test_given_text_when_save_then_load_round_trips(self):
        # arrange
        path = f"{self.dir}/a.txt"
        # act
        persistence.save_text(path, "hello world")
        result = persistence.load_text(path)
        # assert
        self.assertEqual(result, "hello world")

    def test_given_missing_file_when_load_then_raises_file_not_found(self):
        # arrange
        path = f"{self.dir}/missing.txt"
        # act / assert
        with self.assertRaises(FileNotFoundError):
            persistence.load_text(path)


class EnsureDirTest(unittest.TestCase):
    dir: str = ""

    @override
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def test_given_nested_path_when_ensure_dir_then_creates_tree(self):
        # arrange
        path = f"{self.dir}/a/b/c"
        # act
        persistence.ensure_dir(path)
        # assert
        import os
        self.assertTrue(os.path.isdir(path))

    def test_given_existing_dir_when_ensure_dir_then_no_error(self):
        # arrange
        path = f"{self.dir}/exists"
        persistence.ensure_dir(path)
        # act / assert (idempotent, no exception)
        persistence.ensure_dir(path)


class ListFilesTest(unittest.TestCase):
    dir: str = ""

    @override
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def test_given_files_when_list_then_returns_sorted_names(self):
        # arrange
        persistence.save_text(f"{self.dir}/b.txt", "x")
        persistence.save_text(f"{self.dir}/a.txt", "x")
        # act
        result = persistence.list_files(self.dir)
        # assert
        self.assertEqual(result, ["a.txt", "b.txt"])

    def test_given_missing_dir_when_list_then_returns_empty(self):
        # arrange / act
        result = persistence.list_files(f"{self.dir}/nope")
        # assert
        self.assertEqual(result, [])


class StateRoundTripTest(unittest.TestCase):
    dir: str = ""
    path: str = ""

    @override
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name
        self.path = f"{self.dir}/tasks.json"

    def test_given_state_when_save_then_load_round_trips(self):
        # arrange
        state = ProjectState(tasks=[
            Task(id="t07", name="auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t07.1", name="a", desc="", status=Status.DONE)]),
            Task(id="t08", name="login", desc="d", type="simple", status=Status.NOT_PLANNED),
        ])
        # act
        persistence.save_state(state, self.path)
        restored = persistence.load_state(self.path)
        # assert
        self.assertEqual(restored, state)

    def test_given_saved_state_when_file_then_is_pretty_printed_json(self):
        # arrange
        state = ProjectState(tasks=[
            Task(id="t01", name="a", desc="", type="simple", status=Status.DONE),
        ])
        # act
        persistence.save_state(state, self.path)
        text = persistence.load_text(self.path)
        # assert
        self.assertTrue(text.startswith("{\n  "))
        self.assertTrue(text.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
