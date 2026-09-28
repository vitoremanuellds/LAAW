---
name: plan-task
description: Use when the user asks to plan or create a task, or to plan a subtask of an existing supertask. Registers the task in the right index and creates its plan file. For new tasks, decides whether the task is simple or a supertask.
---

# Plan Task

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Understand the task the user described. Ask clarifying questions if the scope is unclear.
2. Decide what kind of planning this is:
   - **New simple task** — the steps fit comfortably in one task file (under 100 lines).
   - **New supertask** — the task is too big for one file: it splits naturally into several independent, reviewable chunks.
   - **Subtask** — the user asks to plan a subtask of an existing supertask. Work inside the supertask's folder; do not create a new top-level task.
3. Compute the ID:
   - New task: from `.ai/tasks/index.md`, `max(existing IDs) + 1`. If the index does not exist, create it with the table header.
   - Subtask: `t{N}.{next}`, read from the supertask's Subtask table.
4. Register the task:
   - New task: add a row to the index table with ID, Status, Name, Description (≤ 180 chars), Type (`simple` or `supertask`), Dependencies. Set the status to `planning` once the plan file is created. Tasks registered without a plan file stay `not-planned`.
   - Subtask: its row already exists in the supertask's Subtask table (add it if missing). Set its status to `planning` once the plan file is created. Do not touch the top-level index.
5. Create the plan file:
   - Simple task: `.ai/tasks/t{0N}_task-name.md`
   - Supertask: `.ai/tasks/t{0N}_task-name/task.md`, with a Subtask table listing its subtasks. Do NOT create subtask files or `new-info.md` yet — subtask files are only created when the user asks for them, and `new-info.md` is created on first subtask propagation.
   - Subtask: `.ai/tasks/t{0N}_supertask-name/t{0N}.{n}_subtask-name.md`
6. The plan file must contain: Title, Description, Context (link the relevant `.ai/context/` files), In scope / Out of scope, Steps (with pseudocode where useful), Validations (including any human-only checks), and Notes (required, initially empty).

## Rules

- Keep the plan file under 100 lines. If it grows beyond that, the task is a supertask.
- Subtask files are only created when the user explicitly asks to plan that subtask — never on your own initiative.
- Read only the context files relevant to this task (start from `.ai/context/index.md`).
- Present the plan to the user. Iterate with the user until the plan is approved. Do not start implementing.
