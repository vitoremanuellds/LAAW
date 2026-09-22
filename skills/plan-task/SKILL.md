---
name: plan-task
description: The only skill that creates tasks. Reads workflow, board, and context chosen by index; scaffolds task file(s) via tasks.py new/subtask (the CLI mints IDs, slugs, files, and draft state); fills the task file sections; asks for plan approval. Use when the human wants new work started or says "plan a task".
---

# Skill: plan-task

Plan-task turns a request into task file(s). It is the only skill that creates tasks — and it
does so through the tasks CLI, which mints IDs, slugs, filenames, and `draft` state. Never
construct an ID, slug, or task filename yourself, and never hand-edit `state.json`.

## Steps

1. Read `.ai/workflow/workflow.md` (once per session) and run `python3 .ai/workflow/tools/tasks.py board`
   fresh. Choose context by index (workflow.md §8): read `.ai/context/index.md`, open
   `project.md` plus every file whose name or summary matches the task, and note which files
   you read. Explore the project only as much as needed to plan honestly.
2. Decide the shape:
   - **Leaf task** — one coherent unit of work → a flat file with `Steps`.
   - **Super-task** — several independent workstreams that share a goal → a folder with a parent
     `task.md` plus one child file per workstream.
   - A task has exactly one of these, never both.
3. Scaffold via the tasks CLI (from the project root):
   - Leaf: `python3 .ai/workflow/tools/tasks.py new "<Name>" --desc "<one line>"`
   - Super-task: `... new "<Name>" --super --desc "<one line>"`, then one
     `... subtask t{N} "<child name>" --desc "<one line>"` per workstream.
   The CLI mints the IDs (`t{N}`, `t{N}.{k}`), writes the files from the templates, and
   registers them as `draft`. Read the IDs from its output.
4. Fill each task file's sections (the CLI left the template placeholders in place):
   - `Description` — what and why, one paragraph.
   - `In scope` / `Out of scope` — what the task covers, and what it explicitly does not (name
     where the out-of-scope work belongs, if anywhere).
   - `Context` — what the implementer must know; **list the `.ai/context/` files you read in
     step 1** — the human checks this selection at plan approval.
   - `Steps` (leaf or child) — **implementation-ready**: concrete, checkable, in order. Each
     step is a small action or a short pseudocode block the implementer can execute without
     re-designing — abstract enough to stay code-free, concrete enough that it is not a second
     planning exercise. A step the implementer would have to break down again is too abstract.
   - If this task can only start once other existing root tasks are `done`, wire it with
     `tasks.py depends t{N} t{A} …` (draft tasks only) and say so in the approval summary.
   - For a super-task parent: the `Subtasks:` list — one line per child:
     `- t{N}.{k} (t{N}.{k}_{slug}.md) — child name` (static; no status column).
   - `Validations` — real commands/checks that prove done (tests, builds, greps, manual checks).
   - `Context updates` — the exact `.ai/context/` changes this task will make when it finishes,
     or `none`. For a super-task parent: what you expect the children to report.
5. Show the task file(s) and ask: "Approve plan for t{N}?" (root ID from the CLI output), then stop.

## Rules

- If the human wants **several root tasks** (a project or milestone plan), hand off to
  **plan-project** instead — one root per request is this skill's scope.
- On rejection: revise the files, re-ask. If the name or shape changes: `tasks.py rename` /
  `remove` / `depends` (all draft-only), then re-scaffold. Tasks stay `draft` until the human
  approves — you never call `set-status`.
- Never hand-edit `state.json`, never construct IDs/slugs/filenames, never start
  implementation in the same turn you asked.
- Keep plans small enough that each task's Validations can actually be run.
