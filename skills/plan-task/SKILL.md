---
name: plan-task
description: Use when the user asks to plan or create a task. Registers the task in the index and creates its plan file. Decides whether the task is simple or a supertask.
---

# Plan Task

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Understand the task the user described. Ask clarifying questions if the scope is unclear.
2. Decide the task type:
   - **Simple task** — the steps fit comfortably in one task file (under 100 lines).
   - **Supertask** — the task is too big for one file: it splits naturally into several independent, reviewable chunks. Create it as a supertask.
3. Compute the next ID from `.ai/tasks/index.md`: `max(existing IDs) + 1`. If the index does not exist, create it with the table header.
4. Register the task in the index table:
   - ID, Status, Name, Description (≤ 180 chars), Type (`simple` or `supertask`), Dependencies.
   - Set the status to `planning` once the plan file is created. Tasks registered without a plan file (e.g. subtasks listed in a supertask's table) stay `not-planned`.
5. Create the plan file:
   - Simple task: `.ai/tasks/t{0N}_task-name.md`
   - Supertask: `.ai/tasks/t{0N}_task-name/task.md`, with a Subtask table listing its subtasks. Do NOT create subtask files yet — subtask files are only created when the user asks for them.
6. The plan file must contain: Title, Description, Context (link the relevant `.ai/context/` files), In scope / Out of scope, Steps (with pseudocode where useful), Validations (including any human-only checks), and Notes (empty).

## Rules

- Keep the plan file under 100 lines. If it grows beyond that, the task is a supertask.
- Read only the context files relevant to this task (start from `.ai/context/index.md`).
- Present the plan to the user. Iterate with the user until the plan is approved. Do not start implementing.
