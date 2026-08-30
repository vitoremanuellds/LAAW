---
name: create-constitution
description: Create or update a project's constitution (mission.md, techstack.md) under .ai/constitution/ — an optional layer. Always bootstraps .ai/info.md on first run, regardless of whether constitution content is wanted, since info.md is gate-authority plumbing, not an optional layer. Not for phase or task planning — see define-phase/define-task. Not for scaffolding any other layer (context/decisions/phases/tasks/workbench) — each owns its own scaffold-on-first-use step, see reference/scaffold-on-first-use.md.
---

# Skill: create-constitution

This skill performs the **constitution** operation
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from).

- **Can:** constitution artifacts (mission, techstack), ask
  clarification.
- **Must:** ADR for project decisions; first run, bootstrap
  `info.md` unedited, never overwrite existing.
- **Cannot:** touch code; invent unsupported requirements; scaffold
  any layer other than constitution + `info.md` — that's each other
  layer's own owning skill, per
  [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md).

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for constitution work.

## When to use

Creating or updating `.ai/constitution/mission.md` or `techstack.md`.
On a brand-new project, this is also what bootstraps `.ai/info.md` —
the one piece of first-run scaffolding this skill owns unconditionally,
since gate authority isn't an optional layer the way constitution
content is. A project that never wants a constitution at all still
needs `info.md`; running this skill (directly, or via `bootstrap`) is
what creates it.

## Inputs

- User-provided project information (interview, existing docs, stated
  goals).
- Existing constitution files, if updating.
- [`.ai/workflow/templates/info-template.md`](.ai/workflow/templates/info-template.md) —
  only read/used if `.ai/info.md` doesn't exist yet.
- [`.ai/workflow/templates/decisions-template.md`](.ai/workflow/templates/decisions-template.md) —
  only read/used if this run writes the project's first-ever ADR and
  `.ai/decisions/` doesn't exist yet (see step 7).

## Procedure

All paths below are `.ai/`-prefixed and relative to the project root —
not relative to this skill file. Steps 1–7 require no prior approval —
draft everything before stopping for anything. Only step 8 is gated.

1. Read existing constitution files if present — do not overwrite blind.
2. **First run only:** if `.ai/info.md` doesn't exist, copy
   [`.ai/workflow/templates/info-template.md`](.ai/workflow/templates/info-template.md) there unedited — its
   defaults (`mode: assisted`) are the safe starting point; the human
   adjusts it later, not you. This is the only file this skill
   scaffolds unconditionally — every other layer (context, decisions,
   phases, tasks, workbench) is scaffolded by its own owning skill on
   first use, never here (see
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)).
   Never overwrite `info.md` if it already exists — a second
   constitution run (updating an existing project) skips this step
   entirely.
3. Ask the user for anything missing that's required to write mission
   or tech stack. Do not invent goals or constraints the user hasn't
   stated or clearly implied.
4. Write `.ai/constitution/mission.md`: what/why/who/goals/boundaries.
   Keep it stable — this file should rarely need to change.
5. Write `.ai/constitution/techstack.md`: languages, frameworks,
   runtime, infra, constraints. Describe the foundation, not per-task
   implementation choices.
6. Ask the user whether there's anything else to add to this draft
   (mission or techstack) before requesting review — batch it in now
   rather than triggering a second review cycle later for something
   that could have been included in this one.
7. If a project-level decision was made while drafting mission or
   techstack that future work needs to know about, this is yours to
   document — check `.ai/decisions/decisions.md` first; a related
   decision may already exist. If `.ai/decisions/` doesn't exist yet,
   scaffold it per
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)
   (copy [`.ai/workflow/templates/decisions-template.md`](.ai/workflow/templates/decisions-template.md)
   to `.ai/decisions/decisions.md` unedited first). Then write the ADR
   from [.ai/workflow/templates/adr-template.md](.ai/workflow/templates/adr-template.md)
   into `.ai/decisions/adr{NN}-{name}.md` and add its index row in the
   same step.
8. Commit the draft: stage `.ai/constitution/mission.md` and
   `.ai/constitution/techstack.md`, plus `.ai/info.md` if you just
   created it, and `.ai/decisions/` if you just scaffolded or added to
   it in step 7; the message should say what was drafted or updated,
   and whether this was a first-run bootstrap (see
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

`.ai/constitution/mission.md`, `.ai/constitution/techstack.md` —
always. `.ai/info.md` — first run only. A new ADR and
`.ai/decisions/decisions.md` row (scaffolded first if needed) if a
project-level decision was made.
