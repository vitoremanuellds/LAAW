---
name: implement-task
description: The only skill that modifies project files. Works a leaf task's Steps (or walks a super-task's children in ID order), checks steps off, runs Validations, fills Context updates, and flips statuses via tasks.py set-status. Ends by asking for implementation approval. Use when route hands off an in-progress task or an approved plan.
---

# Skill: implement-task

Implement-task does the work. It is the only skill that edits project code, and the only skill
allowed to trigger the `in-progress`, `impl-review`, and subtask `done` transitions — always
via `python3 .ai/workflow/tools/tasks.py set-status <id> <status>` (from the project root).
Never hand-edit `state.json`; if the CLI refuses a flip, report the error instead of forcing it.

## Preconditions

- The task is `draft` with the human's current message approving its plan, or already
  `in-progress` (check with `tasks.py status <id>` — fresh, this turn). Otherwise stop and let
  route re-decide.

## Leaf task (has Steps)

1. Read `.ai/workflow/workflow.md` (once per session), the task file, and every `.ai/context/`
   file named in its `Context:` section — fresh, this turn.
2. `tasks.py set-status t{N} in-progress`. This records the plan approval; do it before
   touching any project file.
3. Work the Steps in order. Check each step off (`- [x]`) in the task file as it completes.
   - **Deviation** (a step is wrong or impossible): stop, tell the human what and why, and get a
     decision. Record the decision in `Notes`; adjust the step only with that decision.
   - **Blocker**: add a Notes line, keep status `in-progress`, report to the human. Never invent
     a status.
4. Run every Validation. Record each result (pass/fail + output summary) in `Notes`. Fix
   failures and re-run until all pass or the human decides otherwise.
5. Fill `Context updates` with the exact `.ai/context/` edits this task makes (or confirm `none`).
6. `tasks.py set-status t{N} impl-review`. Show a diff summary of project changes plus
   validation results, then ask: "Approve implementation of t{N}?" and stop.
7. On rejection: `set-status t{N} in-progress`, fix the work, re-run validations, re-ask.

## Super-task (has Subtasks)

1. Read the parent's `task.md`; get the children and their statuses with
   `tasks.py status t{N}` (or `board`). Child files live in the parent folder, named by their
   own IDs.
2. Walk children lowest ID first. For each:
   - Child already `impl-review` → ask "Approve implementation of t{N}.{k}?" (unless the
     human's current message already approves it). On approval: `set-status t{N}.{k} done`,
     continue.
   - Otherwise: `set-status t{N}.{k} in-progress` and work the child exactly like a leaf task
     (steps 1–6 above, using the child's own file and ID). On approval: `set-status t{N}.{k} done`,
     continue to the next child.
3. When every child is `done`:
   - Run the **parent's** Validations; record results in the parent's `Notes`.
   - Fill the parent's `Context updates` as the aggregate of what the children reported.
   - Leave the parent `in-progress`, report "all subtasks done, ready for context pass", and
     stop. Route hands the parent to propagate-context (workflow.md §7).

## Rules

- Never trigger `ctx-review` or root-level `done` — those belong to propagate-context.
- Never commit project code; commits of `.ai/context/` belong to propagate-context.
- One task (or one subtask) at a time; finish the current gate before starting anything else.
- Task files hold content only — status changes go through `tasks.py set-status`, never into
  the markdown.
