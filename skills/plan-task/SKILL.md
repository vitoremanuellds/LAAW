---
name: plan-task
description: Use when the user asks to plan or create a task, or to plan a subtask of an existing supertask. Registers the task in the right index and creates its plan file. For new tasks, decides whether the task is simple or a supertask.
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
   - **New simple task / new supertask** — classify using the Simple vs supertask criteria below.
4. Compute the ID:
   - New task: from `.ai/tasks/index.md`, `max(existing IDs) + 1`. If the index does not exist, create it with the table header.
   - Subtask: `t{N}.{next}`, read from the supertask's Subtask table.
5. Register the task:
   - New task: add a row to the index table with ID, Status, Name, Description (≤ 180 chars), Type (`simple` or `supertask`), Dependencies. Set the status to `planning` once the plan file is created. Tasks registered without a plan file stay `not-planned`.
   - Subtask: its row already exists in the supertask's Subtask table (add it if missing). Set its status to `planning` once the plan file is created. Do not touch the top-level index.
6. Create the plan file:
   - Simple task: `.ai/tasks/t{0N}_task-name.md`
   - Supertask: `.ai/tasks/t{0N}_task-name/task.md`, with a Subtask table listing its subtasks. Do NOT create subtask files or `new-info.md` yet — subtask files are only created when the user asks for them, and `new-info.md` is created on first subtask propagation.
   - Subtask: `.ai/tasks/t{0N}_supertask-name/t{0N}.{n}_subtask-name.md`
7. The plan file must contain: Title, Description, Context, In scope / Out of scope, Steps (with pseudocode where useful), Validations (including any human-only checks), and Notes (required, initially empty).
   - Context lists the relevant `.ai/context/` files **with their paths** (e.g. `../../context/auth-module.md`). It is the direct door to context: whoever implements this task reads those files first, before touching the codebase.

## Simple vs supertask

For a new task, classify it using these criteria:

- **Hard signals → supertask, no debate:**
  - the plan file would exceed 100 lines;
  - the work spans 2+ modules/layers defined in `.ai/context/`.
- **Size trigger → present a split proposal:** estimated more than 600 lines of net change. If the work genuinely cannot be split into ≥2 independently verifiable chunks, it stays a simple task — but the plan must record the estimate and why it is not splittable.
- **Transparency:** always write the estimate (files touched, lines of change, modules spanned) and the simple/supertask decision with its reasoning into the plan file, so the user can veto it at the plan gate.

## Rules

- Keep the plan file under 100 lines. If it grows beyond that, the task is a supertask (hard signal above).
- Subtask files are only created when the user explicitly asks to plan that subtask — never on your own initiative.
- Context before codebase: read `.ai/context/index.md` first, then only the files that look relevant to the task's scope, and only then read codebase files.
- Present the plan to the user. Iterate with the user until the plan is approved. Do not start implementing.
