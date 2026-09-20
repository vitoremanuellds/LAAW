---
name: plan-task
description: The only skill that creates tasks. Reads workflow, task index, and context chosen by index; explores the project as needed; writes task file(s) from the template with minted IDs and slugs; adds root rows to .ai/tasks/index.md; asks for plan approval. Use when the human wants new work started or says "plan a task".
---

# Skill: plan-task

Plan-task turns a request into task file(s). It is the only skill that creates tasks, mints IDs,
or adds status rows.

## Steps

1. Read `.ai/workflow/workflow.md` (once per session) and `.ai/tasks/index.md`. Choose context by
   index (workflow.md §8): read `.ai/context/index.md`, open `project.md` plus every file whose
   name or summary matches the task, and note which files you read. Explore the project only as
   much as needed to plan honestly.
2. Decide the shape:
   - **Leaf task** — one coherent unit of work → a flat file with `Steps`.
   - **Super-task** — several independent workstreams that share a goal → a folder with a parent
     `task.md` (holding the Subtasks table) plus one child file per workstream.
   - A task has exactly one of these, never both.
3. Mint IDs and slugs (workflow.md §4): next root = highest root ID + 1 (`t{N}`); children of
   `t{N}` are `t{N}.1`, `t{N}.2`, … in order. Slugs: lowercase, hyphens, no spaces, ~30 chars
   max. No scripts, no randomness.
4. Write the task file(s) from `templates/task-template.md`:
   - Leaf: `.ai/tasks/t{N}_{slug}.md`.
   - Super-task: folder `.ai/tasks/t{N}_{slug}/` with `task.md` plus one child file per
     workstream, each named by its own ID: `t{N}.1_{slug}.md`, …
   - Every file gets:
     - `Description` — what and why, one paragraph.
     - `Context` — what the implementer must know; **list the `.ai/context/` files you read in
       step 1** — the human checks this selection at plan approval.
     - `Steps` (leaf or child) — small, checkable, in order. The parent instead gets a
       `Subtasks:` table (`| id | name | status |`) with one `draft` row per child.
     - `Validations` — real commands/checks that prove done (tests, builds, greps, manual checks).
     - `Context updates` — the exact `.ai/context/` changes this task will make when it finishes,
       or `none`. For a super-task, the parent lists what it expects children to report.
     - `Notes` — empty.
5. Add one `draft` row **per root** to `.ai/tasks/index.md` — roots only; child rows live in the
   parent's Subtasks table.
6. Show the task file(s) and ask: "Approve plan for t{N}?" then stop.

## Rules

- On rejection: revise the files/rows, keep status `draft`, re-ask. If the name or shape changes,
  rename or move the file(s) — nothing references a draft yet. Never start implementation in the
  same turn you asked.
- Do not set any status other than `draft`; the flip to `in-progress` belongs to implement-task
  and records the human's approval.
- Keep plans small enough that each task's Validations can actually be run.
