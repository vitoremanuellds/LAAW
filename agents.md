# Agent Contracts

Referenced from [workflow.md §11](workflow.md#11-agents). An agent never
determines its own authority — it operates strictly within the contract
below, and gate authority comes from [policy.md](policy.md).

## Constitution Agent

**Can:** read user-provided project information; create/modify
constitution artifacts; ask for clarification.

**Must:** write an ADR — and add its entry to
[decisions/index.md](decisions/index.md) — for project-level decisions,
including any produced by a project-level deviation (see
[deviations.md §Project-Level](deviations.md#project-level-deviation)).

**Cannot:** modify project code; invent requirements unsupported by the
project.

## Phase Planning Agent

**Can:** read constitution; read relevant project context; create phase
context, requirements, plan, validations.

**Must:** write an ADR — and add its entry to
[decisions/index.md](decisions/index.md) — for phase-level architectural
decisions, including any produced by a phase-level deviation (see
[deviations.md §Phase-Level](deviations.md#phase-level-deviation)).

**Cannot:** implement project code.

## Task Planning Agent

**Can:** read phase artifacts; read relevant project context; inspect
relevant project files; create task context and implementation plans.

**Must:** create or update `tasks/index.md` in the phase's `tasks/`
folder whenever a task is added — id, title, one-line purpose,
dependencies. See [workflow-task](skills/workflow-task/SKILL.md) for
the format.

**Cannot:** implement project code; write an ADR. If an architectural
decision surfaces during task planning, raise a phase-level deviation
instead (see [deviations.md](deviations.md)) — it isn't this agent's
scope to decide.

## Implementation Agent

**Can:** read the assigned task and referenced context; inspect relevant
project files; modify project files; execute required tools; update task
status.

**Must:**
- Update `project-context/structure.md` when a task creates, deletes,
  or moves a file or directory — before the task is handed to
  validation.
- Update the task's entry in the phase's `tasks/index.md` when updating
  task status.
- Write an ADR — and add its entry to
  [decisions/index.md](decisions/index.md) — when making an
  architectural decision during implementation. Check
  `decisions/index.md` first; a related decision may already exist.

**Cannot:** silently change approved requirements or the phase plan.

Skill: [workflow-implementation](skills/workflow-implementation/SKILL.md)

## Validation Agent

**Can:** read requirements and implementation plans; inspect project
files; execute validation commands; report failures.

**Should not:** modify implementation merely to make validation pass. If
validation requires implementation changes, return to the implementation
loop (see [lifecycle.md](lifecycle.md)).

## Context Agent

**Can:** inspect completed work; identify reusable knowledge; update
phase context; reconcile project context at phase completion.

**Should not:** copy task history into project context; duplicate
information already represented elsewhere; record internal reasoning.

## Review Agent

**Can:** inspect requirements, plan, implementation, changes, tests,
context, and relevant ADRs; identify scope violations, requirement
mismatches, unnecessary complexity, architectural inconsistencies,
missing validation, context inconsistencies, and undocumented decisions
(an architectural choice with no corresponding ADR).

**Should not:** silently fix problems, or write the missing ADR itself —
flag it back to the agent whose scope produced the decision (Constitution,
Phase Planning, or Implementation — see their contracts above), unless
its policy entry in [policy.md](policy.md) explicitly grants
implementation authority.
