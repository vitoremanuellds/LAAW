---
name: workflow-task
description: Use this skill to break a phase's phase.md plan section into individual tasks (task.md under .ai/phases/*/tasks/), or to replan a single task after a task-level deviation. Trigger this whenever the user wants to define the next unit of implementable work, assign a task ID, or specify what files a task touches and how it will be validated. Requires an approved phase plan to already exist — use workflow-phase first if it doesn't. Do not use this to actually implement the task's code.
---

# Skill: workflow.task

Operation for the **Task Planning Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

Breaking a phase's plan into individual tasks, or replanning one task
after a task-level deviation.

## Inputs

- The phase's `phase.md` (Requirements + Plan sections) and `context.md`.
- Only the project-context modules and files this specific task touches.

## Procedure

Steps 1–5 require no prior approval — draft the task fully before
stopping for anything. Only step 6 is gated.

1. Read the plan section step this task corresponds to. If the phase's
   Status in `../../../constitution/roadmap.md` is still
   `plan-approved`, set it to `in-progress` — task planning starting is
   the actual signal that work has begun; nothing else sets this
   transition. (If it's still `awaiting-plan-review`, phase-review
   hasn't actually passed yet — stop and check before proceeding;
   don't treat being asked to plan tasks as itself implying approval
   happened.)
2. Assign the next sequential ID (`P{NN}-T{NN}`) — never reuse or
   renumber. Name the directory `p{NN}-t{NN}-{kebab-name}/`.
3. Write `task.md` with two sections:
   - **Context** — task-specific only. Do not copy phase context; have
     `task.md` link to it as `../../context.md` (relative to the task's
     own directory, two levels up to the phase). Relevant files,
     relevant constraints.
   - **Implementation** — objective, relevant requirements,
     implementation steps, files expected to change, dependencies,
     expected result, validation instructions.
4. Note dependencies on other tasks explicitly if they exist
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
5. Create or update `tasks/index.md` in the same `tasks/` folder — add
   a row for this task:

   ```
   | ID | Title | Purpose | Depends on | Status |
   |---|---|---|---|---|
   | P01-T03 | Refresh token rotation | ... | P01-T02 | awaiting-plan-review |
   ```

   Status starts at `awaiting-plan-review` — by the time this row
   exists, `task.md` is already drafted (step 3), so there's no
   meaningful `not-planned` moment for a task the way there is for a
   phase in `roadmap.md`. See
   [../../workflow.md §11](../../workflow.md#11-status-vocabulary-indexes-not-a-state-file)
   for the full enum — every agent that touches this task updates its
   row as it moves through the lifecycle.
6. Commit the draft (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)). Stop for
   task plan review (`task-review` gate) — see
   [../../../policy.md](../../../policy.md). **When
   approval comes back, that's a separate turn:** set Status to
   `plan-approved` in `tasks/index.md`. In `manual`/`assisted` mode,
   report the approval and explicitly ask whether to proceed to
   implementation now, and wait for that answer as its own
   confirmation — don't begin implementing in the same response that
   reports the approval, even though `task-review` passing does
   technically authorize it (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)).
   `workflow-implementation`'s own first step is what finally moves
   Status to `in-progress`, once you actually start.

## Output

`phases/p{NN}-.../tasks/p{NN}-t{NN}-{name}/task.md`
`phases/p{NN}-.../tasks/index.md` (created or updated)
`constitution/roadmap.md` — Status updated if this was the first task
planned for the phase.
