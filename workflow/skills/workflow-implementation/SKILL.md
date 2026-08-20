---
name: workflow-implementation
description: Use this skill to actually write, modify, or delete project code for a task that already has an approved task.md. Trigger this whenever the user wants to implement a task, write the code for a task, or execute an already-planned implementation step. Requires task planning to be done first — use workflow-task if task.md doesn't exist yet. Do not use this to plan what a task should do; only to carry out a plan that already exists.
---

# Skill: workflow.implementation

Operation for the **Implementation Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

This is the most frequently invoked skill in the workflow — it runs
once per task, potentially many times per phase. Keep its context cost
low; see §1 below before reading anything else.

## 1. What to read (and what not to)

Do **not** reread the full [../../workflow.md](../../workflow.md) for a
routine implementation — its rules are already compiled into this
skill. Read only:

1. The task's `task.md` (Context + Implementation sections).
2. [../../../policy.md](../../../policy.md) — cheap, tells you whether
   task-validation/task-review are yours to self-certify or require a
   human.
3. Only the files `task.md`'s Context section lists as relevant, plus
   whatever those reference and you actually end up touching. Don't
   pull in unrelated modules "for context."
4. Explore the actual codebase with `tree`/`find`/`grep`/`ls` directly
   when you need to locate something — there's no structure map to
   consult or keep in sync; the filesystem is the source of truth.

Read the full `workflow.md` only if this skill doesn't cover a
situation you've hit (e.g. unsure whether something counts as a
deviation).

## 2. Procedure

1. Read `task.md`'s Implementation section: objective, steps, files
   expected to change, dependencies, expected result, validation
   instructions.
2. Read the Context section and only the referenced files it names.
3. Set the task's Status to `in-progress` in the phase's `tasks/index.md`.
4. Implement the steps in order. Minor mismatches (a function living
   in a different file than expected) — adjust and continue, no
   deviation needed.
5. If the plan turns out wrong in a way that changes scope, the
   library/API doesn't support what was planned, or the strategy has
   to change — stop and raise a deviation. See
   [../../workflow.md §6](../../workflow.md#6-deviations). Do not silently
   expand scope or improvise past what was approved.
6. If you make an architectural decision along the way (a new
   dependency, a new pattern) that future work needs to know about,
   this is yours to document — you don't escalate it. Check
   [../../../decisions/index.md](../../../decisions/index.md) first; a
   related decision may already exist. If not, write the ADR from
   [../../decision-template.md](../../decision-template.md) and add its
   row to the index in the same step.

## 3. Finishing

1. Set the task's Status to `validating` (or `blocked` if stuck) in
   the phase's `tasks/index.md`. The index is the only place task status lives
   — nothing else needs updating to match it.
2. Commit (see [../../workflow.md §13](../../workflow.md#13-commit-discipline)).
   Stop for `task-validation` — see [../../../policy.md](../../../policy.md)
   for whether that's yours to run (→
   [workflow-validation](../workflow-validation/SKILL.md)) or a human's.
3. Do not mark the task complete yourself — completion requires
   validation and review to pass first (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)).

## Output

Modified project files; an updated `tasks/index.md` row; a new ADR and
`decisions/index.md` row if an architectural decision was made; the
task ready for validation.
