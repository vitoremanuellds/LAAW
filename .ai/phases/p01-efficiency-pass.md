# P01 — Efficiency pass

Roadmap entry: `.ai/constitution/roadmap.md`.

## Context

This repo mounts itself as `.ai/workflow/` (a self-referential
submodule pinned to a prior commit — see `mission.md`) and now uses
its own methodology to plan its own development. The motivating goal,
from the user directly: reduce token/context overhead per skill
invocation, reduce agent mistakes/retries, and make the bootstrap
process and artifact templates more specific with less waste. See
`.ai/constitution/mission.md`'s Goals section.

`templates/` holds seven files, copied into a consuming project's
`.ai/` on first bootstrap by whichever skill owns that step:

| Template | Copied to | Copying skill(s) |
|---|---|---|
| `info-template.md` | `.ai/info.md` | `create-constitution-full` |
| `medium-info-template.md` | `.ai/info.md` | `create-constitution-medium` |
| `lite-project-template.md` | `.ai/project.md` | `workflow-lite` |
| `minimal-tasks-template.md` | `.ai/tasks.md` | `workflow-minimal` |
| `decisions-template.md` | `.ai/decisions/decisions.md` | `create-constitution-full`, `create-constitution-medium` |
| `context-template.md` | `.ai/context/context.md` | `create-constitution-full`, `create-constitution-medium` |
| `adr-template.md` | `.ai/decisions/adr{NN}-{name}.md` | referenced from `workflow.md §7` / `workflow-medium.md §7`, and from `implement-task-full` / `implement-task-medium` when an implementation-time ADR is written |

Research this session (full read of all seven templates and every
skill/doc that references them) found: five templates
(`info-template.md`, `medium-info-template.md`,
`lite-project-template.md`, `minimal-tasks-template.md`,
`decisions-template.md`) open with an agent-facing "Copy this to
`.ai/X` in your project and edit..." paragraph, aimed at whichever
skill performs the bootstrap copy. Two (`context-template.md`,
`adr-template.md`) already contain no such prose — pure artifact
content from line 1.

Every skill that actually performs a copy already independently
states the destination path and "copy ... there unedited" instruction
— confirmed by direct reading of `create-constitution-full/SKILL.md`
(lines 38–47), `create-constitution-medium/SKILL.md` (lines 39–49),
`workflow-lite/SKILL.md` (lines 46–51), and
`workflow-minimal/SKILL.md` (lines 53–58) — none of them depend on the
template's own meta text for anything. Because the copy step is
"unedited," that meta paragraph is carried verbatim into the live
project file — e.g. after bootstrap, `.ai/info.md` literally contains
"Copy this to `.ai/info.md` in your project and edit," which is
already false/confusing the moment it's read back, and it's read back
on every gate check for the life of the project (`workflow.md §2`).

`decisions-template.md`'s opening paragraph is a blend: "Copy this to
`.ai/decisions/decisions.md` in your project." (pure bootstrap
meta) followed by "One row per ADR. Check here before writing a new
one — a related decision may already exist (see
`.ai/workflow/workflow.md §7`)." (genuine, ongoing usage guidance for
whoever adds an ADR row later — not a bootstrap instruction, belongs
in the live artifact).

README.md references these templates in two places (bootstrap
walkthrough, repo-structure tables/tree) but only describes *that*
each is copied to a destination — it doesn't embed or depend on any
template's internal meta prose, so it needs no change for this phase.

## Requirements

1. No template under `templates/` contains agent-facing bootstrap
   instructions ("copy this to X," "edit this," which skill's rules
   apply) — only real artifact content (headings, structural
   skeleton, placeholders, and genuine usage guidance meant to live in
   the final artifact).
2. Every skill that copies a template remains fully self-sufficient
   for destination path and "copy unedited" behavior without relying
   on the template's own text — true today; must stay true after the
   edit (no skill currently needs a change to satisfy this, per the
   research above, but that gets re-verified as part of the task, not
   assumed).
3. `decisions-template.md` keeps its genuine usage-guidance sentence
   ("One row per ADR. Check here before writing a new one...") —
   only its "copy this to X" sentence is removed.
4. No other doc (`README.md`, `workflow.md`, `workflow-medium.md`, any
   `skills/*/SKILL.md`) is left referencing or depending on text this
   phase removes.
5. `context-template.md` and `adr-template.md` are left untouched —
   already clean, no meta prose to strip.

## Plan

1. Strip the "Copy this to `.ai/X` in your project and edit..."
   paragraph entirely from: `templates/info-template.md`,
   `templates/medium-info-template.md`,
   `templates/lite-project-template.md`,
   `templates/minimal-tasks-template.md`.
2. In `templates/decisions-template.md`, remove only the "Copy this
   to `.ai/decisions/decisions.md` in your project." sentence; keep
   the rest of that paragraph as the live artifact's opening
   guidance.
3. Re-verify (not re-derive from scratch) that
   `create-constitution-full/SKILL.md`,
   `create-constitution-medium/SKILL.md`, `workflow-lite/SKILL.md`,
   and `workflow-minimal/SKILL.md` still fully specify destination +
   "unedited" independent of the now-removed template text — no edit
   expected, but confirm by reading each again after the template
   edits land.
4. Sweep `README.md`, `workflow.md`, `workflow-medium.md` for any
   reference to the removed text — none expected (verified this
   session), confirm again post-edit.

This is small enough to be a single task, not several — see Tasks
below.

## Validations

- `grep -n "Copy this to" templates/*.md` returns zero matches after
  the edit.
- Each of the five edited templates, read start-to-finish, reads as
  pure artifact content: heading, then immediately real structure —
  no orphaned blank paragraph where the meta text used to be.
- `git diff --stat` for the task's commit touches only the five
  `templates/*.md` files listed above — nothing under `skills/` or
  `README.md`/`workflow.md`/`workflow-medium.md`, unless step 3/4
  above actually finds a dependency (in which case that finding gets
  reported, not silently patched around).
- `context-template.md` and `adr-template.md` are byte-identical to
  their pre-phase state (untouched).

## Tasks

| ID | Title | Purpose | Depends on | Status |
|---|---|---|---|---|
| P01-T01 | Strip bootstrap prose from templates | Remove agent-facing "copy this to X" paragraphs from the 5 templates that carry them; keep decisions-template.md's usage guidance; re-confirm no skill/doc depends on the removed text | — | complete |
