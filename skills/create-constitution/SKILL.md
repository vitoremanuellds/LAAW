---
name: create-constitution
description: Create or update a project's context (mission + techstack as inline core in context.md) — an optional layer. Always bootstraps .ai/info.md on first run, regardless of whether mission/techstack content is wanted, since info.md is gate-authority plumbing, not an optional layer. Not for task planning — see define-task. Not for scaffolding any layer other than info.md + context/ — that's each other layer's own owning skill, see reference/scaffold-on-first-use.md. Decisions are written as c-{ID}-{name}.md context rows.
---

# Skill: create-constitution

This skill performs the **constitution** operation
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from).

- **Can:** context artifacts (mission, techstack, decisions as
  `c-{ID}.md`), ask clarification.
- **Must:** write `c-{ID}-{name}.md` for project-level decisions;
  first run, bootstrap `info.md` unedited, never overwrite existing.
- **Cannot:** touch code; invent unsupported requirements; scaffold
  any layer other than `info.md` + `context/` — that's each other
  layer's own owning skill, per
  [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md).

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for constitution work.

## When to use

Creating or updating `.ai/context/context.md` (mission/techstack
inline + index table). On a brand-new project, this is also what
bootstraps `.ai/info.md` — the one piece of first-run scaffolding this
skill owns unconditionally, since gate authority isn't an optional
layer the way context content is. A project that never wants a
constitution at all still needs `info.md`; running this skill
(directly, or via `bootstrap`) is what creates it.

## Inputs

- User-provided project information (interview, existing docs, stated
  goals).
- Existing context files, if updating.
- [`.ai/workflow/templates/info-template.md`](.ai/workflow/templates/info-template.md) —
  only read/used if `.ai/info.md` doesn't exist yet.
- [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md) —
  the single-folder index template (now includes inline mission/techstack
  core + index table with columns: File, Description, Relation, Superseded by).

## Procedure

All paths below are `.ai/`-prefixed and relative to the project root —
not relative to this skill file. Steps 1–7 require no prior approval —
draft everything before stopping for anything. Only step 8 is gated.

1. Read existing context files if present — do not overwrite blind.
2. **First run only:** if `.ai/info.md` doesn't exist, copy
   [`.ai/workflow/templates/info-template.md`](.ai/workflow/templates/info-template.md)
   there unedited — its defaults (`mode: assisted`) are the safe
   starting point; the human adjusts it later, not you. This is the
   only file this skill scaffolds unconditionally — every other layer
   (context, workbench) is scaffolded by its own owning skill on first
   use, never here (see
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)).
   Never overwrite `info.md` if it already exists — a second
   constitution run (updating an existing project) skips this step
   entirely.
3. Ask the user for anything missing that's required to write mission
   or tech stack. Do not invent goals or constraints the user hasn't
   stated or clearly implied.
4. Write `.ai/context/context.md`: inline mission/techstack core +
   index table (columns: File, Description, Status, Relations). Keep
   it stable — this file should rarely need to change.
5. Ask the user whether there's anything else to add to this draft
   (mission or techstack) before requesting review — batch it in now
   rather than triggering a second review cycle later for something
   that could have been included in this one.
6. If a project-level decision was made while drafting mission or
   techstack that future work needs to know about, write a
   `c-{ID}-{name}.md` context row (use
   `tools/generate-id.py --prefix c` to generate the ID) and add its
   index row in `context.md`'s table.
7. Commit — stage `context/context.md` (and `info.md` if just
   created), plus any `c-{ID}.md` files; the message should say what
   was drafted or updated, and whether this was a first-run bootstrap
   (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
   Stop for `task-review` gate — see
   `.ai/info.md` (read fresh, not from memory) for who approves it.
   **When approval comes back:** in `manual`/`assisted` mode, report
   and explicitly ask whether to proceed.

## Output

`.ai/context/context.md` (always). `.ai/info.md` — first run only. A
new `c-{ID}-{name}.md` context row if a project-level decision was
made.
