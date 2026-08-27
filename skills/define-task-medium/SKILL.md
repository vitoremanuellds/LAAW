---
name: define-task-medium
description: Medium-profile skill to define a new task (tasks/t{NN}-{name}.md, flat, no pseudocode) directly under the constitution's roadmap, or replan one after a task-level deviation. Requires the constitution to exist first. Not for the full profile (see define-task-full) — there's no phase layer here, so this skill both stubs and drafts tasks straight from the roadmap.
---

# Skill: define-task-medium

This skill performs the **task-planning** operation. Its
Can/Must/Cannot contract:
[.ai/workflow/workflow-medium.md §10](.ai/workflow/workflow-medium.md#10-operation-contracts).

Read [.ai/workflow/workflow-medium.md](.ai/workflow/workflow-medium.md)
in full, same as every other medium-profile skill — do not skip it for
task planning.

## When to use

Breaking the roadmap into individual tasks, or replanning one after a
task-level deviation. **Scope is whatever was actually asked** —
"plan the first task" means exactly one; "plan the tasks" means all
remaining ones in one pass. If the request is ambiguous about scope,
ask rather than defaulting silently to one or to all.

## Inputs

- `.ai/constitution/roadmap.md` — the flat task index (what you're
  drafting rows for and updating).
- Only the `.ai/context/context.md` and project source files this
  specific task actually touches — inspect the real code enough to
  write accurate file lists and steps.

## Procedure

**All paths below are `.ai/`-prefixed and relative to the project
root — not relative to this skill file.** Status values you set here
(`not-planned`, `awaiting-plan-review`, `in-progress`) are three of
exactly eight in a closed enum — see
[.ai/workflow/workflow-medium.md §11](.ai/workflow/workflow-medium.md#11-status-the-fast-pointer-and-the-permanent-record)
for the full list; never invent one not on it.

Steps 1–6 require no prior approval — draft everything for this
invocation before stopping for anything. Only step 7 is gated, and
it's a single stop for the whole batch, not one per task.

1. **If this is the first time any task has been planned**, or
   `roadmap.md` doesn't yet have a row for every known unit of work:
   add a row for *every remaining* known task, not just the ones in
   scope this invocation — ID assigned, Title, Status `not-planned`,
   no task file yet. Skip this step entirely if the table already has
   a row for every known task.

**Then, repeat steps 2–6 for each task actually in scope this
invocation:**

2. If this task doesn't already have an ID from step 1's stubbing,
   assign the next sequential one (`T{NN}`) — never reuse or renumber.
3. Write `.ai/tasks/t{NN}-{name}.md` — flat, directly under
   `.ai/tasks/`, never at the project root — with two sections:
   - **Context** — task-specific only. Link to `.ai/constitution/` or
     `.ai/context/context.md` instead of repeating them.
   - **Implementation** — detailed enough that implementation can be
     close to mechanical:
     - **Objective** — one or two sentences.
     - **Files to modify** / **Files to create** — explicit paths, one
       line each on what changes and why, kept separate from each
       other. Real project source paths, not `.ai/` artifacts.
     - **Steps** — ordered, literal actions, not high-level
       description. **No pseudocode section at this profile** — if the
       logic is non-trivial enough to need pseudocode, the steps
       themselves need to be more literal, not supplemented.
     - **Dependencies**, **expected result**, **validation
       instructions**.

   Do not add a Status field to this file — status lives exclusively
   in `.ai/constitution/roadmap.md`'s row for this task (step 5).
4. Note dependencies on other tasks explicitly if they exist (`T03
   depends on T02`). **If this task logically precedes tasks that
   already exist**, this new task's own Depends-on may be empty, but
   go back and add it to the Depends-on column of every existing task
   that now needs it done first — see
   [.ai/workflow/workflow-medium.md §11](.ai/workflow/workflow-medium.md#11-status-the-fast-pointer-and-the-permanent-record).
5. Update this task's row in `.ai/constitution/roadmap.md` — Status
   moves from `not-planned` to `awaiting-plan-review` now that its
   file exists.
6. Update `.ai/info.md`'s Status section: set `Active task` to this
   task's ID.

7. **Once every task in scope for this invocation is drafted**, commit
   everything together (see
   [.ai/workflow/workflow-medium.md §13](.ai/workflow/workflow-medium.md#13-commit-discipline)).
   Stop for task plan review (`task-review` gate) — see `.ai/info.md`
   (read fresh) — covering only the tasks actually drafted this
   invocation. **When approval comes back, that's a separate turn:**
   set Status to `plan-approved` in `roadmap.md` for every task
   approved — a partial approval is fine. In `manual`/`assisted` mode,
   report the approval and explicitly ask whether to proceed to
   implementation now, rather than starting it in the same response.
   `implement-task-medium`'s own first step is what moves each task's
   Status to `in-progress`.

## Output

One `.ai/tasks/t{NN}-{name}.md` per task actually drafted this
invocation — never at the project root. `.ai/constitution/roadmap.md`
updated with a row for *every* remaining known task (most at
`not-planned` if this was the first invocation). `.ai/info.md` updated.
