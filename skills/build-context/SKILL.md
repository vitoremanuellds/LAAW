---
name: build-context
description: Populate .ai/context/ for a project that has little context yet — reads real files and writes c-{ID}.md items directly to context/. Not for propagating knowledge after a task completes — see propagate-context. Requires .ai/info.md to already exist; scaffolds .ai/context/ on first use if it doesn't exist yet.
---

# Skill: build-context

This skill performs the **context** operation, survey half — see also
`propagate-context` for the propagation half
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from). This
one builds context by surveying an existing codebase, not by
propagating what a completed task learned.

- **Can:** read project files; write `c-{ID}-{name}.md` to
  `context/`; update `context.md`'s index table.
- **Must:** get human review of context content before committing;
  never delete a `[ASSUMPTION]` or `[QUESTION]` line unilaterally.
- **Cannot:** copy task history; duplicate info; record reasoning.

Always use `tools/generate-id.py --prefix t` to generate IDs for any
project file that requires an ID. Never hardcode, guess, or manually
construct IDs — the script is the single source of truth for ID
generation across the entire project.

Always use `tools/generate-id.py --prefix c` to generate IDs for
context files.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for context building.

## When to use

`.ai/context/` is thin or doesn't exist — this skill builds it by
surveying the codebase. Not a required step of bootstrap; invoked when
the human wants context built up deliberately.

## Procedure

1. If `.ai/context/` doesn't exist, scaffold it (copy
   [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md)
   to `context.md`).
2. Run a recursive directory listing of the project, excluding
   `.git/`, `.ai/workflow/`, and build/dependency directories.
3. For each file (or batch of files, if the user specifies a batch
   size):
   - Read the file in full.
   - Write or update a `c-{ID}-{name}.md` context file in `context/`.
   - Update `context.md`'s index table in the same step.
4. Ask the user whether to process more files, or stop.
5. Commit — stage the updated `context/*.md` files and `context.md`'s
   table; the message should say which files were processed. Stop for
   `task-review` gate.

## Output

Updated `context/*.md` files, `context.md`'s index table, plus any
`c-{ID}.md` files created.
