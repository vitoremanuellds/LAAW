---
name: define-task-full
description: Full-profile skill to break a phase file's Plan section into individual tasks (tasks/p{NN}-t{NN}-{name}.md, flat), or replan one after a task-level deviation. Writes enough detail (files, ordered steps, optional pseudocode) that implementation is close to mechanical. On first use per phase, stubs every remaining plan step, then fully drafts whatever's in scope — one, several, or all. Requires an approved phase plan. Not for implementing code.
---

# Skill: define-task-full

This skill performs the **task-planning** operation
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from).

- **Can:** read the phase file + `context/`; create the task file
  with implementation-ready detail.
- **Must:** update the phase file's task table on every status
  change; refresh `info.md`'s Active task pointer.
- **Cannot:** implement code; write an ADR — escalate as a
  phase-level deviation.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for task planning.

## When to use

Breaking a phase's plan into individual tasks; replanning one task
after a task-level deviation; or drafting tasks for Plan items a
phase's append (`define-phase`, not tied to a deviation — see
[.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations))
just added — same mechanics as any other invocation, since step 1
below already stubs a row for any Plan item that doesn't have one yet,
regardless of whether it arrived via the phase's initial plan or a
later append. **Scope is whatever was actually asked**
— "plan the first task" means exactly one; "plan the tasks for this
phase" or "break down the whole plan" means all remaining steps in one
pass. If the request is ambiguous about scope, ask rather than
defaulting silently to one or to all.

## Inputs

- The owning phase's `.ai/phases/p{NN}-{name}.md` — its Context section,
  Plan section (what to break down), and Tasks table (the table you'll
  update).
- Only the `.ai/context/` files and project source files this specific
  task actually touches — inspect the real code enough to write
  accurate file lists and steps; this is worth the extra reads, since
  it's what lets implementation be mechanical.

## Procedure

**All paths below are `.ai/`-prefixed and relative to the project
root — not relative to this skill file.** A bare or dot-relative path
resolves against your current working directory when a write tool
executes it, not against where this skill file lives — write the full
`.ai/...` path every time. Status values you set here (`not-planned`,
`awaiting-plan-review`, `in-progress`) are three of exactly eight in a
closed enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)
for the full list; never invent one not on it.

Steps 1–8 require no prior approval — draft everything for this
invocation before stopping for anything. Only step 9 is gated, and
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
2. Update `.ai/info.md`'s Status section: if the phase's status in
   `.ai/constitution/roadmap.md` is still `plan-approved`, set it to
   `in-progress` there — task planning starting is the actual signal
   that work has begun. (If `.ai/info.md`'s Status section points at a
   different phase, or `roadmap.md` still shows `awaiting-plan-review`
   for this one, stop and check before proceeding — don't treat being
   asked to plan tasks as itself implying phase-review approval
   happened. Read `.ai/info.md` fresh for this check, not from earlier
   in the session.)

**Then, repeat steps 3–7 for each task actually in scope this
invocation:**

3. If this task doesn't already have an ID from step 1's stubbing,
   assign the next sequential one (`P{NN}-T{NN}`) — never reuse or
   renumber.
4. Write `.ai/tasks/p{NN}-t{NN}-{name}.md` — flat, directly under
   `.ai/tasks/`, no phase subfolder, and never at the project root —
   with two sections:
   - **Context** — task-specific only. Don't repeat the phase file's
     own Context section — link to it instead
     (`../phases/p{NN}-{name}.md`, relative to this new task file's
     own location within `.ai/tasks/`). Relevant files, relevant
     constraints.
   - **Implementation** — detailed enough that implementation can be
     close to mechanical, not just described in prose:
     - **Objective** — one or two sentences, what this task achieves.
     - **In scope** — a short bullet list of exactly what this task
       covers.
     - **Out of scope** — a short bullet list of adjacent things this
       task deliberately does *not* do — things a reader might
       otherwise assume are included, given the Objective.
     - **Files to modify** — explicit paths, one line each on what
       changes and why. These are real project source paths, relative
       to the project root like normal source code — not `.ai/`
       artifacts.
     - **Files to create** — explicit paths, one line each on purpose.
       Keep this separate from "modify" — conflating them is exactly
       what makes a task file too vague to implement mechanically.
     - **Steps** — ordered, literal actions, not high-level
       description. "Add a `resetPassword` method to
       `auth.service.ts` that calls `/api/auth/reset`" not "handle
       password reset." **Mark any step detail that's genuinely
       low-importance/flexible explicitly inline** — e.g. "(flexible:
       exact variable name)". Unmarked details are binding: a mismatch
       against them during implementation is a deviation
       ([.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations)),
       not a minor adjustment. Mark sparingly — the default is binding,
       not flexible.
     - **Pseudocode** — optional, only when the logic isn't obvious
       from the steps alone (a new algorithm, a non-trivial data
       transform). Skip it when it would just restate the steps in a
       different font (a config change, a route registration). This
       is guidance for the implementation operation, not a literal
       script
       — see [.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations)
       for why deviating from its specifics isn't automatically a
       deviation. **Write it in informal, language-agnostic
       notation — never the target language's real syntax.** No real
       class/decorator/import syntax, no exact method signatures, no
       code that would compile once imports were added. If what
       you've written looks like it could be pasted straight into the
       file, it's too literal — that's implementation, which this
       agent Cannot do (§10). For example, for a non-trivial
       transform, write:
       ```
       for each raw item:
         if item.status is "archived", skip it
         group remaining items by item.category
         within each group, sort by item.updatedAt descending
       return groups as a list of {category, items} entries
       ```
       not:
       ```typescript
       items.filter(i => i.status !== 'archived')
         .reduce((acc, i) => { acc[i.category] ??= []; acc[i.category].push(i); return acc; }, {} as Record<string, Item[]>)
       ```
     - **Dependencies**, **expected result**.
     - **Automatic validations** — mechanically checkable: a command,
       a grep, a test run, literal enough to run without judgment.
     - **Manual validations** — requires a human or agent judgment
       call that can't be scripted. Both kinds present where
       applicable — never merge them back into one undifferentiated
       "validation instructions" list.

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
   [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)) —
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
7. Update `.ai/info.md`'s Status section: set `Active task` to this
   task's ID. If multiple tasks are in scope this invocation, the
   Status section can only reflect one at a time (see
   [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record))
   — use the last one drafted, or the one most likely to be
   implemented next.

8. **Once every task in scope for this invocation is drafted**, ask
   the user whether there's more to add — more tasks to draft this
   invocation, or scope missing from the ones just drafted — before
   requesting review; batch it in now rather than triggering a second
   review cycle later.
9. Commit everything together: stage every drafted
   `.ai/tasks/p{NN}-t{NN}-{name}.md`, the owning
   `.ai/phases/p{NN}-{name}.md`'s updated Tasks table (stub rows and
   all), `.ai/info.md`, and `.ai/constitution/roadmap.md` if this was
   the phase's first task planned; the message should say which tasks
   were drafted (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
   Stop for task plan review (`task-review` gate) — see `.ai/info.md`
   (read fresh) — covering only the tasks actually drafted this
   invocation, not the stubs (nothing to review in a title-only row).
   **When approval comes back, that's a separate turn:** set Status to
   `plan-approved` in the phase file's table for every task that was
   approved — a partial approval (some tasks approved, others sent
   back) is fine; update each row according to its own outcome. In
   `manual`/`assisted` mode, report the approval and explicitly ask
   whether to proceed to implementation now, and wait for that answer
   as its own confirmation — don't begin implementing in the same
   response that reports the approval, even though `task-review`
   passing does technically authorize it (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).
   `implement-task-full`'s own first step is what finally moves
   each task's Status to `in-progress`, once you actually start it.

**Deviations convention:** a deviation
([.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations))
is recorded inline in the task file, not a separate file — append (or
update) a `## Deviations` subsection with one entry per deviation:
`Expected / Discovered / Why it fails / Proposed fix / Replan?
(task/phase/project)`, lifecycle `OPEN → ADDRESSED → INCORPORATED`,
then delete the entry once its fact already lives in the plan,
implementation, or an ADR. This subsection doesn't exist in a freshly
drafted task file — you don't create it while planning; it's added
later, by whichever operation actually raises the deviation.

## Output

One `.ai/tasks/p{NN}-t{NN}-{name}.md` per task actually drafted this
invocation — never at the project root — not one for every stub row.
The owning `.ai/phases/p{NN}-{name}.md`'s Tasks table — updated with a
row for *every* remaining plan step (most at `not-planned` if this was
the first invocation for the phase), not just the ones drafted this
time.
`.ai/info.md` and `.ai/constitution/roadmap.md` — updated to reflect
the phase moving to `in-progress` if this was the first task planned.
