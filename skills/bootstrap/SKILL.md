---
name: bootstrap
description: One-time scaffold of .ai/tasks/ and .ai/context/ in a project, via `tasks.py init`. Creates the task state file, the local gitignore for tasks, and the context index; triggers setup-project when context is empty. Use on first use of LAAW in a project, or when route finds no state file.
---

# Skill: bootstrap

Bootstrap creates the working layout. It never touches project code and never creates tasks.

## Steps

1. Check `.ai/workflow/workflow.md` exists. If not: LAAW is not installed — tell the human to run
   `tools/sync-workflow.py <project-root>` from a LAAW checkout, then stop.
2. Check `.ai/tasks/state.json` exists. If it does: already bootstrapped — report and stop
   (route takes over).
3. From the project root run:

   ```text
   python3 .ai/workflow/tools/tasks.py init
   ```

   It creates `.ai/tasks/` (`state.json`, `.gitignore` containing `*` — tasks are local working
   files and never enter git history) and `.ai/context/` (`index.md`). If the command fails,
   show the error to the human and stop — do not scaffold by hand.
4. Check whether `.ai/context/` has any topic files besides `index.md`. If not: hand off to
   **setup-project** and stop. If yes: report "bootstrap complete" and stop (route takes over).

## Rules

- Idempotent: if the layout already exists, do not rewrite it — just report.
- Do not create task files, IDs, or status entries here; that is plan-task's job, via `tasks.py new`.
- Do not hand-edit `state.json`; do not commit anything (setup-project's seeded context is
  committed by its own approval flow).
