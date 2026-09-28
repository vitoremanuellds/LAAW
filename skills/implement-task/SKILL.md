---
name: implement-task
description: Use when the user asks to implement an approved task or subtask. Checks dependencies, implements the task following its plan file, records deviations, and runs the validations.
---

# Implement Task

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Identify the task file:
   - Simple task: `.ai/tasks/t{0N}_task-name.md`
   - Subtask: `.ai/tasks/t{0N}_supertask-name/t{0N}.{n}_subtask-name.md`
2. Check dependencies from the index (`.ai/tasks/index.md`, or the supertask's Subtask table for subtasks). If any dependency is not `done`:
   - **Refuse to implement.** Tell the user which dependencies are unsatisfied. Stop.
3. Read the task file and the context files listed in its Context section.
4. Set the task's status to `in-progress` in the index (or the supertask's subtask table).
5. Implement following the Steps section, staying inside In scope.
6. Iterate with the user until the implementation is approved:
   - If the user requests a change that is incompatible with the approved plan, apply it **and record the deviation** in the task file's Notes section: what changed, and why.
   - If the plan turns out to be unimplementable (a premise is wrong, something is missing), **stop and notify the user**, and record the deviation in Notes.
7. Run the Validations section. Run the agent-doable validations yourself; tell the user which validations are human-only so they can run them.
8. Once the user approves the implementation, set the task's status to `propagating-context` and tell the user to proceed with context propagation (`propagate-context`).

## Rules

- The plan file is the contract. Any departure from it is a deviation and must be recorded in Notes.
- Do not expand scope. If you discover work that is out of scope, note it in Notes and tell the user; do not do it.
- Keep any new or edited project files consistent with the documented architecture in `.ai/context/`.
