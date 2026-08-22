---
name: workflow-task
description: Use this skill to break a phase file's Plan section into individual tasks (tasks/p{NN}-t{NN}-{name}.md, flat, no per-phase subfolder), or to replan a single task after a task-level deviation. Trigger this whenever the user wants to define the next unit of implementable work, assign a task ID, or specify what files a task touches and how it will be validated. Writes tasks in enough detail that implementation is close to mechanical — explicit files to modify/create, ordered steps, optional pseudocode for non-obvious logic. On first use for a phase, stubs a row in that phase file's embedded task table (not-planned) for every remaining plan step, then fully drafts whichever task(s) were actually asked for — one, several, or all, depending on what's requested; it is not limited to one task per invocation. Requires an approved phase plan to already exist — use workflow-phase if it doesn't. Do not use this to actually implement the task's code.
---

# Skill: workflow.task

Operation for the **Task Planning Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

Breaking a phase's plan into individual tasks, or replanning one task
after a task-level deviation. **Scope is whatever was actually asked**
— "plan the first task" means exactly one; "plan the tasks for this
phase" or "break down the whole plan" means all remaining steps in one
pass. If the request is ambiguous about scope, ask rather than
defaulting silently to one or to all.

## Inputs

- The owning phase's `phases/p{NN}-{name}.md` — its Context section,
  Plan section (what to break down), and Tasks table (the table you'll
  update).
- Only the `context/` files and project source files this specific
  task actually touches — inspect the real code enough to write
  accurate file lists and steps; this is worth the extra reads, since
  it's what lets implementation be mechanical.

## Procedure

Steps 1–7 require no prior approval — draft everything for this
invocation before stopping for anything. Only step 8 is gated, and
it's a single stop for the whole batch, not one per task — don't make
the human approve four tasks one at a time when they asked for all
four together.

1. **If this is the first time any task has been planned for this
   phase**, or the phase file's Tasks table doesn't yet have a row for
   every step in its Plan section: add a row in that table for *every
   remaining* plan step, not just the ones in scope this invocation —
   ID assigned, Title from the plan step, Status `not-planned`, no
   task file yet for any of them. This is cheap (titles only, not full
   plans) and is what gives full visibility into the phase's task list
   immediately, rather than only after every task has been
   individually drafted. Skip this step entirely if the table already
   has a row for every plan step.
2. Update `info.md`'s Status section: if the phase's status in
   `roadmap.md` is still `plan-approved`, set it to `in-progress` there
   — task planning starting is the actual signal that work has begun.
   (If `info.md`'s Status section points at a different phase, or
   `roadmap.md` still shows `awaiting-plan-review` for this one, stop
   and check before proceeding — don't treat being asked to plan tasks
   as itself implying phase-review approval happened. Read `info.md`
   fresh for this check, not from earlier in the session.)

**Then, repeat steps 3–7 for each task actually in scope this
invocation:**

3. If this task doesn't already have an ID from step 1's stubbing,
   assign the next sequential one (`P{NN}-T{NN}`) — never reuse or
   renumber.
4. Write `tasks/p{NN}-t{NN}-{name}.md` — flat, directly under `tasks/`,
   no phase subfolder — with two sections:
   - **Context** — task-specific only. Don't repeat the phase file's
     own Context section — link to it instead
     (`../phases/p{NN}-{name}.md`). Relevant files, relevant
     constraints.
   - **Implementation** — detailed enough that implementation can be
     close to mechanical, not just described in prose:
     - **Objective** — one or two sentences, what this task achieves.
     - **Files to modify** — explicit paths, one line each on what
       changes and why.
     - **Files to create** — explicit paths, one line each on purpose.
       Keep this separate from "modify" — conflating them is exactly
       what makes a task file too vague to implement mechanically.
     - **Steps** — ordered, literal actions, not high-level
       description. "Add a `resetPassword` method to
       `auth.service.ts` that calls `/api/auth/reset`" not "handle
       password reset."
     - **Pseudocode** — optional, only when the logic isn't obvious
       from the steps alone (a new algorithm, a non-trivial data
       transform). Skip it when it would just restate the steps in a
       different font (a config change, a route registration). This
       is guidance for the Implementation Agent, not a literal script
       — see [../../workflow.md §6](../../workflow.md#6-deviations)
       for why deviating from its specifics isn't automatically a
       deviation.
     - **Dependencies**, **expected result**, **validation
       instructions**.

   Do not add a Status field to this file — status for every task lives
   exclusively in the owning phase file's Tasks table (step 6), never
   duplicated here.
5. Note dependencies on other tasks explicitly if they exist
   (`P01-T03 depends on P01-T02`) — this determines what can run in
   parallel. **If this task logically precedes tasks that already
   exist** (e.g. a replan inserts a foundational setup step after
   `P01-T01`–`P01-T04` were already created), this new task's own
   Depends-on may be empty, but go back and add it to the Depends-on
   column of every existing task that now needs it done first in the
   phase file's table. Skipping this leaves the dependency graph wrong
   in exactly the way that makes "implement the first task" ambiguous
   later (see
   [../../workflow.md §11](../../workflow.md#11-status-the-fast-pointer-and-the-permanent-record)) —
   ID order alone won't reflect the real sequence once this happens.
6. Update this task's row in the phase file's Tasks table — Status
   moves from `not-planned` to `awaiting-plan-review` now that its
   file exists:

   ```
   | ID | Title | Purpose | Depends on | Status |
   |---|---|---|---|---|
   | P01-T01 | Scaffold Angular project | ... | — | awaiting-plan-review |
   | P01-T02 | Define domain types | ... | P01-T01 | awaiting-plan-review |
   | P01-T03 | Implement scoring engine | ... | P01-T02 | not-planned |
   ```

   (Example: T01–T02 were in scope this invocation and got fully
   drafted; T03 exists as a stub from step 1 but wasn't asked for yet.)
7. Update `info.md`'s Status section: set `Active task` to this task's
   ID. If multiple tasks are in scope this invocation, the Status
   section can only reflect one at a time (see
   [../../workflow.md §12](../../workflow.md#12-multi-agent--multi-human))
   — use the last one drafted, or the one most likely to be
   implemented next.

8. **Once every task in scope for this invocation is drafted**, commit
   everything together — the new stubs from step 1, the fully-drafted
   task files, the phase file's updated table, `info.md`, all of it
   (see [../../workflow.md §13](../../workflow.md#13-commit-discipline)).
   Stop for task plan review (`task-review` gate) — see
   [../../../info.md](../../../info.md) (read fresh) — covering only
   the tasks actually drafted this invocation, not the stubs (nothing
   to review in a title-only row). **When approval comes back, that's
   a separate turn:** set Status to `plan-approved` in the phase file's
   table for every task that was approved — a partial approval (some
   tasks approved, others sent back) is fine; update each row according
   to its own outcome. In `manual`/`assisted` mode, report the approval
   and explicitly ask whether to proceed to implementation now, and
   wait for that answer as its own confirmation — don't begin
   implementing in the same response that reports the approval, even
   though `task-review` passing does technically authorize it (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)).
   `workflow-implementation`'s own first step is what finally moves
   each task's Status to `in-progress`, once you actually start it.

## Output

One `tasks/p{NN}-t{NN}-{name}.md` per task actually drafted this
invocation — not one for every stub row.
The owning `phases/p{NN}-{name}.md`'s Tasks table — updated with a row
for *every* remaining plan step (most at `not-planned` if this was the
first invocation for the phase), not just the ones drafted this time.
`info.md` and `constitution/roadmap.md` — updated to reflect the phase
moving to `in-progress` if this was the first task planned.
