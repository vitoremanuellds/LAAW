---
name: bootstrap
description: Ask which optional layers (constitution/context/decisions/phases/workbench) a project wants set up now, then trigger each chosen layer's own scaffold-on-first-use step. Always ensures .ai/info.md exists first, regardless of which optional layers are chosen. Tasks are excluded from the menu — always implicit, scaffolded by the first task regardless. Safe to re-run later to add a layer not chosen initially. Does not author real mission/techstack/phase/task content itself beyond what create-constitution's own interview does when constitution is chosen.
---

# Skill: bootstrap

This skill performs the **layer setup** operation
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from). It owns
no scaffolding logic of its own — it is a thin front end over the
convention in
[reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md),
delegating to each chosen layer's own owning skill.

- **Can:** ask which optional layers to enable now; trigger each
  chosen layer's own scaffold step.
- **Must:** ensure `.ai/info.md` exists before anything else,
  unconditionally — it's gate-authority plumbing, not one of the
  optional layers on the menu; never overwrite a layer that already
  exists; stay safely re-runnable later for a layer not chosen this
  time.
- **Cannot:** author real mission/techstack content itself (that's
  `create-constitution`'s own interview, which this skill triggers
  rather than duplicates); author real phase/task/context-survey
  content — a layer chosen here gets an empty, ready-to-use scaffold,
  not drafted content.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for bootstrap work.

## When to use

A human wants to set up several optional layers deliberately, in one
sitting, rather than discovering each one lazily the first time its
owning skill gets used for real work. Equally valid to never run this
at all — every layer comes into existence just as well the first time
its owning skill is actually invoked (see
[reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)).
Re-running this later to add a layer not chosen the first time is
normal, not a special case.

## Inputs

- [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md) —
  the layer-ownership table this skill delegates against.
- The user's choice of which optional layers to enable now.

## Procedure

All paths below are `.ai/`-prefixed and relative to the project root —
not relative to this skill file.

1. If `.ai/info.md` doesn't exist yet, create it now via
   `create-constitution`'s own info.md-bootstrap step (copy
   [`.ai/workflow/templates/info-template.md`](.ai/workflow/templates/info-template.md)
   to `.ai/info.md` unedited) — this happens regardless of which
   optional layers get chosen below; `info.md` isn't one of them.
2. Check which optional layers already exist (constitution, context,
   decisions, phases, workbench — each per
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)'s
   directory column). Ask the user only about the ones that don't
   exist yet — never re-offer a layer already present, and never
   overwrite one.
3. For each layer the user chooses:
   - **Constitution** — run `create-constitution`'s full procedure
     now (the mission/techstack interview happens as part of this
     choice, not deferred) — including its own commit and
     `constitution-review` gate at the end. This is the one layer
     where "chosen during bootstrap" means real content gets
     authored, not just an empty scaffold, since mission/techstack
     only exist as interviewed content.
   - **Context** — create `.ai/context/` and copy
     [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md)
     to `.ai/context/context.md` unedited. An empty, ready-to-use
     scaffold — an actual codebase survey is `build-context`'s own,
     separate, larger operation, run later if wanted.
   - **Decisions** — create `.ai/decisions/` and copy
     [`.ai/workflow/templates/decisions-template.md`](.ai/workflow/templates/decisions-template.md)
     to `.ai/decisions/decisions.md` unedited.
   - **Phases** — create `.ai/phases/` and `.ai/phases/phases.md` (an
     empty `| ID | Title | Depends on | Status |` table) — no phase
     content, that's `define-phase`'s own job once there's an actual
     phase to plan.
   - **Workbench** — create `.ai/workbench/` and copy
     [`.ai/workflow/templates/workbench-readme-template.md`](.ai/workflow/templates/workbench-readme-template.md)
     to `.ai/workbench/README.md` unedited.
4. Commit: stage everything scaffolded this run (excluding whatever
   constitution's own procedure already committed itself in step 3);
   the message should say which layers were set up (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
   No gate of its own for the non-constitution layers — an empty
   scaffold carries no decision to review; if constitution was chosen,
   its own `constitution-review` gate already applied in step 3.

## Output

`.ai/info.md` — always, first run only. Any subset of
`.ai/constitution/{mission,techstack}.md` (via `create-constitution`,
with its own gate), `.ai/context/context.md`,
`.ai/decisions/decisions.md`, `.ai/phases/phases.md`,
`.ai/workbench/README.md` — whichever layers were chosen. `.ai/tasks/`
is never scaffolded here — it comes into existence with the project's
first task, phase-linked or orphan, via `define-task`.
