"""End-to-end CLI integration: run the real tools/tasks.py as a subprocess
against a temp project. Ported from the original tools/test_tasks.py
round-trip, extended with the shape-rule cases.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TASKS = Path(__file__).resolve().parents[1] / "tasks.py"


def run(tmp, *args, check_rc=True):
    r = subprocess.run(
        [sys.executable, str(TASKS), "--root", str(tmp), *args],
        capture_output=True,
        text=True,
    )
    if check_rc and r.returncode != 0:
        raise AssertionError(f"command failed: {r.stderr}\n{r.stdout}")
    return r


class TestCliRoundtrip(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_full_flow(self):
        run(self.tmp, "init")
        # state.json is written only by the CLI; .ai/tasks/ holds no other
        # tracked files (.gitignore '*').
        run(self.tmp, "new", "Add login form")
        run(self.tmp, "new", "Auth flow", "--super")
        run(self.tmp, "subtask", "t2", "Password reset")
        run(self.tmp, "subtask", "t2", "Email verification")

        out = run(self.tmp, "status").stdout
        for token in ("t1", "t2", "t2.1", "t2.2", "draft"):
            self.assertIn(token, out)

        # board is the whole board as a markdown table, with a depends-on column
        out = run(self.tmp, "board").stdout
        for token in ("| id | name | status | depends |", "| t2.2 | Email verification | draft | — |"):
            self.assertIn(token, out)

        # status of one task
        out = run(self.tmp, "status", "t2.1").stdout
        self.assertIn("t2.1 | Password reset | draft | child of t2 | file:", out)

        # every markdown task file must be free of status strings
        td = self.tmp / ".ai" / "tasks"
        for f in td.rglob("*.md"):
            body = f.read_text()
            for s in ("draft", "in-progress", "impl-review", "ctx-review"):
                self.assertNotIn(s, body, f"status string {s!r} leaked into {f}")

        # next: two draft roots -> lists both, asks the human to pick
        out = run(self.tmp, "next").stdout
        self.assertIn("Multiple active roots", out)
        self.assertIn("t1 — Add login form (draft)", out)
        self.assertIn("t2 — Auth flow (draft)", out)

        # rename a draft super-task (draft children allowed): the folder and
        # every child file path must follow
        run(self.tmp, "rename", "t2", "Auth & sessions")
        out = run(self.tmp, "status", "t2").stdout
        self.assertIn("Auth & sessions", out)
        out = run(self.tmp, "status", "t2.1").stdout
        self.assertIn("t2_auth-sessions/t2.1_password-reset.md", out)

        # rename a draft child task; its file must follow (while all draft)
        run(self.tmp, "rename", "t2.2", "Email verification flow")
        out = run(self.tmp, "status", "t2.2").stdout
        self.assertIn("Email verification flow", out)
        self.assertIn("t2.2_email-verification-flow.md", out)

        # subtasks can be added and removed while the root is still draft
        run(self.tmp, "subtask", "t2", "Throwaway")
        run(self.tmp, "remove", "t2.3")
        out = run(self.tmp, "status").stdout
        self.assertNotIn("t2.3", out)

        run(self.tmp, "set-status", "t1", "in-progress")
        bad = run(self.tmp, "set-status", "t1", "done", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("illegal transition", bad.stderr)

        # super-task must not reach impl-review (no gate of its own)
        run(self.tmp, "set-status", "t2", "in-progress")
        # re-planning a live super-task: subtasks that have not started may still be
        # added, renamed, and removed while the root is in-progress (workflow.md §4)
        run(self.tmp, "subtask", "t2", "Late child")
        out = run(self.tmp, "status").stdout
        self.assertIn("| t2.3 | Late child | draft |", out)
        run(self.tmp, "rename", "t2.3", "Session refresh")
        run(self.tmp, "remove", "t2.3")
        out = run(self.tmp, "status").stdout
        self.assertNotIn("t2.3", out)
        bad = run(self.tmp, "set-status", "t2", "impl-review", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("impl-review", bad.stderr)

        # super-task must not reach ctx-review while subtasks are live
        bad = run(self.tmp, "set-status", "t2", "ctx-review", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("all subtasks must be done", bad.stderr)

        run(self.tmp, "set-status", "t1", "impl-review")
        # a root task must not skip the context gate
        bad = run(self.tmp, "set-status", "t1", "done", check_rc=False)
        self.assertNotEqual(bad.returncode, 0, "impl-review → done is subtasks only")
        run(self.tmp, "set-status", "t1", "ctx-review")
        run(self.tmp, "set-status", "t1", "done")
        bad = run(self.tmp, "set-status", "t1", "draft", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("done", bad.stderr)

        # a done task must not be renamed (rename is draft-only, §5)
        bad = run(self.tmp, "rename", "t1", "Login v2", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("not draft", bad.stderr)

        run(self.tmp, "set-status", "t2.1", "in-progress")
        run(self.tmp, "set-status", "t2.1", "impl-review")
        run(self.tmp, "set-status", "t2.1", "done")

        # subtasks have no context gate
        bad = run(self.tmp, "set-status", "t2.2", "ctx-review", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)

        # check should pass at this point
        run(self.tmp, "check")

        # next: t2 is the only live root
        out = run(self.tmp, "next").stdout
        self.assertIn("t2.2", out)
        self.assertIn("implement-task", out)

        # a draft child of a live super-task may still be renamed (re-planning, §4);
        # once the child leaves draft, its shape is frozen
        run(self.tmp, "rename", "t2.2", "Session store")
        run(self.tmp, "set-status", "t2.2", "in-progress")
        bad = run(self.tmp, "rename", "t2.2", "Late name", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("not draft", bad.stderr)
        bad = run(self.tmp, "remove", "t2.2", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("not draft", bad.stderr)

        # finish the last subtask, then the parent can take the context gate
        run(self.tmp, "set-status", "t2.2", "impl-review")
        run(self.tmp, "set-status", "t2.2", "done")

        # remove a non-draft must fail
        bad = run(self.tmp, "remove", "t2.1", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("not draft", bad.stderr)

        run(self.tmp, "set-status", "t2", "ctx-review")
        run(self.tmp, "set-status", "t2", "done")

        # unknown id everywhere
        bad = run(self.tmp, "set-status", "t9", "done", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)

        # check passes at the end
        run(self.tmp, "check")


class TestCliDepends(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        run(self.tmp, "init")
        run(self.tmp, "new", "Auth core")
        run(self.tmp, "new", "API client")
        run(self.tmp, "new", "UI polish")

    def tearDown(self):
        self._tmp.cleanup()

    def test_depends_blocks_until_done(self):
        run(self.tmp, "depends", "t2", "t1")
        # board shows the depends-on column
        out = run(self.tmp, "board").stdout
        self.assertIn("| t2 | API client | draft | t1 |", out)
        # status line shows depends
        out = run(self.tmp, "status", "t2").stdout
        self.assertIn("depends: t1", out)
        # next marks it blocked
        out = run(self.tmp, "next").stdout
        self.assertIn("BLOCKED by t1 (draft)", out)
        # the CLI refuses to move a blocked task past draft
        bad = run(self.tmp, "set-status", "t2", "in-progress", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("blocked by t1", bad.stderr)
        # finish t1: unblocks t2
        run(self.tmp, "set-status", "t1", "in-progress")
        run(self.tmp, "set-status", "t1", "impl-review")
        run(self.tmp, "set-status", "t1", "ctx-review")
        run(self.tmp, "set-status", "t1", "done")
        run(self.tmp, "set-status", "t2", "in-progress")
        run(self.tmp, "check")

    def test_depends_validation(self):
        bad = run(self.tmp, "depends", "t1", "t1", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("itself", bad.stderr)
        bad = run(self.tmp, "depends", "t1", "t9", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("unknown task", bad.stderr)
        # cycle: t1 → t2 → t1
        run(self.tmp, "depends", "t1", "t2")
        bad = run(self.tmp, "depends", "t2", "t1", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("cycle", bad.stderr)
        # state is unchanged by the refused flip
        out = run(self.tmp, "status", "t2").stdout
        self.assertNotIn("depends", out)
        # --clear empties the list
        run(self.tmp, "depends", "t1", "--clear")
        out = run(self.tmp, "status", "t1").stdout
        self.assertNotIn("depends", out)

    def test_depends_is_draft_only(self):
        # t1 depends on t2: t1 is blocked, t2 is free
        run(self.tmp, "depends", "t1", "t2")
        # draft-only: a blocked draft task may still change its depends-on list
        run(self.tmp, "depends", "t1", "t2", "t3")
        # ...but not once it leaves draft
        run(self.tmp, "set-status", "t2", "in-progress")
        bad = run(self.tmp, "depends", "t2", "t3", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("not draft", bad.stderr)


class TestCliInitAndErrors(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_twice_fails(self):
        run(self.tmp, "init")
        bad = run(self.tmp, "init", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("already initialized", bad.stderr)

    def test_command_without_bootstrap_fails(self):
        bad = run(self.tmp, "status", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("not bootstrapped", bad.stderr)

    def test_subtask_on_leaf_root_fails(self):
        run(self.tmp, "init")
        run(self.tmp, "new", "Leaf")
        bad = run(self.tmp, "subtask", "t1", "child", check_rc=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("not a super-task", bad.stderr)


if __name__ == "__main__":
    unittest.main()
