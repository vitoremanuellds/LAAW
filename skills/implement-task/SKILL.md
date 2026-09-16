---
name: implement-task
description: Write, modify, or delete project code for a task with an already-approved task file. Requires task planning first — use define-task if the task file doesn't exist. Not for planning what a task should do.
---

# Skill: implement-task

This skill performs the **implementation** operation
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from).

- **Can:** read the task file + context; modify project files; run
  tools; fill in the task's Context After section after implementation;
  update subtask statuses in the parent's Subtasks table.
- **Must:** update the task's Status in `.ai/tasks/tasks.md` as it
  progresses (for root tasks); update subtask statuses in the parent's
  Subtasks table (for subtasks); record architectural decisions as
  context rows for `propagate-context` to promote later.
- **Cannot:** silently change approved requirements/plan.

Always use `tools/generate-id.py --prefix t` to generate IDs for any
project file that requires an ID. Never hardcode, guess, or manually
construct IDs — the script is the single source of truth for ID
generation across the entire project.

Always use `tools/generate-id.py --prefix c` to generate IDs for
context files.

This is the most frequently invoked skill in the workflow — it runs
once per task, potentially many times.

**All `.ai/`-artifact paths below (`.ai/info.md`, `.ai/tasks/...`) are
relative to the project root, not to this skill file — write the full
`.ai/...` path, never a bare or dot-relative one.** Project source
paths (the actual code you're editing) are correctly relative to the
project root already, same as normal.



<!-- TOC -->
<details><summary>Table of Contents</summary>

  - [1. What to read](#1-what-to-read)
  - [2. Procedure](#2-procedure)
  - [3. Finishing](#3-finishing)
  - [Output](#output)

</details>



- **Include a Table of Contents** with internal anchor links for files with 2+ `##` sections

## 1. What to read

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full,
same as every other skill — do not skip it for implementation. Then
read:

1. `.ai/info.md` — read fresh, not from earlier in the session;
   confirms whether `task-completion-review` is yours to self-certify.
2. The task file — `tasks/t{ID}-{name}/task.md` (leaf task) or
   `tasks/t{ID}-{name}/t{sub-ID}-{sub-name}/task.md` (parent with subtasks) —
   Context + Steps sections, including its Validations.
3. Only the files the task's Context section lists as relevant, plus
   whatever those reference and you actually end up touching. Don't
   pull in unrelated modules "for context."
4. Explore the actual codebase with `tree`/`find`/`grep`/`ls` directly
   when you need to locate something — there's no structure map to
   consult or keep in sync; the filesystem is the source of truth.

## 2. Procedure

1. Read the task file's Steps section in full.
2. Read the Context section and only the referenced files it names.
3. Check the task's current Status in `.ai/tasks/tasks.md`. It should
   be `in-progress`. If it's `planned`, `task-review` hasn't actually
   passed yet — stop and check before proceeding rather than assuming
   being asked to implement implies approval happened. Once confirmed,
   set Status to `in-progress` there.
   **The Status enum is exactly these four values, nothing else:**
   `not-started` · `planned` · `in-progress` · `done` (+`blocked`).
   If you find yourself wanting a status this list doesn't have, that's
   a signal you've misunderstood the situation, not a reason to invent
   one — stop and re-read
   [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)
   rather than write something new into the table.
4. **If this task is a subtask** (it has no row in `tasks.md` but has
   a row in a parent task's Subtasks table), check the parent's
   Subtasks table instead. The subtask's Status should be `in-progress`.
   If it's `planned`, `task-review` hasn't passed yet — stop and check
   before proceeding.
5. **If the task has subtasks**, walk through them in id order before
   implementing the parent's own Steps. For each subtask:
   - Update its status from `not-started` to `planned`, then to
     `in-progress`, in the parent's Subtasks table.
   - Read the subtask file (`tasks/t{parent-ID}-{parent-name}/t{sub-ID}-{sub-name}/task.md`)
     if it exists; read the parent's Steps if not.
   - Implement the subtask's work (follow its Steps section, or
     execute the parent's Steps directly if the subtask has no file).
   - Update its status to `done` in the Subtasks table.
   - If the subtask produced reusable knowledge, note it for
     `propagate-context` (the parent's Context After section captures
     the aggregate).
6. Follow the task's Steps in order. Adjust freely only where the task
   file explicitly marked a detail flexible. Everything else that
   doesn't match gets raised as a deviation per step 7.
7. If the plan turns out wrong in a way that changes scope, the
   library/API doesn't support what was planned, or the strategy
   itself has to change — stop and raise a deviation. Do not silently
   expand scope or improvise past what was approved.
8. **Decisions are context rows.** If an architectural decision is made
   along the way (a new dependency, a new pattern) that future work
   needs to know about, record it as a note for `propagate-context` to
   promote later, or write it directly as a context row
   (`c-{ID}-{name}.md`) if the operation contract assigns it to this
   skill. Context rows go into `context/`, not a separate decisions
   directory.

## 3. Finishing

1. **Fill in the Context After section.** Write the context/understanding
   this task PRODUCES once implemented — architecture facts, invariants,
   responsibilities, dependencies, constraints, domain knowledge. This
   section is read by `propagate-context` to determine what to promote
   to `context/`. Omit task history, temporary details, reasoning, or
   anything recorded elsewhere.
2. Set the task's Status to `done` (implementation complete, ready for
   validation).
3. **Update the Status row:**
   - For root tasks: update `.ai/tasks/tasks.md`.
   - For subtasks: update the parent task file's Subtasks table.
4. Commit: stage the modified/created project files, the updated Status
   row, and the filled-in Context After section; verify no
   `.gitignore`d files are included (run `git diff --cached` and check
   the output); the message should say what was implemented (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
   Stop for `task-completion-review` → `validate-work` — see
   `.ai/info.md` (read fresh) for whether that's yours to run
   (→ [validate-work](.ai/workflow/skills/validate-work/SKILL.md))
   or a human's.
5. Do not mark the task complete yourself — completion requires
   validation and review to pass first (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).

## Output

Modified project files; an updated Status row in `.ai/tasks/tasks.md`
(for root tasks) or the parent task file's Subtasks table (for
subtasks); the filled-in Context After section; a decision recorded as
a context row if an architectural decision was made; the task ready
for validation.
