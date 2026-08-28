---
name: create-constitution-full
description: Full-profile skill to create or update a project's constitution (mission.md, techstack.md, roadmap.md) under .ai/constitution/ — the first operation on a new project; also bootstraps info.md, context/context.md, and decisions/decisions.md on first run. Not for phase or task planning — see define-phase/define-task-full.
---

# Skill: create-constitution-full

This skill performs the **constitution** operation
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from).

- **Can:** constitution artifacts, ask clarification.
- **Must:** ADR for project decisions; first run, bootstrap
  `info.md`/`context.md`/`decisions.md` unedited, never overwrite
  existing.
- **Cannot:** touch code; invent unsupported requirements.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for constitution work.

## When to use

Creating or updating `.ai/constitution/mission.md`, `techstack.md`, or
`roadmap.md`. On a brand-new project, this is also what bootstraps
`.ai/info.md`, `.ai/context/context.md`, and
`.ai/decisions/decisions.md`.

## Inputs

- User-provided project information (interview, existing docs, stated
  goals).
- Existing constitution files, if updating.
- [`.ai/workflow/templates/info-template.md`](.ai/workflow/templates/info-template.md),
  [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md), and
  [`.ai/workflow/templates/decisions-template.md`](.ai/workflow/templates/decisions-template.md) — only
  read/used if the destinations don't exist yet.

## Procedure

All paths below are `.ai/`-prefixed and relative to the project root —
not relative to this skill file. Steps 1–8 require no prior approval —
draft everything before stopping for anything. Only step 9 is gated.

1. Read existing constitution files if present — do not overwrite blind.
2. **First run only:** if `.ai/info.md` doesn't exist, copy
   [`.ai/workflow/templates/info-template.md`](.ai/workflow/templates/info-template.md) there unedited — its
   defaults (`mode: assisted`) are the safe starting point; the human
   adjusts it later, not you. If `.ai/context/context.md` doesn't
   exist, copy [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md)
   there unedited. If `.ai/decisions/decisions.md` doesn't exist,
   copy [`.ai/workflow/templates/decisions-template.md`](.ai/workflow/templates/decisions-template.md) there
   unedited. Never overwrite any of these if they already exist — a
   second constitution run (updating an existing project) skips this
   step entirely.
3. Ask the user for anything missing that's required to write mission,
   tech stack, or roadmap. Do not invent goals or constraints the user
   hasn't stated or clearly implied.
4. Write `.ai/constitution/mission.md`: what/why/who/goals/boundaries.
   Keep it stable — this file should rarely need to change.
5. Write `.ai/constitution/techstack.md`: languages, frameworks,
   runtime, infra, constraints. Describe the foundation, not per-task
   implementation choices.
6. Write `.ai/constitution/roadmap.md` as a table: `| ID | Title |
   Depends on | Status |`, one row per phase, Status `not-planned` for
   all of them initially (this file is the phase-level permanent
   record; see
   [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)).
   Leave Depends-on empty unless a phase is already known to require
   another one first — `define-phase` fills in or adjusts this as
   phases actually get planned, the same way task-level dependencies
   get filled in later (§11). Each phase should be feature-sized,
   semantically-linked work, not a task list —
   [.ai/workflow/workflow.md §4](.ai/workflow/workflow.md#4-artifact-hierarchy--context-rule)
   defines what counts as a phase. No separate per-phase files here —
   phase detail lives in each phase's own
   `.ai/phases/p{NN}-{name}.md` once planned. **Layout: any
   explanatory/intro prose about the roadmap goes before the table,
   never after — the table is the file's last element.** This applies
   equally when appending a single new phase row to an
   already-existing `roadmap.md`, not just the initial full write —
   merge any new context into the existing intro paragraph rather than
   tacking a note on after the table. **When appending one new phase
   row to an already-existing `roadmap.md` (not the initial full
   write, where every phase gets stubbed together during the same
   interview as mission/techstack) — that row is title-only; the
   phase's actual Context/Requirements/Plan/Validations don't exist
   yet and won't until `define-phase` drafts them, later, possibly in
   a different session. Tell the user this explicitly, and ask if they
   want to share any context/detail for the new phase now — a session
   that ends before `define-phase` runs may lose anything that was
   only ever stated in conversation, not yet captured in a file.**
7. Ask the user whether there's anything else to add to this draft
   (mission, techstack, or roadmap) before requesting review — batch
   it in now rather than triggering a second review cycle later for
   something that could have been included in this one.
8. If a project-level decision was made while drafting mission/
   techstack/roadmap that future work needs to know about, this is
   yours to document — check `.ai/decisions/decisions.md` first; a
   related decision may already exist. If not, write the ADR from
   [.ai/workflow/templates/adr-template.md](.ai/workflow/templates/adr-template.md)
   into `.ai/decisions/adr{NN}-{name}.md` and add its index row in the
   same step.
9. Commit the draft: stage `.ai/constitution/mission.md`,
   `.ai/constitution/techstack.md`, and `.ai/constitution/roadmap.md`,
   plus `.ai/info.md`/`.ai/context/context.md`/
   `.ai/decisions/decisions.md` if you just created them or added an
   ADR row in step 8; the message should say what was drafted or
   updated, and whether this was a first-run bootstrap (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
   Stop. Constitution review is a gate — see
   `.ai/info.md` (read fresh, not from memory) for who approves it.
   Do not proceed to phase planning yourself unless authorized. **When
   approval comes back, that's a separate turn:** in `manual`/
   `assisted` mode, report the approval and explicitly ask whether to
   start phase planning now, rather than starting it in the same
   response (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).

## Output

`.ai/constitution/mission.md`, `.ai/constitution/techstack.md`,
`.ai/constitution/roadmap.md` — always. `.ai/info.md`,
`.ai/context/context.md`, `.ai/decisions/decisions.md` — first run
only. A new ADR and `.ai/decisions/decisions.md` row if a
project-level decision was made.
