---
name: plan-task
description: Use when the user asks to plan or create a task, or to plan a subtask of an existing supertask. Registers the task in state and creates its plan file via the CLI. For new tasks, decides whether the task is simple or a supertask.
---

# Plan Task

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Understand the task the user described. Ask clarifying questions if the scope is unclear.
2. Gather context before touching the codebase:
   - Read `.ai/context/index.md`, then the context files that look relevant to the task's scope.
   - Only after that, read codebase files — and only what you still cannot answer from context.
   - If the context is missing or stale for the task's scope, note it in the plan's Context section.
3. Decide what kind of planning this is:
   - **Subtask** — the user asks to plan a subtask of an existing supertask. Work inside the supertask's folder; do not create a new top-level task.
   - **New simple task / new supertask** — classify using the Simple vs supertask rule in workflow.md (hard signals first, then the sizing split proposal).
4. Register and plan via the CLI:
   - New task: `laaw task register --name <name> [--desc "..."] [--deps ...]` (→ `not-planned`), then `laaw task plan <id>` (→ `planning`; scaffolds `task.md` + `notes.md`). Do both in one swoop.
   - Subtask: register each listed subtask into state with `laaw task register --subtask-of <supertask-id>` when the supertask is planned (rows only, status stays `not-planned`). The row must exist before it can be planned; if it is missing, stop and tell the user. Then `laaw task plan <id>`. Planning a subtask sets the owning supertask to `in-progress` automatically.
5. Write the plan content into the scaffolded `task.md`: Title, Description, Context (with paths to `.ai/context/` files), In scope / Out of scope, Steps, Validations. The model owns this content; everything else is CLI-generated.
   - If the plan outgrows its size limit and must stay, split it into att files per the Splitting rule in workflow.md and link them from `task.md`.

## Rules

- Context before codebase: read `.ai/context/index.md` first, then only the files that look relevant to the task's scope, and only then read codebase files.
- Subtask files are only created when the user explicitly asks to plan that subtask — never on your own initiative.
- Statuses and IDs are owned by state; never hand-edit `tasks.json`, `tasks.md`, or `subtasks.md`.
- Present the plan to the user. Iterate with the user until the plan is approved. Do not start implementing.
