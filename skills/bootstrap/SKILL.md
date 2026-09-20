---
name: bootstrap
description: One-time scaffold of .ai/tasks/ and .ai/context/ in a project. Creates the task index, the local gitignore for tasks, and the context index; triggers setup-project when context is empty. Use on first use of LAAW in a project, or when route finds no .ai/tasks/index.md.
---

# Skill: bootstrap

Bootstrap creates the working layout. It never touches project code and never creates tasks.

## Steps

1. Check `.ai/workflow/workflow.md` exists. If not: LAAW is not installed — tell the human to run
   `tools/sync-workflow.py <project-root>` from a LAAW checkout, then stop.
2. Check `.ai/tasks/index.md` exists. If it does: already bootstrapped — report and stop (route
   takes over).
3. Create `.ai/tasks/` and write `.ai/tasks/index.md`:

   ```markdown
   # Tasks

   | id | name | status |
   |---|---|---|
   ```

4. Write `.ai/tasks/.gitignore` containing exactly:

   ```text
   *
   ```

   Tasks are local working files and never enter git history.
5. Create `.ai/context/` and write `.ai/context/index.md`:

   ```markdown
   # Context index

   | file | summary |
   |---|---|
   ```

6. Check whether `.ai/context/` has any topic files besides `index.md`. If not: hand off to
   **setup-project** and stop. If yes: report "bootstrap complete" and stop (route takes over).

## Rules

- Idempotent: if the layout already exists, do not rewrite it — just report.
- Do not create task files, IDs, or status rows here; that is plan-task's job.
- Do not commit anything; setup-project's seeded context is committed by its own approval flow.
