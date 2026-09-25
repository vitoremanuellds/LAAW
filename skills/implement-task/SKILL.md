# implement-task

Implement a task: execute its Steps, run Validations, fill Context updates, and ask for
implementation approval.

## When to use

- After a task's plan is approved (`in-progress` status).
- When the human asks to implement a task.

## Steps

1. Run `python3 .ai/workflow/tools/laaw.py status <task-id>` to get the task's current state.
2. Read `workflow.md` (§2, §5, §8) for task file rules and re-read discipline.
3. Re-read exactly the files named in the task's `Context:` section (workflow.md §8).
4. Execute each Step in order, flipping `- [ ]` to `- [x]` as you go.
   - **Never reword, merge, or delete step text** after plan approval.
   - Steps are implementation-ready: concrete actions the implementer can execute.
5. Run all Validations and record results.
6. If the task is a super-task:
   - Walk subtasks in ID order on their own turns.
   - Wait for each subtask's implementation approval before continuing.
   - Aggregate Context updates from all subtasks.
7. If the task is a root or leaf with Steps:
   - Fill the `Context updates` section with exact changes to make in `.ai/context/`.
8. Run `python3 .ai/workflow/tools/laaw.py set-status <task-id> contextualizing`
   to transition to the context gate.
9. Ask the human: **"Approve implementation of <task-id>?"** — show the diff summary
   and validation results. On approval, stop and wait for the human's answer.
   Do not ask and answer in the same response.

## Implementation approval outcomes

- **Approved**: Continue to context propagation (propagate-context).
- **Rejected**: Fix the issues, re-run Validations, then re-ask.

## Notes

- A root task with Steps always passes through the context gate (`contextualizing → done`).
- A subtask that is approved transitions directly to `done` (no context gate for subtasks).
- Use `laaw.py next` to see the exact next action after approval.
