#!/usr/bin/env python3
"""LAAW tasks CLI — the single writer of .ai/tasks/state.json.

Task state (ids, names, statuses, file paths) lives in ONE file:
.ai/tasks/state.json. It is written only by this CLI, never by hand.
Markdown task files hold content only (Description, Steps, Validations,
Context updates, Notes) — no status is ever written to a markdown file.

The CLI enforces the status state machine from workflow.md §2: every
set-status call is validated, and illegal transitions are refused with an
instructional error. tools/tests/ keeps this table in sync with
workflow.md.

This file is a thin entry point — the implementation lives in the
laaw_tasks/ package next to it:
  laaw_tasks/state.py     — state.json I/O + status state machine
  laaw_tasks/scaffold.py  — slugify + template scaffolding
  laaw_tasks/report.py    — board/next/check rendering
  laaw_tasks/cli.py       — argument parsing + command wiring

Commands (run from the project root, or pass --root /path/to/project):
  init                          create .ai/tasks/ (state.json, .gitignore) and .ai/context/ (index.md)
  new <name> [--super] [--desc T]   scaffold a root task as draft
  subtask <root-id> <name> [--desc T]  scaffold a child of a super-task as draft
  rename <id> <new-name>        rename a draft task and its file(s)
  remove <id>                   delete a draft task (and draft children) and its file(s)
  set-status <id> <status>      flip a status; validates the transition (workflow.md §2)
  status [id]                   one task's status line, or the whole board
  board                         the whole board as a markdown table
  next                          print the active task and the exact next action/question
  check                         report state/file consistency problems
"""

import sys
from pathlib import Path

# Make the sibling laaw_tasks/ package importable no matter where this
# script is invoked from.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from laaw_tasks.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
