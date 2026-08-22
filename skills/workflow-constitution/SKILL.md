---
name: workflow-constitution
description: Use this skill when creating or updating a project's constitution — mission.md, techstack.md, or roadmap.md under .ai/constitution/. Trigger this whenever the user wants to define what a project is, why it exists, its tech stack, or its phase roadmap for the first time, or wants to revise any of these. This is the first workflow operation on a new project — if .ai/constitution/ is empty or missing, start here before phase or task planning; it also bootstraps .ai/info.md, .ai/context/context.md, and .ai/decisions/decisions.md from their templates on first run. Do not use for phase-level or task-level planning; see workflow-phase and workflow-task for those.
---

# Skill: workflow.constitution

Operation for the **Constitution Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

Creating or updating `mission.md`, `techstack.md`, or `roadmap.md`. On
a brand-new project, this is also what bootstraps `info.md`,
`context/context.md`, and `decisions/decisions.md`.

## Inputs

- User-provided project information (interview, existing docs, stated
  goals).
- Existing constitution files, if updating.
- [`../../templates/info-template.md`](../../templates/info-template.md),
  [`../../templates/context-template.md`](../../templates/context-template.md), and
  [`../../templates/decisions-template.md`](../../templates/decisions-template.md) — only
  read/used if the destinations don't exist yet.

## Procedure

Steps 1–6 require no prior approval — draft everything before stopping
for anything. Only step 7 is gated.

1. Read existing constitution files if present — do not overwrite blind.
2. **First run only:** if `../../info.md` doesn't exist, copy
   [`../../templates/info-template.md`](../../templates/info-template.md) there unedited — its
   defaults (`mode: assisted`) are the safe starting point; the human
   adjusts it later, not you. If `../../context/context.md` doesn't
   exist, copy [`../../templates/context-template.md`](../../templates/context-template.md)
   there unedited. If `../../decisions/decisions.md` doesn't exist,
   copy [`../../templates/decisions-template.md`](../../templates/decisions-template.md) there
   unedited. Never overwrite any of these if they already exist — a
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
   a **Status** column (`not-planned` for all of them initially — this
   file is the phase-level permanent record; see
   [../../workflow.md §11](../../workflow.md#11-status-the-fast-pointer-and-the-permanent-record)).
   No separate per-phase files here — phase detail lives in each
   phase's own `phases/p{NN}-{name}.md` once planned.
7. Commit the draft (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)) —
   include `info.md`/`context/context.md`/`decisions/decisions.md` in
   this same commit if you just created them. Stop. Constitution
   review is a gate — see [../../../info.md](../../../info.md) (read
   fresh, not from memory) for who approves it. Do not proceed to
   phase planning yourself unless authorized. **When approval comes
   back, that's a separate turn:** in `manual`/`assisted` mode, report
   the approval and explicitly ask whether to start phase planning
   now, rather than starting it in the same response (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)).

## Output

`constitution/mission.md`, `constitution/techstack.md`,
`constitution/roadmap.md` — always. `info.md`, `context/context.md`,
`decisions/decisions.md` — first run only.
