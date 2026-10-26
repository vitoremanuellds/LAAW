"""Tests for laaw.core.file_check. Read-only — no state."""

import tempfile
import unittest
from pathlib import Path

from laaw.core import file_check
from laaw.core.base import Refuse


class FileCheckTest(unittest.TestCase):
    dir: str = ""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write(self, name: str, words: int) -> str:
        path = Path(self.dir) / name
        path.write_text(" ".join(f"w{i}" for i in range(words)), encoding="utf-8")
        return str(path)

    # --- under threshold --------------------------------------------------------

    def test_given_file_under_threshold_when_check_then_ok_exit_0(self):
        path = self._write("small.md", 100)
        message, code = file_check.check(path)
        self.assertEqual(code, 0)
        self.assertIn("100 words", message)
        self.assertIn("\u2264", message)

    # --- over threshold ---------------------------------------------------------

    def test_given_file_over_threshold_when_check_then_split_exit_1(self):
        path = self._write("big.md", 1501)
        message, code = file_check.check(path)
        self.assertEqual(code, 1)
        self.assertIn("1501 words > 1500", message)
        self.assertIn("split it", message)

    def test_given_file_exactly_at_threshold_when_check_then_ok_exit_0(self):
        path = self._write("edge.md", 1500)
        message, code = file_check.check(path)
        self.assertEqual(code, 0)
        self.assertIn("1500 words", message)

    # --- exemption ----------------------------------------------------------------

    def test_given_exempt_workflow_md_when_check_then_exempt_exit_0(self):
        folder = Path(self.dir) / "workflow"
        folder.mkdir()
        path = folder / "workflow.md"
        path.write_text(" ".join(f"w{i}" for i in range(2000)), encoding="utf-8")
        message, code = file_check.check(str(path))
        self.assertEqual(code, 0)
        self.assertIn("exempt", message)

    def test_given_non_exempt_workflow_md_name_when_check_then_not_exempt(self):
        path = self._write("workflow.md", 1600)
        message, code = file_check.check(path)
        self.assertEqual(code, 1)
        self.assertNotIn("exempt", message)

    # --- refusals -----------------------------------------------------------------

    def test_given_missing_file_when_check_then_refuse(self):
        with self.assertRaises(Refuse):
            file_check.check(str(Path(self.dir) / "nope.md"))

    def test_given_directory_when_check_then_refuse(self):
        with self.assertRaises(Refuse):
            file_check.check(self.dir)


if __name__ == "__main__":
    unittest.main()
