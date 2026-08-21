---
name: workflow-context
description: Use this skill to evaluate and propagate reusable knowledge into context files after a task or phase completes — updating phase context.md at task completion, or project-context files at phase completion. Also finalizes status, marking a task complete in tasks/index.md or a phase complete in roadmap.md — but only once its completion-review gate (task-completion-review or phase-completion-review) has already been approved via workflow-review; this skill finalizes an approved review, it doesn't perform one. Trigger this whenever the user wants to determine whether something learned during a task or phase should be persisted for future tasks, or wants to reconcile project-context/*.md after a phase finishes. Do not use this to record task history, temporary implementation details, or internal reasoning — only persistent, reusable facts propagate.
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
3. If yes, update the phase's `context.md` with the persistent fact
   only (not the task's history or reasoning).
4. Set the task's Status to `complete` in `tasks/index.md` — this is
   the actual "task complete" marker; nothing else needs updating.

## workflow.context.phase — reconciling during a phase

Run periodically or when a task's context-agent step flags something
phase-wide. Ensure `phases/p{NN}-.../context.md` still accurately
describes shared architecture, constraints, and task relationships as
the phase progresses.

## workflow.context.project — on phase completion

**Precondition:** the phase's Status must already be `reviewing` with
an approved `phase-completion-review`, and all tasks in the phase
already `complete` — same principle as the task-level precondition
above.

1. Read the finished phase's `context.md`.
2. Ask: does this remain relevant *beyond this phase*? Only
   sufficiently general, persistent knowledge qualifies.
3. If yes, update `project-context/context.md` or the relevant
   `project-context/modules/*.md`.
4. Set the phase's Status to `complete` in
   `../../../constitution/roadmap.md` — this is the actual "phase complete"
   marker.
5. Commit (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)).

## Never propagate

Task history, temporary implementation details, information already
recorded elsewhere, internal reasoning, progress reports. See
[../../workflow.md §9](../../workflow.md#9-context-propagation).

## Output

Updated `context.md` at the appropriate level only — task, phase, or
project. The relevant Status field (`tasks/index.md` or `roadmap.md`)
set to complete. Do not write to more than one context level per
invocation unless the fact genuinely applies at both.
