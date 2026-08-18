# Agent Contracts

Referenced from [workflow.md §11](workflow.md#11-agents). An agent never
determines its own authority — it operates strictly within the contract
below, and gate authority comes from [policy.md](policy.md).

## Constitution Agent

**Can:** read user-provided project information; create/modify
constitution artifacts; ask for clarification.

**Cannot:** modify project code; invent requirements unsupported by the
project.

## Phase Planning Agent

**Can:** read constitution; read relevant project context; create phase
context, requirements, plan, validations.

**Cannot:** implement project code.

## Task Planning Agent

**Can:** read phase artifacts; read relevant project context; inspect
relevant project files; create task context and implementation plans.

**Cannot:** implement project code.

## Implementation Agent

**Can:** read the assigned task and referenced context; inspect relevant
project files; modify project files; execute required tools; update task
status.

**Must:** update `project-context/structure.md` when a task creates,
deletes, or moves a file or directory — before the task is handed to
validation.

**Cannot:** silently change approved requirements or the phase plan;
make architectural decisions without documenting them (write an ADR or
raise a deviation — see [deviations.md](deviations.md)).

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
missing validation, context inconsistencies.

**Should not:** silently fix problems unless its policy entry in
[policy.md](policy.md) explicitly grants implementation authority.
