---
name: workflow-context
description: Use this skill to evaluate and propagate reusable knowledge into context files after a task or phase completes — updating a phase's own Context section at task completion, or context/*.md files at phase completion. Also finalizes status, marking a task complete in its owning phase file's Tasks table, a phase complete in roadmap.md, and clearing the active pointer in info.md's Status section — but only once its completion-review gate (task-completion-review or phase-completion-review) has already been approved via workflow-review; this skill finalizes an approved review, it doesn't perform one. Trigger this whenever the user wants to determine whether something learned during a task or phase should be persisted for future tasks, or wants to reconcile context/*.md after a phase finishes. Do not use this to record task history, temporary implementation details, or internal reasoning — only persistent, reusable facts propagate.
---

# Skill: workflow.context

Operation for the **Context Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts). Three
sub-operations — use whichever matches the trigger.

## workflow.context.task — on task completion

**Precondition:** the task's Status must already be `reviewing` with
an approved `task-completion-review` (see
[workflow-review](../workflow-review/SKILL.md)) — this operation
finalizes an already-approved review, it doesn't substitute for one.
If Status isn't `reviewing` with approval confirmed, that gate hasn't
passed yet; don't mark complete regardless of how the task looks.

1. Inspect what the task actually produced.
2. Ask: does anything discovered here matter to *other tasks in this
   phase*? If not, skip to step 4 — not every task needs this.
3. If yes, update the phase file's own Context section with the
   persistent fact (not the task's history or reasoning). If the fact
   is general enough to matter beyond this one phase, put it under
   `context/` instead (new or existing file) — see the propagation
   rule in
   [../../workflow.md §9](../../workflow.md#9-context-propagation). If
   you touch `context/`, update its row (or add one) in
   [../../../context/context.md](../../../context/context.md)'s table
   in the same step.
4. Set the task's Status to `complete` in its owning phase file's
   Tasks table — this is the actual "task complete" marker. Clear it
   as the active task in `info.md`'s Status section (leave `Active
   phase` alone if the phase itself isn't done).

## workflow.context.phase — reconciling during a phase

Run periodically or when a task's context-agent step flags something
phase-wide. Ensure the phase file's own Context section still
accurately describes shared architecture, constraints, and task
relationships as the phase progresses.

## workflow.context.project — on phase completion

**Precondition:** the phase's Status must already be `reviewing` with
an approved `phase-completion-review`, and all tasks in the phase
already `complete` — same principle as the task-level precondition
above.

1. Read the finished phase file's own Context section.
2. Ask: does this remain relevant *beyond this phase*? Only
   sufficiently general, persistent knowledge qualifies.
3. If yes, update the relevant file under `context/` (new or
   existing), and update its row in `context/context.md`'s table
   (Description, Status, Relations) in the same step.
4. Set the phase's Status to `complete` in
   `../../constitution/roadmap.md` — this is the actual "phase
   complete" marker. Clear `info.md`'s Status section entirely (both
   `Active phase` and `Active task` go back to `—`) unless a next
   phase is already starting in the same breath.
5. Commit (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)).

## Never propagate

Task history, temporary implementation details, information already
recorded elsewhere, internal reasoning, progress reports. See
[../../workflow.md §9](../../workflow.md#9-context-propagation).

## Output

Updated context at the appropriate level only — a phase file's own
Context section, or a file under `context/` (plus its row in
`context/context.md`'s table). The relevant Status set to `complete`
in its owning phase file's Tasks table or `roadmap.md`, and `info.md`'s
Status section updated to match. Do not write to more than one context
level per invocation unless the fact genuinely applies at both.
