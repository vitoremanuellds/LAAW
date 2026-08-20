---
name: workflow-constitution
description: Use this skill when creating or updating a project's constitution — mission.md, techstack.md, or roadmap.md under .ai/constitution/. Trigger this whenever the user wants to define what a project is, why it exists, its tech stack, or its phase roadmap for the first time, or wants to revise any of these. This is the first workflow operation on a new project — if .ai/constitution/ is empty or missing, start here before phase or task planning. Do not use for phase-level or task-level planning; see workflow-phase and workflow-task for those.
---

# Skill: workflow.constitution

Operation for the **Constitution Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

Creating or updating `mission.md`, `techstack.md`, or `roadmap.md`.

## Inputs

- User-provided project information (interview, existing docs, stated
  goals).
- Existing constitution files, if updating.

## Procedure

Steps 1–5 require no prior approval — draft the full constitution
before stopping for anything. Only step 6 is gated.

1. Read existing constitution files if present — do not overwrite blind.
2. Ask the user for anything missing that's required to write mission,
   tech stack, or roadmap. Do not invent goals or constraints the user
   hasn't stated or clearly implied.
3. Write `mission.md`: what/why/who/goals/boundaries. Keep it stable —
   this file should rarely need to change.
4. Write `techstack.md`: languages, frameworks, runtime, infra,
   constraints. Describe the foundation, not per-task implementation
   choices.
5. Write `roadmap.md` — ordered phases, one-line description each, and
   a **Status** column (`planned` for all of them initially — this
   file doubles as the phase index; see
   [../../workflow.md §11](../../workflow.md#11-status-vocabulary-indexes-not-a-state-file)).
   No separate per-phase roadmap files — phase detail lives in each
   phase's own `context.md`/`phase.md` once planned, not here.
6. Commit the draft (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)). Stop.
   Constitution review is a gate — see [../../../policy.md](../../../policy.md)
   for who approves it. Do not proceed to phase planning yourself
   unless authorized.

## Output

`constitution/mission.md`, `constitution/techstack.md`,
`constitution/roadmap.md`.
