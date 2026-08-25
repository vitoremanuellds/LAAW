---
name: create-constitution-medium
description: Medium-profile skill to create or update a project's constitution (mission.md, techstack.md, roadmap.md-as-flat-task-index) under .ai/constitution/ — the first operation on a new medium-profile project; also bootstraps info.md, context/context.md, and decisions/decisions.md on first run. Not for the full profile (see create-constitution-full) or task planning (see define-task-medium).
---

# Skill: create-constitution-medium

Operation for the **Constitution Agent**. Contract:
[.ai/workflow/workflow-medium.md §10](.ai/workflow/workflow-medium.md#10-agent-contracts).

Read [.ai/workflow/workflow-medium.md](.ai/workflow/workflow-medium.md)
in full, same as every other medium-profile skill — do not skip it for
constitution work.

## When to use

Creating or updating `.ai/constitution/mission.md`, `techstack.md`, or
`roadmap.md` on a **medium-profile** project. On a brand-new project,
this is also what bootstraps `.ai/info.md`, `.ai/context/context.md`,
and `.ai/decisions/decisions.md`.

## Inputs

- User-provided project information (interview, existing docs, stated
  goals).
- Existing constitution files, if updating.
- [`.ai/workflow/templates/medium-info-template.md`](.ai/workflow/templates/medium-info-template.md),
  [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md), and
  [`.ai/workflow/templates/decisions-template.md`](.ai/workflow/templates/decisions-template.md) — only
  read/used if the destinations don't exist yet.

## Procedure

All paths below are `.ai/`-prefixed and relative to the project root —
not relative to this skill file. Steps 1–6 require no prior approval —
draft everything before stopping for anything. Only step 7 is gated.

1. Read existing constitution files if present — do not overwrite blind.
2. **First run only:** if `.ai/info.md` doesn't exist, copy
   [`.ai/workflow/templates/medium-info-template.md`](.ai/workflow/templates/medium-info-template.md)
   there unedited — its defaults (`mode: assisted`) are the safe
   starting point; the human adjusts it later, not you. If
   `.ai/context/context.md` doesn't exist, copy
   [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md)
   there unedited. If `.ai/decisions/decisions.md` doesn't exist, copy
   [`.ai/workflow/templates/decisions-template.md`](.ai/workflow/templates/decisions-template.md)
   there unedited. Never overwrite any of these if they already
   exist — a second constitution run (updating an existing project)
   skips this step entirely.
3. Ask the user for anything missing that's required to write mission,
   tech stack, or roadmap. Do not invent goals or constraints the user
   hasn't stated or clearly implied.
4. Write `.ai/constitution/mission.md`: what/why/who/goals/boundaries.
   Keep it stable — this file should rarely need to change.
5. Write `.ai/constitution/techstack.md`: languages, frameworks,
   runtime, infra, constraints. Describe the foundation, not per-task
   implementation choices.
6. Write `.ai/constitution/roadmap.md` — this is a **flat task index**
   at the medium profile, not a phase list: `| ID | Title | Purpose |
   Depends on | Status |`, one row per known task, Status
   `not-planned` for all of them initially (this file is the
   permanent record — see
   [.ai/workflow/workflow-medium.md §11](.ai/workflow/workflow-medium.md#11-status-the-fast-pointer-and-the-permanent-record)).
   No separate phase files at this profile — task detail lives in each
   task's own `.ai/tasks/t{NN}-{name}.md` once planned.
7. Commit the draft (see
   [.ai/workflow/workflow-medium.md §13](.ai/workflow/workflow-medium.md#13-commit-discipline)) —
   include `.ai/info.md`/`.ai/context/context.md`/
   `.ai/decisions/decisions.md` in this same commit if you just
   created them. Stop. Constitution review is a gate — see
   `.ai/info.md` (read fresh, not from memory) for who approves it.
   Do not proceed to task planning yourself unless authorized. **When
   approval comes back, that's a separate turn:** in `manual`/
   `assisted` mode, report the approval and explicitly ask whether to
   start task planning now, rather than starting it in the same
   response (see
   [.ai/workflow/workflow-medium.md §5](.ai/workflow/workflow-medium.md#5-lifecycle--gates)).

## Output

`.ai/constitution/mission.md`, `.ai/constitution/techstack.md`,
`.ai/constitution/roadmap.md` — always. `.ai/info.md`,
`.ai/context/context.md`, `.ai/decisions/decisions.md` — first run
only.
