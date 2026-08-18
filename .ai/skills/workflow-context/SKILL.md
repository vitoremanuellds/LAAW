---
name: workflow-context
description: Use this skill to evaluate and propagate reusable knowledge into context files after a task or phase completes — updating phase context.md at task completion, or project-context files at phase completion. Trigger this whenever the user wants to determine whether something learned during a task or phase should be persisted for future tasks, or wants to reconcile project-context/*.md after a phase finishes. Do not use this to record task history, temporary implementation details, or internal reasoning — only persistent, reusable facts propagate.
---

# Skill: workflow.context

Operation for the **Context Agent**. Contract:
[../../agents.md#context-agent](../../agents.md#context-agent). Three
sub-operations — use whichever matches the trigger.

## workflow.context.task — on task completion

1. Inspect what the task actually produced.
2. Ask: does anything discovered here matter to *other tasks in this
   phase*? If not, stop — not every task needs this step.
3. If yes, update the phase's `context.md` with the persistent fact
   only (not the task's history or reasoning).

## workflow.context.phase — reconciling during a phase

Run periodically or when a task's context-agent step flags something
phase-wide. Ensure `phases/p{NN}-.../context.md` still accurately
describes shared architecture, constraints, and task relationships as
the phase progresses.

## workflow.context.project — on phase completion

1. Read the finished phase's `context.md`.
2. Ask: does this remain relevant *beyond this phase*? Only sufficiently
   general, persistent knowledge qualifies.
3. If yes, update `project-context/context.md` or the relevant
   `project-context/modules/*.md`.

## Never propagate

Task history, temporary implementation details, information already
recorded elsewhere, internal reasoning, progress reports. See
[../../workflow.md §6](../../workflow.md#6-context-propagation).

## Output

Updated `context.md` at the appropriate level only — task, phase, or
project. Do not write to more than one level per invocation unless the
fact genuinely applies at both.
