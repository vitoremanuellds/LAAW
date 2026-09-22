---
name: plan-project
description: "Project-level planning: several root tasks for the whole project (each a leaf or a super-task), wired together with depends-on, all scaffolded as drafts via tasks.py. Asks one plan approval for the whole board. Use when the human wants a plan with several root tasks (a project or milestone plan), not a single task."
---

# Skill: plan-project

Plan-project turns a project request into a board of root tasks. It is the only skill that
plans **several** roots at once; it creates them through the tasks CLI (which mints IDs, slugs,
filenames, and `draft` state) and asks for one plan approval of the whole board. Never
construct an ID, slug, or task filename yourself, and never hand-edit `state.json`.

If the human wants a single new task, that is **plan-task**, not this skill.

## Steps

1. Read `.ai/workflow/workflow.md` (once per session) and run `python3 .ai/workflow/tools/tasks.py board`
   fresh. Choose context by index (workflow.md §8): read `.ai/context/index.md`, open
   `project.md` plus every file whose name or summary matches the project, and note which
   files you read. Explore the project only as much as needed to plan honestly.
2. Agree the root list with the human: several root tasks, each one coherent unit of work
   (leaf or super-task, per plan-task's shape rules), small enough that its Validations can
   actually be run. Establish **order and dependencies** between roots: which root must be
   `done` before another can start? Record only real dependencies — a root with no true
   prerequisite gets no `depends-on` entry.
3. Scaffold every root via the tasks CLI (from the project root), in ID order:
   - Leaf: `python3 .ai/workflow/tools/tasks.py new "<Name>" --desc "<one line>"`
   - Super-task: `... new "<Name>" --super --desc "<one line>"`, then one
     `... subtask t{N} "<child name>" --desc "<one line>"` per workstream.
   Then wire the dependencies (draft tasks only):
   `... depends t{M} t{A} t{B}` (replaces the list; `--clear` empties it).
   Read the minted IDs from the CLI output.
4. Fill each task file's sections (the CLI left the template placeholders in place):
   - `Description` — what and why, one paragraph.
   - `In scope` / `Out of scope` — what the task covers, and what it explicitly does not
     (name the root where the out-of-scope work belongs, if any).
   - `Context` — what the implementer must know; **list the `.ai/context/` files you read in
     step 1** — the human checks this selection at plan approval.
   - `Steps` (leaf or child) — **implementation-ready**: concrete, in order, each step a small
     action or a short pseudocode block the implementer can execute without re-designing.
     Pseudocode and well-defined micro-steps are encouraged; never final code.
   - For a super-task parent: the `Subtasks:` list — one line per child:
     `- t{N}.{k} (t{N}.{k}_{slug}.md) — child name` (static; no status column).
   - `Validations` — real commands/checks that prove done (tests, builds, greps, manual checks).
   - `Context updates` — the exact `.ai/context/` changes this task will make when it finishes,
     or `none`. For a super-task parent: what you expect the children to report.
5. Show `tasks.py board` (it includes depends-on) plus a per-root summary — one line each:
   shape, in-scope outcome, depends-on — and ask: "Approve project plan (t1–tN)?" then stop.

## Rules

- On approval (a later human message): flip **only the first workable root** — the lowest-ID
  root whose depends-on are all `done` — with `tasks.py set-status t{N} in-progress`, and hand
  off to implement-task. The other roots stay `draft`; each gets its own plan-approval question
  ("Approve plan for tN?") via route when its turn comes, and the human's board approval is the
  answer to it. Never flip a blocked root — the CLI refuses it.
- On rejection: revise the board (all draft ops stay available: `rename`, `remove`, `subtask`,
  `depends`), then re-ask. Tasks stay `draft` until approved — you never call `set-status`
  in the same turn you asked.
- Never hand-edit `state.json`, never construct IDs/slugs/filenames, never start
  implementation in the same turn you asked.
- Keep the board small: several coherent roots, not a decomposition of one task — that is a
  super-task with subtasks, not five roots.
