---
name: propagate-context
description: Propagate reusable knowledge into context files after a task or phase completes, and to finalize status (mark complete in the phase file's task table, tasks.md for an orphan task, or phases.md for a phase) — but only after its completion-review gate is already approved via review-work. Not for task history, temporary implementation details, or internal reasoning.
---

# Skill: propagate-context

This skill performs the **context** operation, propagation half — see
also `build-context` for the survey half
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from). Three
sub-operations below — use whichever matches the trigger.

- **Can:** propagate reusable knowledge to a phase file's Context or
  `context/` (or directly to `context/` for an orphan task — see
  `propagate-context.task` below); mark rows complete in the phase
  file, `tasks.md`, or `phases.md`.
- **Must:** verify the completion-review gate was actually approved
  before marking complete — finalizes, doesn't substitute.
- **Should not:** copy task history; duplicate info; record
  reasoning.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for context propagation.

**All `.ai/`-artifact paths below are relative to the project root,
not to this skill file — write the full `.ai/...` path.** Status
values you set here (`complete`) are one of exactly six in a closed
enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)
for the full list; never invent one not on it.

## propagate-context.task — on task completion

**Precondition:** the task's Status must already be `reviewing` with
an approved `task-completion-review` (see
[review-work](.ai/workflow/skills/review-work/SKILL.md)) — this operation
finalizes an already-approved review, it doesn't substitute for one.
If Status isn't `reviewing` with approval confirmed, that gate hasn't
passed yet; don't mark complete regardless of how the task looks.

1. Inspect what the task actually produced.
2. **Phase-linked task:** ask does anything discovered here matter to
   *other tasks in this phase*? If not, skip to step 3 — not every
   task needs this. If yes, update the owning phase file's own Context
   section with the persistent fact (not the task's history or
   reasoning). **Never write to `.ai/context/` directly from this
   sub-operation for a phase-linked task, even if the fact looks like
   it matters beyond this one phase** — promotion to `.ai/context/`
   happens only once, in `propagate-context.project` below, which
   reviews everything the phase's Context section accumulated at once.
   Writing to `.ai/context/` mid-phase skips that review and is
   exactly the shortcut the hierarchy in
   [.ai/workflow/workflow.md §9](.ai/workflow/workflow.md#9-context-propagation)
   exists to prevent.
   **Orphan task:** ask does anything discovered here matter *beyond
   this task itself*? If not, skip to step 3. If yes, write directly to
   `.ai/context/` (new or existing file, plus its row in
   `context.md`'s table), scaffolding `.ai/context/` first per
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)
   if it doesn't exist yet — an orphan task has no owning phase's
   Context section to route through, and no later phase-completion
   checkpoint to defer batching to, so its own completion is the
   natural point to write directly.
3. Set the task's Status to `complete` — in its owning phase file's
   Tasks table if phase-linked, or `.ai/tasks/tasks.md` if orphan.
   This is the actual "task complete" marker.
4. Commit: stage the updated Status row (phase file's Tasks table or
   `tasks.md`), plus any Context update from step 2 (phase file's
   Context section, or `.ai/context/` files + `context.md`'s table for
   an orphan task); the message should say which task completed (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline));
   exclude any gitignored files — gitignored layers simply have nothing to
   commit, not a violation of commit discipline.
5. **Phase-linked:** ask whether the phase needs more tasks — does the
   phase file's Plan still look sufficient, or is there something to
   add before this unit of work is really closed? A plain question,
   not a gate — it sets no Status on its own. If the answer is yes,
   that's a normal `define-task` invocation next, same as any other.
   **Orphan:** ask whether a related follow-up task should be defined
   now — same non-gate question, no phase Plan to check against.

## propagate-context.phase — reconciling during a phase

Run periodically or when a task's context-agent step flags something
phase-wide. Ensure the phase file's own Context section still
accurately describes shared architecture, constraints, and task
relationships as the phase progresses. Applies only to a project that
uses phases at all — an orphan task's equivalent reconciliation, if
any, already happened directly in `propagate-context.task` above.

## propagate-context.project — on phase completion

**Precondition:** the phase's Status must already be `reviewing` with
an approved `phase-completion-review`, and all tasks in the phase
already `complete` — same principle as the task-level precondition
above.

1. Read the finished phase file's own Context section.
2. Ask: does this remain relevant *beyond this phase*? Only
   sufficiently general, persistent knowledge qualifies.
3. If yes, update the relevant file under `.ai/context/` (new or
   existing, scaffolding `.ai/context/` first per
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)
   if it doesn't exist yet), and update its row in
   `.ai/context/context.md`'s table (Description, Status, Relations)
   in the same step.
4. Set the phase's Status to `complete` in `.ai/phases/phases.md` —
   this is the actual "phase complete" marker.
5. Commit: stage `.ai/phases/phases.md`'s updated Status, and the
   `.ai/context/` file(s) touched in step 3 plus `context.md`'s table
   row; the message should say which phase completed (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline));
   exclude any gitignored files — gitignored layers simply have nothing to
   commit, not a violation of commit discipline.
6. Ask whether the project needs another phase, or is done for now — a
   plain question, not a gate. If the answer is yes, the normal next
   step is running `define-phase` directly for the new phase (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates),
   "Starting without a plan"), not re-deriving the whole mechanism
   here.

## Never propagate

Task history, temporary implementation details, information already
recorded elsewhere, internal reasoning, progress reports. See
[.ai/workflow/workflow.md §9](.ai/workflow/workflow.md#9-context-propagation).

## Output

Updated context at the appropriate level only —
`propagate-context.task` writes to the phase file's own Context
section for a phase-linked task, or directly to `.ai/context/` for an
orphan task; `propagate-context.project` writes only to `.ai/context/`
(plus its row in `.ai/context/context.md`'s table), once per finished
phase. The relevant Status set to `complete` in its owning phase
file's Tasks table, `.ai/tasks/tasks.md`, or `.ai/phases/phases.md`.
