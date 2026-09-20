---
name: implement-task
description: The only skill that modifies project files. Works a leaf task's Steps (or walks a super-task's children in ID order), checks steps off, runs Validations, fills Context updates, and moves status per the single-writer table. Ends by asking for implementation approval. Use when route hands off an in-progress task or an approved plan.
---

# Skill: implement-task

Implement-task does the work. It is the only skill that edits project code, and the only writer of
`in-progress`, `impl-review`, and subtask `done`.

Status rows live by level (workflow.md §2): a root task's row is in `.ai/tasks/index.md`; a
subtask's row is in its parent's `task.md` `Subtasks:` table. Flip the right one, always.

## Preconditions

- The task is `draft` with the human's current message approving its plan, or already
  `in-progress`. Otherwise stop and let route re-decide.

## Leaf task (has Steps)

1. Read `.ai/workflow/workflow.md` (once per session), the task file, and every `.ai/context/`
   file named in its `Context:` section — fresh, this turn.
2. Set the row to `in-progress` in `.ai/tasks/index.md`. This records the plan approval; do it
   before touching any project file.
3. Work the Steps in order. Check each step off (`- [x]`) in the task file as it completes.
   - **Deviation** (a step is wrong or impossible): stop, tell the human what and why, and get a
     decision. Record the decision in `Notes`; adjust the step only with that decision.
   - **Blocker**: add a Notes line, keep status `in-progress`, report to the human. Never invent a
     status.
4. Run every Validation. Record each result (pass/fail + output summary) in `Notes`. Fix failures
   and re-run until all pass or the human decides otherwise.
5. Fill `Context updates` with the exact `.ai/context/` edits this task makes (or confirm `none`).
6. Set the row to `impl-review`. Show a diff summary of project changes plus validation results,
   then ask: "Approve implementation of t{N}?" and stop.
7. On rejection: set the row back to `in-progress`, fix the work, re-run validations, re-ask.

## Super-task (has Subtasks)

1. Read the parent's `task.md`; list children in ID order from its `Subtasks:` table. Child files
   live in the same folder, named by their own IDs (`t{N}.1_{slug}.md`, …).
2. Walk children lowest ID first. For each:
   - Row already `impl-review` → ask "Approve implementation of t{N}.{k}?" (unless the human's
     current message already approves it). On approval set the row to `done` in the parent's table
     and continue.
   - Otherwise set its row to `in-progress` in the parent's table and work it exactly like a leaf
     task (steps 1–6 above, with the child's own file — but the status row is in the parent's
     table, not the index). On approval set the row to `done` and continue to the next child.
3. When every child row is `done`:
   - Run the **parent's** Validations; record results in the parent's `Notes`.
   - Fill the parent's `Context updates` as the aggregate of what the children reported.
   - Leave the parent at `in-progress` (its index row), report "all subtasks done, ready for
     context pass", and stop. Route hands the parent to propagate-context (workflow.md §7).

## Rules

- Never set `ctx-review` or root-level `done` — those belong to propagate-context.
- Never commit project code; commits of `.ai/context/` belong to propagate-context.
- One task (or one subtask) at a time; finish the current gate before starting anything else.
