---
name: propagate-context
description: Use after a task or subtask implementation is approved. Writes the information the implementation created back to the supertask's new-info.md staging file (for subtasks) or to the context files (for simple tasks).
---

# Propagate Context

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Identify the task and its kind:
   - **Subtask** (file lives inside a supertask folder) → propagate to the supertask's `new-info.md` staging file.
   - **Simple task** → propagate to the context files in `.ai/context/`.

2. Gather the information the implementation created: new modules, architecture decisions, API surface, conventions, gotchas. Ignore trivia — context is for what a future agent needs. Describe the project's current state, not what a task did.

3. Write it back:
   - **Subtask:** append the information to the supertask's `new-info.md`. If the file does not exist, create it (and link it from `task.md`).
   - **Simple task:**
     - If the information belongs to an existing context file → update that file.
     - If it is genuinely new (a new module, a new decision) → create a new context file with a descriptive name (e.g. `auth-module.md`).
     - Update `.ai/context/index.md`: add rows for new files, refresh descriptions of updated files.
     - If the task made a context file obsolete → mark its Status as not valid (or rewrite it to reflect the new reality).
   - **Supertask final propagation** (when all subtasks are done): take the content of the supertask's `new-info.md` and distribute it into the context files as above.

4. Respect the 100-line limit for `.ai/` files: if a context file grows past 100 lines, split it into smaller files and keep the entry point linking one-way to the children.
5. Keep context agnostic to tasks: never mention task IDs, task names, or task files inside `.ai/context/` files (including the index). If a context file already contains such references, drop them while you are there.

6. Present the changes to the user. The user approves the context; only after approval is the propagation done.
7. Once the user approves the context, set the task's status to `done` (in the index, or in the supertask's subtask table).
