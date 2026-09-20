#!/usr/bin/env python3
"""Tests for tools/tasks.py. Run: python3 tools/test_tasks.py

Covers:
1. The transition table in tasks.py matches the single-writer table in
   workflow.md §2 (the two sources of truth must not drift).
2. A full CLI round-trip in a temp project: init, scaffold, transitions,
   illegal-transition rejections, board/next/check output, rename/remove.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE / "tasks.py"
WORKFLOW = HERE.parent / "workflow.md"

FAILURES = []


def check(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        FAILURES.append(name)
        print(f" FAIL {name}: {e}")
    except Exception as e:  # noqa: BLE001
        FAILURES.append(name)
        print(f" ERROR {name}: {type(e).__name__}: {e}")


def load_tasks_module():
    spec = importlib.util.spec_from_file_location("laaw_tasks", TASKS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_workflow_table():
    """(from, to, writer) triples from the §2 table in workflow.md."""
    text = WORKFLOW.read_text()
    sec = text.split("## 2.", 1)[1].split("## 3.", 1)[0]
    out = set()
    for line in sec.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        if cells[0] == "From" or set(cells[0]) <= set("-: "):
            continue
        frm = cells[0].replace("`", "").strip()
        if frm == "—":
            frm = "none"
        to = cells[1].replace("`", "").strip()
        writer = cells[2].replace("`", "").strip()
        out.add((frm, to, writer))
    return out


def test_transition_table_matches_workflow():
    mod = load_tasks_module()
    got = {(k[0], k[1], v) for k, v in mod.TRANSITIONS.items()}
    want = parse_workflow_table()
    if got != want:
        only_doc = sorted(want - got)
        only_cli = sorted(got - want)
        raise AssertionError(
            f"workflow.md §2 and tasks.py TRANSITIONS disagree.\n"
            f"  only in workflow.md: {only_doc}\n  only in tasks.py:   {only_cli}"
        )


def run(tmp, *args, check_rc=True):
    p = subprocess.run(
        [sys.executable, str(TASKS), "--root", str(tmp), *args],
        capture_output=True,
        text=True,
    )
    if check_rc and p.returncode != 0:
        raise AssertionError(f"{' '.join(args)} failed (rc={p.returncode}): {p.stderr.strip()}")
    return p


def test_cli_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        run(tmp, "init")
        state = Path(tmp) / ".ai" / "tasks" / "state.json"
        assert state.exists() and (Path(tmp) / ".ai" / "context" / "index.md").exists()

        # scaffold
        out = run(tmp, "new", "Add login form", "--desc", "Let users log in.")
        assert "t1" in out.stdout
        out = run(tmp, "new", "Auth flow", "--super")
        assert "t2" in out.stdout
        run(tmp, "subtask", "t2", "Login form")
        run(tmp, "subtask", "t2", "Session store")
        td = Path(tmp) / ".ai" / "tasks"
        assert (td / "t1_add-login-form.md").exists()
        assert (td / "t2_auth-flow/task.md").exists()
        assert (td / "t2_auth-flow/t2.1_login-form.md").exists()
        assert (td / "t2_auth-flow/t2.2_session-store.md").exists()
        # scaffolded leaf content comes from the template
        assert "# t1 — Add login form" in (td / "t1_add-login-form.md").read_text()
        assert "Description: Let users log in." in (td / "t1_add-login-form.md").read_text()

        st = json.loads(state.read_text())
        assert [r["id"] for r in st["roots"]] == ["t1", "t2"]
        assert [c["id"] for c in st["roots"][1]["children"]] == ["t2.1", "t2.2"]

        # leaf path: draft -> in-progress -> impl-review -> ctx-review -> done
        run(tmp, "set-status", "t1", "in-progress")
        bad = run(tmp, "set-status", "t1", "done", check_rc=False)
        assert bad.returncode != 0 and "illegal transition" in bad.stderr, bad.stderr
        run(tmp, "set-status", "t1", "impl-review")
        run(tmp, "set-status", "t1", "ctx-review")
        run(tmp, "set-status", "t1", "done")
        bad = run(tmp, "set-status", "t1", "draft", check_rc=False)
        assert bad.returncode != 0 and "done" in bad.stderr, bad.stderr

        # super-task path
        run(tmp, "set-status", "t2", "in-progress")
        bad = run(tmp, "set-status", "t2", "impl-review", check_rc=False)
        assert bad.returncode != 0, "super-task must not reach impl-review"
        run(tmp, "set-status", "t2.1", "in-progress")
        run(tmp, "set-status", "t2.1", "impl-review")
        bad = run(tmp, "set-status", "t2.1", "ctx-review", check_rc=False)
        assert bad.returncode != 0, "subtasks have no context gate"
        run(tmp, "set-status", "t2.1", "done")
        out = run(tmp, "next")
        assert "t2.2" in out.stdout, out.stdout

        # rename + remove (draft tasks only)
        run(tmp, "new", "Temp task")
        out = run(tmp, "rename", "t3", "Temporary helper")
        assert "t3_temporary-helper.md" in out.stdout
        assert (td / "t3_temporary-helper.md").exists()
        run(tmp, "remove", "t3")
        assert not (td / "t3_temporary-helper.md").exists()
        bad = run(tmp, "rename", "t2", "Nope", check_rc=False)
        assert bad.returncode != 0, "renaming a non-draft task must fail"

        # board / status / check
        out = run(tmp, "board")
        for token in ("t1", "t2", "t2.1", "t2.2", "| done |", "| in-progress |", "| draft |"):
            assert token in out.stdout, f"{token!r} not in board:\n{out.stdout}"
        out = run(tmp, "status", "t2.2")
        assert "draft" in out.stdout
        out = run(tmp, "check")
        assert out.returncode == 0, out.stderr

        # state is the only status store: no status words in task files
        for f in td.rglob("*.md"):
            body = f.read_text()
            assert "in-progress" not in body and "impl-review" not in body, f"{f} holds a status"


def main():
    check("transition table matches workflow.md §2", test_transition_table_matches_workflow)
    check("CLI round-trip", test_cli_roundtrip)
    if FAILURES:
        print(f"\n{len(FAILURES)} test(s) failed.")
        sys.exit(1)
    print("\nAll tests passed.")


if __name__ == "__main__":
    main()
