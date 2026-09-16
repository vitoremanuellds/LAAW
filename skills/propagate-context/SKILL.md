---
name: propagate-context
description: Propagate reusable knowledge into context files after a task
  completes, and to finalize status (mark done in tasks.md) — but only
  after its task-completion-review gate is already approved via
  review-work. Not for task history, temporary implementation details,
  or internal reasoning.
---

# Skill: propagate-context

This skill performs the **context** operation, propagation half — see
also `build-context` for the survey half
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from). Single
sub-operation below — use it after a task's completion-review passes.

- **Can:** propagate reusable knowledge to `context/`; update
  `context.md`'s index table; set task status to `done`.
- **Must:** verify the `task-completion-review` gate was approved
  before marking done; never write to `context/` without approval.
- **Cannot:** copy task history; duplicate info; record reasoning.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for context propagation.

**All `.ai/`-artifact paths below are relative to the project root,
not to this skill file — write the full `.ai/...` path.** Status
values you set here (`done`) are from a closed enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)
for the full list; never invent one not on it.

## propagate-context.task — on task completion

**Precondition:** the task's Status must already be `in-progress` with
an approved `task-completion-review` (see
[review-work](.ai/workflow/skills/review-work/SKILL.md)) — this operation
finalizes an already-approved review, it doesn't substitute for one.
If Status isn't `in-progress` with approval confirmed, that gate hasn't
passed yet; don't mark done regardless of how the task looks.

1. Inspect what the task actually produced.
2. Ask: does anything discovered here matter *beyond this task itself*?
   If not, skip to step 3. If yes, write directly to `context/` (new
   or existing `c-{ID}-{name}.md` file, plus its row in
   `context.md`'s table), scaffolding `context/` first per
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)
   if it doesn't exist yet.
3. Set the task's Status to `done` in `.ai/tasks/tasks.md`.
4. Commit — stage the updated `context/*.md` files and `context.md`'s
   table, plus the updated Status row; the message should say which
   task completed. Stop for `task-review` gate (if the project uses it
   for propagation).
5. Ask whether a related follow-up task should be defined now — a
   plain question, not a gate.

## Status enum

`not-started` · `planned` · `in-progress` · `done` (+`blocked`).

## Output

Updated `context/*.md` files, `context.md`'s index table, updated
Status row in `tasks.md`.
