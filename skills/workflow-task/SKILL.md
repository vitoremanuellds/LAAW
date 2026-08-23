---
name: workflow-task
description: Use this skill to break a phase's plan into individual tasks — own file at profile full (tasks/p{NN}-t{NN}-{name}.md), inline block in the owning table's row at medium/lite — or replan one after a task-level deviation. Writes enough detail (files, ordered steps, pseudocode at full only) that implementation is close to mechanical. On first use, stubs every remaining plan step, then fully drafts whatever's in scope — one, several, or all. Requires an approved phase plan (full/medium) or approved constitution (lite). Not for implementing code.
---

# Skill: workflow.task

Operation for the **Task Planning Agent**. Contract:
[.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts).

## When to use

Breaking a phase's plan into individual tasks (`full`/`medium`) or
`.ai/project.md`'s flat Roadmap into individual tasks directly
(`lite`, no phase to break down — §14), or replanning one task after a
task-level deviation. **Scope is whatever was actually asked**
— "plan the first task" means exactly one; "plan the tasks for this
phase" or "break down the whole plan" means all remaining steps in one
pass. If the request is ambiguous about scope, ask rather than
defaulting silently to one or to all.

## Inputs

- At `profile: full`/`medium`: the owning phase's
  `.ai/phases/p{NN}-{name}.md` — its Context section, Plan section
  (what to break down), and Tasks table (the table you'll update). At
  `lite`: `.ai/project.md`'s Roadmap section instead — its flat task
  table, no phase file exists (see
  [.ai/workflow/workflow.md §14](.ai/workflow/workflow.md#14-profiles)).
- Only the relevant context files (`.ai/context/`, or `techstack.md`'s/
  `project.md`'s `## Context` subsection at `medium`/`lite`) and
  project source files this specific task actually touches — inspect
  the real code enough to write accurate file lists and steps; this is
  worth the extra reads, since it's what lets implementation be
  mechanical.

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
   has a row for every plan step. **At `profile: lite`**, there's no
   "phase's Plan section" to stub from — `workflow-constitution`
   already stubbed the initial row set directly into `.ai/project.md`'s
   Roadmap table; this step only applies on a later invocation that
   adds genuinely new rows (e.g. after a replan).
2. **Not applicable at `profile: lite`** — there's no phase status to
   flip (§14). At `full`/`medium`: update `.ai/info.md`'s Status
   section: if the phase's status in `.ai/constitution/roadmap.md` is
   still `plan-approved`, set it to `in-progress` there — task planning
   starting is the actual signal that work has begun. (If
   `.ai/info.md`'s Status section points at a different phase, or
   `roadmap.md` still shows `awaiting-plan-review` for this one, stop
   and check before proceeding — don't treat being asked to plan tasks
   as itself implying phase-review approval happened. Read `.ai/info.md`
   fresh for this check, not from earlier in the session.)

**Then, repeat steps 3–7 for each task actually in scope this
invocation:**

3. If this task doesn't already have an ID from step 1's stubbing,
   assign the next sequential one — `P{NN}-T{NN}` at `full`/`medium`;
   flat `T{NN}` at `lite` (no phase prefix — there's no phase, §14) —
   never reuse or renumber.
4. Write the task's detail, covering two sections — **Context**
   (task-specific only; don't repeat the owning file's own Context
   section, link to it instead) and **Implementation** (detailed
   enough that implementation can be close to mechanical, not just
   described in prose): **Objective** (one or two sentences), **Files
   touched** — explicit real project source paths, one line each on
   what changes/is created and why (at `full`, keep "Files to modify"
   and "Files to create" as two separate lists — conflating them is
   what makes a task too vague to implement mechanically; at
   `medium`/`lite`, one merged "Files touched" list is enough), ordered
   literal **Steps** ("Add a `resetPassword` method to
   `auth.service.ts` that calls `/api/auth/reset`" not "handle
   password reset"), **Dependencies**, **expected result**, **validation
   instructions**.

   **Pseudocode** — at `profile: full` only, optional, and only when
   the logic isn't obvious from the steps alone (a new algorithm, a
   non-trivial data transform); skip it when it would just restate the
   steps in a different font. **At `medium`/`lite`, never write a
   Pseudocode subsection at all**, regardless of complexity — rely on
   Steps alone (§14's token-cost cut). When it does apply (`full`),
   it's guidance for the Implementation Agent, not a literal script —
   see [.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations)
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

   **Where this detail is written differs by profile (§14):**
   - `full`: its own file, `.ai/tasks/p{NN}-t{NN}-{name}.md` — flat,
     directly under `.ai/tasks/`, no phase subfolder, never at the
     project root. Context section links to
     `../phases/p{NN}-{name}.md` (relative to this task file's own
     location).
   - `medium`: an inline block nested directly under this task's row
     in the owning `.ai/phases/p{NN}-{name}.md`'s Tasks table — no
     separate task file at all. Context section links to the phase
     file's own Context section by heading, not a separate path.
   - `lite`: an inline block nested directly under this task's row in
     `.ai/project.md`'s Roadmap table. Context section links to
     `project.md`'s Techstack `## Context` subsection.

   Do not add a Status field anywhere in this detail — status for
   every task lives exclusively in its table row (step 6), never
   duplicated into the inline block or task file.
5. Note dependencies on other tasks explicitly if they exist
   (`P01-T03 depends on P01-T02`, or `T03 depends on T02` at `lite`'s
   flat IDs) — this determines what can run in parallel. **If this
   task logically precedes tasks that already exist** (e.g. a replan
   inserts a foundational setup step after several tasks were already
   created), this new task's own Depends-on may be empty, but go back
   and add it to the Depends-on column of every existing task that now
   needs it done first in the owning table. Skipping this leaves the
   dependency graph wrong in exactly the way that makes "implement the
   first task" ambiguous later (see
   [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)) —
   ID order alone won't reflect the real sequence once this happens.
6. Update this task's row in the owning Tasks table — the phase file's
   at `full`/`medium`, `.ai/project.md`'s Roadmap table at `lite` —
   Status moves from `not-planned` to `awaiting-plan-review` now that
   its detail exists:

   ```
   | ID | Title | Purpose | Depends on | Status |
   |---|---|---|---|---|
   | P01-T01 | Scaffold Angular project | ... | — | awaiting-plan-review |
   | P01-T02 | Define domain types | ... | P01-T01 | awaiting-plan-review |
   | P01-T03 | Implement scoring engine | ... | P01-T02 | not-planned |
   ```

   (Example: T01–T02 were in scope this invocation and got fully
   drafted; T03 exists as a stub from step 1 but wasn't asked for yet.
   At `lite`, drop the `P01-` prefix from every ID.)
7. Update `.ai/info.md`'s Status section: set `Active task` to this
   task's ID. If multiple tasks are in scope this invocation, the
   Status section can only reflect one at a time (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-multi-agent--multi-human))
   — use the last one drafted, or the one most likely to be
   implemented next.

8. **Once every task in scope for this invocation is drafted**, commit
   everything together — the new stubs from step 1, the fully-drafted
   task detail (files or inline blocks, per profile), the owning
   table's updates, `.ai/info.md`, all of it
   (see [.ai/workflow/workflow.md §13](.ai/workflow/workflow.md#13-commit-discipline)).
   Stop for task plan review (`task-review` gate — this gate exists at
   every profile, §14) — see `.ai/info.md`
   (read fresh) — covering only the tasks actually drafted this
   invocation, not the stubs (nothing to review in a title-only row).
   **When approval comes back, that's a separate turn:** set Status to
   `plan-approved` in the owning table for every task that was
   approved — a partial approval (some tasks approved, others sent
   back) is fine; update each row according to its own outcome. In
   `manual`/`assisted` mode, report the approval and explicitly ask
   whether to proceed to implementation now, and wait for that answer
   as its own confirmation — don't begin implementing in the same
   response that reports the approval, even though `task-review`
   passing does technically authorize it (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).
   `workflow-implementation`'s own first step is what finally moves
   each task's Status to `in-progress`, once you actually start it.

## Output

At `full`: one `.ai/tasks/p{NN}-t{NN}-{name}.md` per task actually
drafted this invocation — never at the project root — not one for
every stub row. At `medium`/`lite`: no separate task files — an inline
block per drafted task, nested under its row in the owning table
instead.

The owning Tasks table — the phase file's at `full`/`medium`,
`.ai/project.md`'s Roadmap table at `lite` — updated with a row for
*every* remaining plan step (most at `not-planned` if this was the
first invocation), not just the ones drafted this time.

`.ai/info.md` updated. At `full`/`medium`: `.ai/constitution/roadmap.md`
also updated to reflect the phase moving to `in-progress` if this was
the first task planned. Not applicable at `lite` (no phase status).
