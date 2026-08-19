---
name: workflow-task
description: Use this skill to break a phase's plan.md into individual tasks (context.md and implementation.md under .ai/phases/*/tasks/), or to replan a single task after a task-level deviation. Trigger this whenever the user wants to define the next unit of implementable work, assign a task ID, or specify what files a task touches and how it will be validated. Requires an approved phase plan to already exist — use workflow-phase first if it doesn't. Do not use this to actually implement the task's code.
---

# Skill: workflow.task

Operation for the **Task Planning Agent**. Contract:
[../../agents.md#task-planning-agent](../../agents.md#task-planning-agent).

## When to use

Breaking a phase's `plan.md` into individual tasks, or replanning one
task after a task-level deviation.

## Inputs

- Phase [plan.md](../../phases/) and [requirements.md](../../phases/)
  for the phase this task belongs to.
- Only the project-context modules and files this specific task touches.

## Procedure

Steps 1–6 require no prior approval — draft the task fully before
stopping for anything. Only step 7 is gated.

1. Read the phase plan step this task corresponds to.
2. Write `context.md` — task-specific only. Do not copy phase context;
   link to it. Include: relevant files, relevant constraints, links to
   phase/project context. See the example in
   [../../workflow.md §19-equivalent](../../workflow.md).
3. Write `implementation.md` — objective, relevant requirements,
   implementation steps, files expected to change, dependencies,
   expected result, validation instructions.
4. Assign the next sequential ID (`P{NN}-T{NN}`) — never reuse or
   renumber. Name the directory `p{NN}-t{NN}-{kebab-name}/`.
5. Note dependencies on other tasks explicitly if they exist
   (`P01-T03 depends on P01-T02`) — this determines what can run in
   parallel.
6. Create or update `tasks/index.md` in the same `tasks/` folder — add a
   row for this task. Format:

   ```
   | ID | Title | Purpose | Depends on | Status |
   |---|---|---|---|---|
   | P01-T03 | Refresh token rotation | ... | P01-T02 | planned |
   ```

   Status starts at `planned`; the Implementation Agent updates it from
   there (see [workflow-implementation §4](../workflow-implementation/SKILL.md#4-finishing)).
7. Stop for task review — see [../../policy.md](../../policy.md).

## Output

`phases/p{NN}-.../tasks/p{NN}-t{NN}-{name}/{context,implementation}.md`
`phases/p{NN}-.../tasks/index.md` (created or updated)
