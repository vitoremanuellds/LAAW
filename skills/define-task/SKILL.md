---
name: define-task
description: Break a plan into individual tasks (tasks/t{ID}-{name}.md), or draft a standalone task with no parent (tasks/t{ID}-{name}.md, indexed in tasks/tasks.md). Writes enough detail (files, ordered steps, optional pseudocode) that implementation is close to mechanical. On first use, scaffolds .ai/tasks/tasks.md. Supports subtasks: a parent task gets subtask rows in its table during parent planning (status not-started); subtasks are planned separately, one by one or all, each getting its own file and status moving to planned. Not for implementing code.
---

# Skill: define-task

This skill performs the **task-planning** operation
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from).

- **Can:** read the task's description + `context/`; create the task
  file with implementation-ready detail; scaffold `.ai/tasks/tasks.md`
  on first use; manage subtasks (parent rows during parent planning,
  full subtask files during separate subtask planning).
- **Must:** update `.ai/tasks/tasks.md` on every status change for
  root-level tasks — `tasks.md` is the only place status lives for
  them. For subtasks, update the parent task file's Subtasks table.
- **Cannot:** implement code; write an ADR — escalate as a deviation
  instead.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for task planning.

## When to use

Task planning: breaking a plan into individual tasks; replanning after
a task-level deviation; or drafting a standalone task with no parent.
Always writes to `.ai/tasks/`.

**Default scope is exactly one task** — "plan the first task" or
"plan the next task" means exactly one task, drafted and then the user
is asked whether to continue. "Plan all remaining tasks" or "break
down the whole plan" means every remaining step in one pass. The "draft
all" path is NOT the default: it only happens when the user explicitly
asks for it. If the request is ambiguous about scope, ask whether to
draft one task or all before proceeding — never default silently to
one or to all.

## Subtasks

A task may contain **subtasks** — smaller, more concrete units of work
that roll up into the parent task. Subtasks follow the exact same
planning and implementation flow as root tasks; they are planned and
implemented separately.

**Planning a parent task with subtasks:**
- `define-task` creates the parent task file.
- The parent file includes a Subtasks table with one row per subtask
  (id, name, description, depends on, status `not-started`).
- **No subtask files are created during parent planning.** Only the
  rows exist in the table.
- After the parent task is planned and approved, the user explicitly
  asks to plan the subtasks.

**Planning subtasks (separate operation):**
- When the user asks to plan subtasks, `define-task` drafts each
  subtask file (`tasks/t{ID}-{name}/t{ID}-{name}.md`) one by one
  (default) or all at once (if the user explicitly asks for "all").
- Each subtask is a full task file with all sections (Description,
  Context, In scope, Out of scope, Steps, Validations).
- Subtasks follow the same planning flow as root tasks: one by one
  or all, each goes through `task-review`, then `implement-task`.
- Subtask statuses live exclusively in the parent task's Subtasks
  table, **not** in `.ai/tasks/tasks.md`.

**Implementation:**
- `implement-task` walks through subtasks in id order when implementing
  a parent task, updating each subtask's status (`not-started` →
  `planned` → `in-progress` → `done`) in the parent's Subtasks table.
- Subtasks can also be implemented individually by asking to implement
  them directly.

## Inputs

- The task's description as given (from a plan section or a standalone
  request).
- `.ai/tasks/tasks.md` if it already exists.
- Only the `.ai/context/` files and project source files this specific
  task actually touches — inspect the real code enough to write
  accurate file lists and steps; this is worth the extra reads, since
  it's what lets implementation be mechanical.

## Procedure

**All paths below are `.ai/`-prefixed and relative to the project
root — not relative to this skill file.** A bare or dot-relative path
resolves against your current working directory when a write tool
executes it, not against where this skill file lives — write the full
`.ai/...` path every time. Status values you set here (`planned`,
`in-progress`) are two of exactly four in a closed enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)
for the full list; never invent one not on it.

Steps 1–7 require no prior approval — stubbing (step 1) and drafting
the task(s) in scope happen before stopping for anything. Only step 8
is gated. By default only ONE task is drafted this invocation; step 1
still stubs every remaining plan step (titles only, cheap) so the full
task list is visible immediately. Drafting the remaining tasks in
batch only happens when the user explicitly asks for "all".

### Planning a parent task (with or without subtasks)

1. **If `.ai/tasks/tasks.md` doesn't exist**, scaffold it now per
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)
   (an empty `| id | name | description | depends on | status |` table)
   — this is the project's first task. If `.ai/tasks/` itself doesn't
   exist yet either, creating it is part of the same step.
2. Mint the next ID using `tools/generate-id.py --prefix t` — the new
   id format.
3. **Recursive folder rule:** If the task has subtasks, create the
   folder `tasks/t{ID}-{name}/` with the parent file
   `t{ID}-{name}.md` inside it. If it's a leaf task (no subtasks),
   create the single file `tasks/t{ID}-{name}.md`. This is the
   **recursive folder rule** — every task follows the same shape:
   a folder named `t{ID}-{name}/` containing `t{ID}-{name}.md`.
4. Write the parent task file body per the **Task file body** section
   below. If the task has subtasks, add a row for each subtask in the
   Subtasks table with Status `not-started` — **do not create subtask
   files at this point**.
5. Note dependencies on other tasks explicitly if they exist — this
   determines what can run in parallel. **If this task logically
   precedes tasks that already exist** (e.g. a replan inserts a
   foundational setup step after T01–T04 were already created), this
   new task's own Depends-on may be empty, but go back and add it to
   the Depends-on column of every existing task in `tasks.md` that now
   needs it done first. Skipping this leaves the dependency graph
   wrong — ID order alone won't reflect the real sequence once this
   happens.
6. Add or update this task's row in `.ai/tasks/tasks.md` — Status
   `planned`.
7. **Once the parent task drafted this invocation is finished**, ask
   the user whether to draft the next task now, or stop — before
   requesting review. With the single-task default there's normally
   just one task, so this is really "draft the next task, or stop?"
   Batch several in one review cycle only when the user explicitly
   asked for all.
8. Commit everything together: stage the parent task file and
   `.ai/tasks/tasks.md`; the message should say which task was drafted
   (see [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline))
   — which single task by default, or "all" only when the user
   explicitly requested every task; exclude any gitignored files.
   Stop for `task-review` gate — see `.ai/info.md` (read fresh).
   **When approval comes back, that's a separate turn:** set Status to
   `in-progress` in `tasks.md` for every task that was approved — a
   partial approval (some tasks approved, others sent back) is fine;
   update each row according to its own outcome. In `manual`/`assisted`
   mode, report the approval and explicitly ask whether to proceed to
   implementation now, and wait for that answer as its own confirmation
   — don't begin implementing in the same response that reports the
   approval, even though `task-review` passing does technically
   authorize it (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).
   `implement-task`'s own first step is what finally moves each task's
   Status to `in-progress`, once you actually start it.

### Planning subtasks (after parent is planned)

When the user asks to plan the subtasks of a parent task:

1. For each subtask in the parent's Subtasks table (one by one by
   default, or all if the user explicitly asks for "all"):
   - Mint the next ID for the subtask using
     `tools/generate-id.py --prefix t`.
   - Create the subtask file per the recursive folder rule:
     `tasks/t{parent-ID}-{parent-name}/t{subtask-ID}-{subtask-name}.md`.
   - Write the subtask file body per the **Task file body** section
     below (full layout: Description, TL;DR, Context, In scope, Out
     of scope, Steps, Validations — no Subtasks section, since
     subtasks are leaf tasks).
   - Update the subtask's row in the parent's Subtasks table — Status
     `planned`.
2. Ask the user whether to draft the next subtask now, or stop —
   before requesting review. Same single-task default as the parent
   path.
3. Commit: stage the subtask file(s) and the parent task file's
   updated Subtasks table; the message should say which subtask was
   drafted; exclude any gitignored files.
4. Stop for `task-review` gate — see `.ai/info.md` (read fresh).
   **When approval comes back, that's a separate turn:** set Status to
   `in-progress` in the parent's Subtasks table for every subtask that
   was approved. Same "don't start implementing in the same response"
   rule as the parent path.

## Task file body

Write every task file with this layout:

```markdown
# <name>
**ID:** t{ID}       **Status:** in-progress

## Description
<what this task is and why — the intent, one short paragraph>

## TL;DR
- <topic — the fastest possible orientation, as bullets, not prose>
- <topic>

## Context
### Before
<the knowledge/situation the agent needs to START this task>
### After
<!-- Filled in by implement-task after implementation; propagate-context
     reads this section to promote reusable knowledge to context/ -->

## In scope
- <the changes this task makes>

## Out of scope
- <what is explicitly NOT touched>

## Steps
1. <ordered step>
2. <ordered step>
   - <pseudocode here where it helps>

## Validations
- <how to check done>

## Subtasks            ← optional; omit for a leaf task
| id | name | description | depends on | status |
|----|------|-------------|------------|--------|
```

- **Status in the task file is for display only** — the real status
  lives exclusively in `tasks.md` (or a parent task's Subtasks table
  for subtasks). The `**Status:** in-progress` in the template above
  is just a placeholder; `tasks.md` is the source of truth.
- **The Before section states relevant files and constraints directly,
  self-contained.**
- **The After section is left empty by `define-task` and filled in by
  `implement-task` after implementation finishes.** `implement-task`
  writes the context/understanding this task PRODUCES once implemented.
  `propagate-context` reads this section to determine what reusable
  knowledge to promote to `context/`.
- **Subtasks table** — optional; only present if the task has
  subtasks. Columns: id, name, description, depends on, status.
  Rows are id-ascending; new subtasks are appended at the end.
  `define-task` adds rows with Status `not-started` during parent
  planning (no files yet); subtasks move to `planned` when their
  files are created during separate subtask planning.
- **Deviation recording** — same inline `## Deviations` subsection
  pattern as before (added later by whichever operation raises it).

## Output

One task file per task actually drafted this invocation. Update
`.ai/tasks/tasks.md` (scaffolded first if needed) for root tasks;
update the parent task file's Subtasks table for subtasks.
