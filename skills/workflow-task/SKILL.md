---
name: workflow-task
description: Use this skill to break a phase's phase.md plan section into individual tasks (task.md under .ai/phases/*/tasks/), or to replan a single task after a task-level deviation. Trigger this whenever the user wants to define the next unit of implementable work, assign a task ID, or specify what files a task touches and how it will be validated. On first use for a phase, stubs a tasks/index.md row (not-planned) for every remaining plan step, then fully drafts whichever task(s) were actually asked for — one, several, or all, depending on what's requested; it is not limited to one task per invocation. Requires an approved phase plan to already exist — use workflow-phase first if it doesn't. Do not use this to actually implement the task's code.
---

# Skill: workflow.task

Operation for the **Task Planning Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

Breaking a phase's plan into individual tasks, or replanning one task
after a task-level deviation. **Scope is whatever was actually asked**
— "plan the first task" means exactly one; "plan the tasks for this
phase" or "break down the whole plan" means all remaining steps from
`phase.md`'s Plan section in one pass. If the request is ambiguous
about scope, ask rather than defaulting silently to one or to all.

## Inputs

- The phase's `phase.md` (Requirements + Plan sections) and `context.md`.
- Only the project-context modules and files this specific task touches.

## Procedure

Steps 1–6 require no prior approval — draft everything for this
invocation before stopping for anything. Only step 7 is gated, and
it's a single stop for the whole batch, not one per task — don't make
the human approve four tasks one at a time when they asked for all
four together.

1. **If this is the first time any task has been planned for this
   phase**, or `tasks/index.md` doesn't yet have a row for every step
   in `phase.md`'s Plan section: create `tasks/index.md` (if it doesn't
   exist) and add a row for *every remaining* plan step, not just the
   ones in scope this invocation — ID assigned, Title from the plan
   step, Status `not-planned`, no `task.md` yet for any of them. This
   is cheap (titles only, not full plans) and is what gives full
   visibility into the phase's task list immediately, rather than only
   after every task has been individually drafted. Skip this step
   entirely if the index already has a row for every plan step.

**Then, repeat steps 2–6 for each task actually in scope this
invocation** (see "When to use" above for how scope is determined):

2. Read the plan section step this task corresponds to. If the phase's
   Status in `../../../constitution/roadmap.md` is still
   `plan-approved`, set it to `in-progress` — task planning starting is
   the actual signal that work has begun; nothing else sets this
   transition. (If it's still `awaiting-plan-review`, phase-review
   hasn't actually passed yet — stop and check before proceeding;
   don't treat being asked to plan tasks as itself implying approval
   happened.)
3. If this task doesn't already have an ID from step 1's stubbing,
   assign the next sequential one (`P{NN}-T{NN}`) — never reuse or
   renumber. Name the directory `p{NN}-t{NN}-{kebab-name}/`.
4. Write `task.md` with two sections:
   - **Context** — task-specific only. Do not copy phase context; have
     `task.md` link to it as `../../context.md` (relative to the task's
     own directory, two levels up to the phase). Relevant files,
     relevant constraints.
   - **Implementation** — objective, relevant requirements,
     implementation steps, files expected to change, dependencies,
     expected result, validation instructions.
5. Note dependencies on other tasks explicitly if they exist
   (`P01-T03 depends on P01-T02`) — this determines what can run in
   parallel. **If this task logically precedes tasks that already
   exist** (e.g. a replan inserts a foundational setup step after
   `P01-T01`–`P01-T04` were already created), this new task's own
   Depends-on may be empty, but go back and add it to the Depends-on
   column of every existing task that now needs it done first. Skipping
   this leaves the dependency graph wrong in exactly the way that makes
   "implement the first task" ambiguous later (see
   [../../workflow.md §11](../../workflow.md#11-status-vocabulary-indexes-not-a-state-file)) —
   ID order alone won't reflect the real sequence once this happens.
6. Update this task's row in `tasks/index.md` — Status moves from
   `not-planned` to `awaiting-plan-review` now that `task.md` exists:

   ```
   | ID | Title | Purpose | Depends on | Status |
   |---|---|---|---|---|
   | P01-T01 | Scaffold Angular project | ... | — | awaiting-plan-review |
   | P01-T02 | Define domain types | ... | P01-T01 | awaiting-plan-review |
   | P01-T03 | Implement scoring engine | ... | P01-T02 | not-planned |
   | P01-T04 | Persist to local storage | ... | P01-T02 | not-planned |
   ```

   (Example: T01–T02 were in scope this invocation and got fully
   drafted; T03–T04 exist as stubs from step 1 but weren't asked for
   yet.) See
   [../../workflow.md §11](../../workflow.md#11-status-vocabulary-indexes-not-a-state-file)
   for the full enum — every agent that touches a task updates its row
   as it moves through the lifecycle.
7. **Once every task in scope for this invocation is drafted**, commit
   everything together — the new stubs from step 1, the fully-drafted
   tasks, all of it (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)). Stop for
   task plan review (`task-review` gate) — see
   [../../../policy.md](../../../policy.md) — covering only the tasks
   actually drafted this invocation, not the stubs (nothing to review
   in a title-only row). **When approval comes back, that's a separate
   turn:** set Status to `plan-approved` in `tasks/index.md` for every
   task that was approved (a partial approval — some tasks approved,
   others sent back — is fine; update each row according to its own
   outcome). In `manual`/`assisted` mode, report the approval and
   explicitly ask whether to proceed to implementation now, and wait
   for that answer as its own confirmation — don't begin implementing
   in the same response that reports the approval, even though
   `task-review` passing does technically authorize it (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)).
   `workflow-implementation`'s own first step is what finally moves
   each task's Status to `in-progress`, once you actually start it.

## Output

One `task.md` per task actually drafted this invocation, at
`phases/p{NN}-.../tasks/p{NN}-t{NN}-{name}/task.md` — not one for every
row in the index.
`phases/p{NN}-.../tasks/index.md` — created or updated with a row for
*every* remaining plan step (most at `not-planned` if this was the
first invocation for the phase), not just the ones drafted this time.
`constitution/roadmap.md` — Status updated if this was the first task
planned for the phase.
