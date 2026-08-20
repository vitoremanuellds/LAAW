---
name: workflow-constitution
description: Use this skill when creating or updating a project's constitution — mission.md, techstack.md, or roadmap.md under .ai/constitution/. Trigger this whenever the user wants to define what a project is, why it exists, its tech stack, or its phase roadmap for the first time, or wants to revise any of these. This is the first workflow operation on a new project — if .ai/constitution/ is empty or missing, start here before phase or task planning; it also bootstraps .ai/policy.md and .ai/decisions/index.md from their templates on first run. Do not use for phase-level or task-level planning; see workflow-phase and workflow-task for those.
---

# Skill: workflow.constitution

Operation for the **Constitution Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

Creating or updating `mission.md`, `techstack.md`, or `roadmap.md`. On
a brand-new project, this is also what bootstraps `policy.md` and
`decisions/index.md`.

## Inputs

- User-provided project information (interview, existing docs, stated
  goals).
- Existing constitution files, if updating.
- [`../../templates/policy-template.md`](../../templates/policy-template.md) and
  [`../../templates/decisions-index-template.md`](../../templates/decisions-index-template.md) —
  only read/used if the destinations don't exist yet.

## Procedure

Steps 1–6 require no prior approval — draft everything before stopping
for anything. Only step 7 is gated.

1. Read existing constitution files if present — do not overwrite blind.
2. **First run only:** if `../../policy.md` doesn't exist, copy
   [`../../templates/policy-template.md`](../../templates/policy-template.md) there unedited —
   its defaults (`mode: assisted`, gates mostly `human`) are the safe
   starting point; the human adjusts it later, not you. If
   `../../decisions/index.md` doesn't exist, copy
   [`../../templates/decisions-index-template.md`](../../templates/decisions-index-template.md)
   there unedited. Never overwrite either if it already exists — a
   second constitution run (updating an existing project) skips this
   step entirely.
3. Ask the user for anything missing that's required to write mission,
   tech stack, or roadmap. Do not invent goals or constraints the user
   hasn't stated or clearly implied.
4. Write `mission.md`: what/why/who/goals/boundaries. Keep it stable —
   this file should rarely need to change.
5. Write `techstack.md`: languages, frameworks, runtime, infra,
   constraints. Describe the foundation, not per-task implementation
   choices.
6. Write `roadmap.md` — ordered phases, one-line description each, and
   a **Status** column (`planned` for all of them initially — this
   file doubles as the phase index; see
   [../../workflow.md §11](../../workflow.md#11-status-vocabulary-indexes-not-a-state-file)).
   No separate per-phase roadmap files — phase detail lives in each
   phase's own `context.md`/`phase.md` once planned, not here.
7. Commit the draft (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)) —
   include `policy.md`/`decisions/index.md` in this same commit if you
   just created them. Stop. Constitution review is a gate — see
   [../../../policy.md](../../../policy.md) for who approves it (it
   exists by now regardless of whether this was a first run). Do not
   proceed to phase planning yourself unless authorized.

## Output

`constitution/mission.md`, `constitution/techstack.md`,
`constitution/roadmap.md` — always. `policy.md`, `decisions/index.md` —
first run only.
