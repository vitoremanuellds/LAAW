---
name: bootstrap
description: Ask which optional layers (context/workbench) a project wants set up now, then trigger each chosen layer's own scaffold-on-first-use step. Always ensures .ai/info.md exists first, regardless of which optional layers are chosen. Safe to re-run later to add a layer not chosen initially. Does not author real mission/techstack/task content itself beyond what create-constitution's own interview does when context is chosen.
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
  rather than duplicates); author real task/context-survey content —
  a layer chosen here gets an empty, ready-to-use scaffold, not
  drafted content.

Always use `tools/generate-id.py --prefix t` to generate IDs for any
project file that requires an ID. Never hardcode, guess, or manually
construct IDs — the script is the single source of truth for ID
generation across the entire project.

Always use `tools/generate-id.py --prefix c` to generate IDs for
context files.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for bootstrap work.



<!-- TOC -->
<details><summary>Table of Contents</summary>

  - [When to use](#when-to-use)
  - [Inputs](#inputs)
  - [Procedure](#procedure)
  - [Output](#output)

</details>



- **Include a Table of Contents** with internal anchor links for files with 2+ `##` sections

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
2. Check which optional layers already exist (context, workbench — each per
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)'s
   directory column). Ask the user only about the ones that don't
   exist yet — never re-offer a layer already present, and never
   overwrite one.
3. For each layer the user chooses:
   - **Context** — create `.ai/context/` and copy
     [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md)
     to `.ai/context/context.md` unedited. An empty, ready-to-use
     scaffold — an actual codebase survey is `build-context`'s own,
     separate, larger operation, run later if wanted.
   - **Workbench** — create `.ai/workbench/` and copy
     [`.ai/workflow/templates/workbench-readme-template.md`](.ai/workflow/templates/workbench-readme-template.md)
     to `.ai/workbench/README.md` unedited.
4. Commit — stage everything scaffolded this run; the message should
   say which layers were set up (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
   No gate of its own for the optional layers — an empty
   scaffold carries no decision to review.

## Output

`.ai/info.md` — always, first run only. Any subset of
`.ai/context/context.md` (via `create-constitution`, with its own
gate), `.ai/workbench/README.md` — whichever layers were chosen.
`.ai/tasks/` is never scaffolded here — it comes into existence with
the project's first task via `define-task`.
