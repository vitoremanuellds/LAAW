# propagate-context

Aggregate and record context changes approved by the human.

For **subtasks**: propagate their `Context updates` to the parent task's `Context updates` section.
For **root tasks**: write the aggregated `Context updates` to `.ai/context/` files.

## When to use

- After a task's implementation is approved and it is in `contextualizing` status.
- When the human asks to propagate context.

## Steps

1. Run `python3 .ai/workflow/tools/laaw.py status <task-id>` to get the task's current state.
2. Read `workflow.md` (§2, §5, §6) for context rules.
3. Determine if the task is a root or a child:
   - **Child task**: Read the parent's task file. Merge the child's `Context updates` into
     the parent's `Context updates` section. Save the parent file.
   - **Root task**: Read `.ai/context/index.md`, then every file the task's `Context updates`
     section references. Make the exact changes listed in the task's `Context updates` section.
     Update `.ai/context/index.md` if new files were created or summaries changed.
4. Ask the human: **"Approve context changes for <task-id>?"**
   - For **subtasks**: show the changes made to the parent task's `Context updates` section.
   - For **root tasks**: show the exact edits to `.ai/context/` files.
   On approval, stop and wait for the human's answer. Do not ask and answer in the same response.

## Context approval outcomes

- **Approved**:
  1. Run `python3 .ai/workflow/tools/laaw.py set-status <task-id> done` to complete the task.
  2. Record the approval as its first action.
  3. For **root tasks** only: commit context changes:
     `git add .ai/context && git commit -m "<task-id>: context"`.
  4. Continue to the next task.
- **Rejected**: Fix the issues, re-ask.

## Notes

- Context changes to `.ai/context/` happen **only** for root tasks, always behind approval.
- Subtask context updates are aggregated up to the parent; the parent's `Context updates`
  section contains the full set of changes from all its children.
- Use `laaw.py board` to see the whole board; `laaw.py next` for the exact next action.
