---
name: workflow-implementation
description: Use this skill to actually write, modify, or delete project code for a task that already has an approved context.md and implementation.md. Trigger this whenever the user wants to implement a task, write the code for a task, or execute an already-planned implementation step. Requires task planning to be done first — use workflow-task if implementation.md doesn't exist yet. Do not use this to plan what a task should do; only to carry out a plan that already exists.
---

# Skill: workflow.implementation

Operation for the **Implementation Agent**. Contract:
[../../agents.md#implementation-agent](../../agents.md#implementation-agent).

This is the most frequently invoked skill in the workflow — it runs once
per task, potentially many times per phase. Keep its context cost low;
see §1 below before reading anything else.

## 1. What to read (and what not to)

Do **not** reread the full [../../workflow.md](../../workflow.md) for a
routine implementation. Its rules are already compiled into this skill
and into `agents.md`. Read only:

1. The task's `context.md` and `implementation.md`.
2. [../../state.md](../../state.md) and [../../policy.md](../../policy.md)
   — cheap, and `policy.md` tells you whether task-validation/task-review
   are yours to self-certify or require a human.
3. Only the files `context.md` lists as relevant, plus whatever those
   files themselves reference and you actually end up touching. Don't
   pull in unrelated modules "for context."

Read the full `workflow.md` only if this skill doesn't cover a situation
you've hit (e.g. you're unsure whether something counts as a deviation).

## 2. Procedure

1. Read the task's `implementation.md`: objective, steps, files expected
   to change, dependencies, expected result, validation instructions.
2. Read the task's `context.md` and only the referenced files it names.
3. Implement the steps in order. Minor mismatches (a function living in
   a different file than expected) — just adjust and continue, no
   deviation needed.
4. If the plan turns out to be wrong in a way that changes scope, the
   library/API doesn't support what was planned, or the strategy has to
   change — stop and raise a deviation. See
   [../../deviations.md](../../deviations.md). Do not silently expand
   scope or improvise past what was approved.
5. If you make an architectural decision along the way (a new
   dependency, a new pattern) that future work needs to know about,
   document it — as a deviation if it wasn't planned, or flag it for an
   ADR (see [../../decisions/_template.md](../../decisions/_template.md))
   if it's a deliberate persistent choice.

## 3. Keep the project structure map accurate

**This is required, not optional, whenever your task creates, deletes,
or moves a file or directory.** `project-context/structure.md` exists
so agents can locate code without rediscovering the repo — if it goes
stale the moment you touch the file tree, every agent after you pays
for it.

Before finishing implementation:

- Created a file/directory the map doesn't show? Add it.
- Deleted one the map lists? Remove it.
- Moved/renamed one? Update its entry.

This happens as part of implementation itself — do not defer it to the
`workflow-context` task-completion step. Context evaluation is for
*knowledge* (why something changed); the structure map is a mechanical
fact and should never be out of date even for one task-cycle.

## 4. Finishing

1. Update the task's status per your project's convention.
2. Stop for `task-validation` — see [../../policy.md](../../policy.md)
   for whether that's yours to run (→
   [workflow-validation](../workflow-validation/SKILL.md)) or a human's.
3. Do not mark the task complete yourself — completion requires
   validation and review to pass first (see
   [../../lifecycle.md](../../lifecycle.md)).

## Output

Modified project files, an updated `project-context/structure.md` if the
file tree changed, and the task ready for validation.
