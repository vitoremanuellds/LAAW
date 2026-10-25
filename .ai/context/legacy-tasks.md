# Legacy tasks — pre-migration state

The project's task state used to live in old-model markdown files under `.ai/tasks/`: a hand-edited `index.md` table, one per-task plan file (`.md`) for simple tasks, and a folder per supertask with its own subtask table. When the CLI made `tasks.json` the source of truth, that whole state was backed up to **`.ai/tasks-legacy/`** before being migrated into the CLI state.

## What is in `.ai/tasks-legacy/`

- `index.md` — the old hand-edited task index (t01–t07 with statuses, types, deps).
- Per-task plan files for the simple tasks:
  - `t01_pressure-test-the-100-line-rule.md` — pressure-test the 100-line rule and att naming.
  - `t02_make-agents-md-hook-automatic-in-laaw-py.md` — make `sync workflow` write/stub the AGENTS.md Workflow section.
  - `t03_document-worktree-parallel-reconciliation.md` — cancelled; document or forbid parallel context writes.
  - `t04_add-worked-supertask-example-to-workflow-md.md` — cancelled; user skipped it.
  - `t05_deduplicate-workflow-md-rules.md` — deduplicate the 100-line/att/sizing rules to one canonical place each.
  - `t06_surface-the-100-line-exception-list.md` — surface the list of files allowed to exceed 100 lines.
- `t07_laaw-cli/` — the completed supertask folder: `task.md` with its subtask table, `notes.md`, `new-info.md` (staged context), per-subtask plan files, and spec att files.
- `tasks.json`, `tasks.md` — the state as it was at migration time (empty tasks.json; generated tables from the old index).

## How to use it

- Historical reference only: the live task state is in `.ai/tasks/tasks.json` (see [cli.md](cli.md)).
- The open simple tasks were re-registered into the CLI state during the migration; their plan content lives in the new `task.md` files, and the legacy copies remain here for diffing.
- Cancelled and done tasks (old t03, t04, t07) are not re-registered; they exist only in this backup.
