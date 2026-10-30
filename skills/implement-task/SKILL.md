---
name: implement-task
description: Use when the user asks to implement an approved task or subtask. Checks dependencies, implements the task following its plan file, records deviations, handles cancellation, and runs the validations.
---

# Implement Task

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Identify the task folder:
   - Simple task: `.ai/tasks/t{0N}_task-name/`
   - Subtask: `.ai/tasks/t{0N}_supertask-name/t{0N}.{n}_subtask-name/`
2. Check dependencies from the table (`.ai/tasks/_tasks.md`, or the supertask's `subtasks.md` for subtasks). If any dependency is not `done`:
   - **Refuse to implement.** Tell the user which dependencies are unsatisfied. Stop.
3. Read the task's `task.md` and the context files linked in its Context section. This is your context for the task: do not read any other files from the codebase before finishing these.
4. Set the task's status to `in-progress` in `_tasks.md` (or the supertask's `subtasks.md`).
5. Implement following the Steps section, staying inside In scope.
6. Iterate with the user until the implementation is approved:
   - If the user requests a change that is incompatible with the approved plan, apply it **and record the deviation** in the task folder's `notes.md`: what changed, and why.
   - If the plan turns out to be unimplementable (a premise is wrong, something is missing), **stop and notify the user**, and record the deviation in `notes.md`. The approved plan cannot be edited: the user must re-plan the whole task with the agent (status back to `planning`). When the re-planned task is approved again, report its dependent tasks so the user can check the new plan still satisfies them.
   - If the user asks to abandon or cancel the task, mark it `cancelled` in `_tasks.md` (or the supertask's `subtasks.md`) and stop the work. Then scan `_tasks.md` and all supertask `subtasks.md` files for tasks that depend on it — they are blocked forever now. Report them to the user and let the user decide for each: cancel it too, re-plan it without the dependency, or replace the dependency with a new task. Never cancel dependents automatically.
7. Run the Validations section. Run the agent-doable validations yourself; tell the user which validations are human-only so they can run them.
8. Once the user approves the implementation, set the task's status to `propagating-context` and tell the user to proceed with context propagation (`propagate-context`).

## Rules

- The approved plan is the contract and is immutable: after approval, the only mutable files in the task folder are `notes.md` (and, for supertasks, `subtasks.md`). Any departure from the plan is a deviation and must be recorded in `notes.md`.
- A cancelled dependency never becomes `done`, so its dependents are blocked until the user acts on them. The table's Dependencies column is the mutable state ledger — re-pointing a dependency is a table edit.
- Do not expand scope. If you discover work that is out of scope, note it in `notes.md` and tell the user; do not do it.
- Context comes from the plan's Context section first: read the linked `.ai/context/` files before reading any other files from the codebase.
- Keep any new or edited project files consistent with the documented architecture in `.ai/context/`.
