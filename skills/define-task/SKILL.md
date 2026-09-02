---
name: define-task
description: Break a phase file's Plan section into individual phase-linked tasks (tasks/p{NN}-t{NN}-{name}.md), or draft a standalone orphan task with no phase parent (tasks/t{NN}-{name}.md, indexed in tasks/tasks.md) — either because the project has no phases at all, or this particular task just doesn't need one. Writes enough detail (files, ordered steps, optional pseudocode) that implementation is close to mechanical. On first use per phase, stubs every remaining plan step, then fully drafts whatever's in scope. Phase-linked requires an approved phase plan; orphan has no such precondition. Not for implementing code.
---

# Skill: define-task

This skill performs the **task-planning** operation
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from). Two
paths, depending on whether the task has a phase parent — see When to
use.

- **Can:** read the phase file + `context/` (phase-linked) or just
  `context/` + whatever the task touches (orphan); create the task
  file with implementation-ready detail; scaffold `.ai/tasks/tasks.md`
  on the project's first orphan task.
- **Must:** update the phase file's Tasks table (phase-linked) or
  `.ai/tasks/tasks.md` (orphan) on every status change — never both
  for the same task.
- **Cannot:** implement code; write an ADR — escalate as a deviation
  instead (phase-level for a phase-linked task; for an orphan task,
  there's no phase to escalate to — see Deviations convention below).

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for task planning.

## When to use

**Phase-linked:** breaking a phase's plan into individual tasks;
replanning one after a task-level deviation; or drafting tasks for
Plan items a phase's append just added. **Orphan:** drafting a
standalone task with no phase parent — either because the project
doesn't use phases at all, or this particular task just doesn't need
one, independently of whether phases exist elsewhere in the project
(`.ai/workflow/workflow.md §3`/§4). Task files, `p{NN}-t{NN}-{name}.md`
vs. `t{NN}-{name}.md`, are distinguished by filename shape alone, each
with its own independent ID sequence — never mixed.

**Default scope is exactly one task** — "plan the first task" or
"plan the next task" means exactly one task, drafted and then the user
is asked whether to continue. "Plan all remaining tasks" or "break
down the whole plan" means every remaining step in one pass (phase-
linked only — orphan tasks are drafted one request at a time, there's
no plan to exhaust). The "draft all" path is NOT the default: it only
happens when the user explicitly asks for it. If the request is
ambiguous about scope, ask whether to draft one task or all before
proceeding — never default silently to one or to all.

## Inputs

- Phase-linked: the owning phase's `.ai/phases/p{NN}-{name}.md` — its
  Context section, Plan section (what to break down), and Tasks table
  (the table you'll update).
- Orphan: the task's own description as given; `.ai/tasks/tasks.md` if
  it already exists.
- Both paths: only the `.ai/context/` files and project source files
  this specific task actually touches — inspect the real code enough
  to write accurate file lists and steps; this is worth the extra
  reads, since it's what lets implementation be mechanical.

## Procedure — phase-linked

**All paths below are `.ai/`-prefixed and relative to the project
root — not relative to this skill file.** A bare or dot-relative path
resolves against your current working directory when a write tool
executes it, not against where this skill file lives — write the full
`.ai/...` path every time. Status values you set here (`not-planned`,
`awaiting-plan-review`, `in-progress`) are three of exactly eight in a
closed enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)
for the full list; never invent one not on it.

Steps 1–7 require no prior approval — stubbing (step 1) and drafting
the task(s) in scope happen before stopping for anything. Only step 8
is gated. By default only ONE task is drafted this invocation; step 1
still stubs every remaining plan step (titles only, cheap) so the full
phase task list is visible immediately. Drafting the remaining tasks in
batch only happens when the user explicitly asks for "all".

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
2. If the phase's status in `.ai/phases/phases.md` is still
   `plan-approved`, set it to `in-progress` there — task planning
   starting is the actual signal that work has begun. If `phases.md`
   still shows `awaiting-plan-review` for this phase, stop and check
   before proceeding — don't treat being asked to plan tasks as itself
   implying phase-review approval happened. Read `phases.md` fresh for
   this check, not from earlier in the session.

**Then, repeat steps 3–6 for each task actually in scope this
invocation — by default that's a single task unless the user explicitly
asked for all:**

3. If this task doesn't already have an ID from step 1's stubbing,
   assign the next sequential one (`P{NN}-T{NN}`) — never reuse or
   renumber.
4. Write `.ai/tasks/p{NN}-t{NN}-{name}.md` — flat, directly under
   `.ai/tasks/`, no phase subfolder, and never at the project root —
   with two sections, per [Task file body](#task-file-body) below.
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
   [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)) —
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

7. **Once the task drafted this invocation is complete**, ask the user
   whether to draft the next task now, or stop — before requesting
   review. With the single-task default there's normally just one task,
   so this is really "draft the next task, or stop?" Batch several in
   one review cycle only when the user explicitly asked for all.
8. Commit everything together: stage every drafted
   `.ai/tasks/p{NN}-t{NN}-{name}.md`, the owning
   `.ai/phases/p{NN}-{name}.md`'s updated Tasks table (stub rows and
   all), and `.ai/phases/phases.md` if this was the phase's first task
   planned; the message should say which task was drafted (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline))
   — which single task by default, or "all" only when the user explicitly
   requested every task;
   exclude any gitignored files — gitignored layers simply have nothing to
   commit, not a violation of commit discipline.
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
   `implement-task`'s own first step is what finally moves
   each task's Status to `in-progress`, once you actually start it.

## Procedure — orphan

Same path/prefix rules as above. Steps 1–4 require no prior approval;
step 5 is gated.

Orphan tasks are drafted one at a time by default — there's no phase
Plan to exhaust, so there's never a "draft all" batch here. Step 6's
"more to add?" question therefore means "draft the next orphan task now,
or stop?", which is the same single-task default as the phase-linked
path.

1. **If `.ai/tasks/tasks.md` doesn't exist yet**, scaffold it now per
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)
   (an empty `| ID | Title | Purpose | Depends on | Status |` table) —
   this is the project's first orphan task. If `.ai/tasks/` itself
   doesn't exist yet either (the project's very first task of any
   kind), creating it is part of the same step.
2. Assign the next sequential orphan ID (`T{NN}`) — its own
   independent counter, never shared with phase-linked `P{NN}-T{NN}`
   IDs, never reused or renumbered.
3. Write `.ai/tasks/t{NN}-{name}.md` — flat, directly under
   `.ai/tasks/`, never at the project root — with the same two
   sections as the phase-linked path, per
   [Task file body](#task-file-body) below. The Context section has no
   phase file to link to instead of repeating — state relevant files
   and constraints directly, self-contained.
4. Note dependencies on other tasks explicitly if they exist (an
   orphan task can depend on a phase-linked one or another orphan one)
   in `tasks.md`'s Depends-on column, same reasoning as the
   phase-linked path's step 5.
5. Add or update this task's row in `.ai/tasks/tasks.md` — Status
   `awaiting-plan-review` now that its file exists.
6. Ask the user whether to draft the next orphan task now, or stop, before requesting review.
7. Commit: stage the task file and `.ai/tasks/tasks.md` (scaffolded
   first if needed); the message should say which orphan task was
   drafted (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline));
   exclude any gitignored files — gitignored layers simply have nothing to
   commit, not a violation of commit discipline.
   Stop for task plan review (`task-review` gate) — see `.ai/info.md`.
   **When approval comes back:** set Status to `plan-approved` in
   `tasks.md`. Same "don't start implementing in the same response"
   rule as the phase-linked path.

## Task file body

Both paths write the same two sections:

- **Context** — task-specific only. Phase-linked: don't repeat the
  phase file's own Context section — link to it instead
  (`../phases/p{NN}-{name}.md`, relative to this new task file's own
  location within `.ai/tasks/`). Orphan: no phase file to link to —
  state relevant files and constraints directly.
- **Implementation** — detailed enough that implementation can be
  close to mechanical, not just described in prose:
  - **Objective** — one or two sentences, what this task achieves.
  - **In scope** — a short bullet list of exactly what this task
    covers.
  - **Out of scope** — a short bullet list of adjacent things this
    task deliberately does *not* do — things a reader might otherwise
    assume are included, given the Objective.
  - **Files to modify** — explicit paths, one line each on what
    changes and why. These are real project source paths, relative to
    the project root like normal source code — not `.ai/` artifacts.
  - **Files to create** — explicit paths, one line each on purpose.
    Keep this separate from "modify" — conflating them is exactly what
    makes a task file too vague to implement mechanically.
  - **Steps** — ordered, literal actions, not high-level description.
    "Add a `resetPassword` method to `auth.service.ts` that calls
    `/api/auth/reset`" not "handle password reset." **Mark any step
    detail that's genuinely low-importance/flexible explicitly
    inline** — e.g. "(flexible: exact variable name)". Unmarked
    details are binding: a mismatch against them during implementation
    is a deviation
    ([.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations)),
    not a minor adjustment. Mark sparingly — the default is binding,
    not flexible.
  - **Pseudocode** — optional, only when the logic isn't obvious from
    the steps alone (a new algorithm, a non-trivial data transform).
    Skip it when it would just restate the steps in a different font
    (a config change, a route registration). This is guidance for the
    implementation operation, not a literal script — see
    [.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations)
    for why deviating from its specifics isn't automatically a
    deviation. **Write it in informal, language-agnostic notation —
    never the target language's real syntax.** No real
    class/decorator/import syntax, no exact method signatures, no code
    that would compile once imports were added. If what you've written
    looks like it could be pasted straight into the file, it's too
    literal — that's implementation, which this agent Cannot do (§10).
    For example, for a non-trivial transform, write:
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
  - **Automatic validations** — mechanically checkable: a command, a
    grep, a test run, literal enough to run without judgment.
  - **Manual validations** — requires a human or agent judgment call
    that can't be scripted. Both kinds present where applicable —
    never merge them back into one undifferentiated "validation
    instructions" list.

Do not add a Status field to either kind of task file, and do not add
a field recording where the task's description originated (a ticket
ID, a link) — task files stay agnostic to their source. Status for
every task lives exclusively in the owning phase file's Tasks table
(phase-linked) or `.ai/tasks/tasks.md` (orphan), never duplicated in
the task file itself.

**Deviations convention:** a deviation
([.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations))
is recorded inline in the task file, not a separate file — append (or
update) a `## Deviations` subsection with one entry per deviation:
`Expected / Discovered / Why it fails / Proposed fix / Replan?
(task/phase/project)`, lifecycle `OPEN → ADDRESSED → INCORPORATED`,
then delete the entry once its fact already lives in the plan,
implementation, or an ADR. This subsection doesn't exist in a freshly
drafted task file — you don't create it while planning; it's added
later, by whichever operation actually raises the deviation. For an
orphan task, there's no phase to escalate a phase-level deviation to —
a deviation serious enough to change the task's fundamental approach
is either replanned directly (re-run this skill on the same task) or,
if it's genuinely project-level in scope, escalated via
`create-constitution` like any other project-level deviation.

## Output

One task file per task actually drafted this invocation — never at the
project root — not one for every stub row. By default that's a single
task file (the stub rows from step 1 are table rows only, not files).
Produce more than one only when the user explicitly asked for all. Phase-linked: the owning
`.ai/phases/p{NN}-{name}.md`'s Tasks table, updated with a row for
*every* remaining plan step (most at `not-planned` if this was the
first invocation for the phase); `.ai/phases/phases.md` updated to
reflect the phase moving to `in-progress` if this was the first task
planned. Orphan: `.ai/tasks/tasks.md`, updated with this task's row
(scaffolded first if this was the project's first orphan task).
