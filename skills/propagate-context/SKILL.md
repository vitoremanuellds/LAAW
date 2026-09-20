---
name: propagate-context
description: The context pass and the only path to done. Applies a task's Context updates to .ai/context/ (plus subtask files for super-tasks), flips to ctx-review via tasks.py set-status, asks for context approval, then flips to done and commits .ai/context/. Use when route hands off an impl-review task with approved implementation, or a super-task whose subtasks are all done.
---

# Skill: propagate-context

Propagate-context closes the loop: it turns a finished task's `Context updates` into real
context files, gets approval, and marks the task `done`. It is the only skill allowed to
trigger `ctx-review` and `done` — always via `tasks.py set-status <id> <status>` — and the
only skill that commits `.ai/context/`.

## Preconditions (check fresh with `tasks.py status <id>`)

- A task with Steps: `impl-review` and the human's current message approves its implementation.
- A super-task: `in-progress` and every subtask `done`.
- If neither holds, stop and let route re-decide.

## Steps

1. Read `.ai/workflow/workflow.md` (once per session), the task file, **and for a super-task
   every child file in the parent folder** (named by their own IDs), plus
   `.ai/context/index.md` and every context file you are about to edit — fresh, this turn.
2. Collect `Context updates` from the task file; for a super-task, merge in each subtask's
   `Context updates` (the parent's aggregate should already reflect them — flag any mismatch to
   the human instead of guessing).
3. Apply the exact edits:
   - Edit topic files in place; create a new topic file only when the update names one that does
     not exist yet.
   - Keep context per workflow.md §6: small, factual, present tense; split a file past ~100
     lines.
   - Update `.ai/context/index.md` rows for any added/removed files.
4. `tasks.py set-status t{N} ctx-review`. Show the exact context diff (per file), then ask:
   "Approve context changes for t{N}?" and stop.
5. On rejection: revise the edits, keep `ctx-review`, re-ask.
6. On approval (human's current message): `set-status t{N} done`. If the project is a git repo:
   `git add .ai/context && git commit -m "t{N}: context"`. Report the task complete and stop.

## Rules

- Never edit project code here — implementation was already approved.
- Never commit anything outside `.ai/context/`.
- Never hand-edit `state.json`; if the CLI refuses a flip, report the error instead of forcing it.
- A super-task's subtasks stay `done` in state; only the parent moves to `done`.
