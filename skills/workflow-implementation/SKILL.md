---
name: workflow-implementation
description: Use this skill to actually write, modify, or delete project code for a task that already has an approved task file under tasks/. Trigger this whenever the user wants to implement a task, write the code for a task, or execute an already-planned implementation step. Requires task planning to be done first — use workflow-task if the task file doesn't exist yet. Do not use this to plan what a task should do; only to carry out a plan that already exists.
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

1. [../../../info.md](../../../info.md) — read fresh, not from earlier
   in the session; confirms this is genuinely the active task and
   tells you whether `task-validation`/`task-review` are yours to
   self-certify.
2. The task's file (`tasks/p{NN}-t{NN}-{name}.md`, Context +
   Implementation sections — including its Files to modify/create,
   Steps, and any Pseudocode).
3. Only the files the task's Context section lists as relevant, plus
   whatever those reference and you actually end up touching. Don't
   pull in unrelated modules "for context."
4. Explore the actual codebase with `tree`/`find`/`grep`/`ls` directly
   when you need to locate something — there's no structure map to
   consult or keep in sync; the filesystem is the source of truth.

Read the full `workflow.md` only if this skill doesn't cover a
situation you've hit (e.g. unsure whether something counts as a
deviation).

## 2. Procedure

1. Read the task file's Implementation section in full: objective,
   files to modify, files to create, ordered steps, pseudocode if
   present, dependencies, expected result, validation instructions.
2. Read the Context section and only the referenced files it names.
3. Check the task's current Status in its owning phase file's Tasks
   table (the task file itself never tracks its own status — that
   table is the only place it lives). It should be `plan-approved` —
   if it's still `awaiting-plan-review`, task-review hasn't actually
   passed yet; stop and check before proceeding rather than assuming
   being asked to implement implies approval happened. Once confirmed,
   set Status to `in-progress` there, and update `info.md`'s Status
   section to match.
4. Follow the task's Files-to-modify/Files-to-create and Steps in
   order. If Pseudocode is present, treat it as guidance for the
   approach, not a literal script — adapt it to what you actually find
   in the codebase. Minor mismatches (a function living in a different
   file than expected, or an implementation detail that differs from
   the pseudocode's specifics) — adjust and continue, no deviation
   needed; see [../../workflow.md §6](../../workflow.md#6-deviations).
5. If the plan turns out wrong in a way that changes scope, the
   library/API doesn't support what was planned, or the strategy
   itself has to change — stop and raise a deviation. Do not silently
   expand scope or improvise past what was approved.
6. If you make an architectural decision along the way (a new
   dependency, a new pattern) that future work needs to know about,
   this is yours to document — you don't escalate it. Check
   [../../../decisions/decisions.md](../../../decisions/decisions.md)
   first; a related decision may already exist. If not, write the ADR
   from
   [../../templates/adr-template.md](../../templates/adr-template.md)
   and add its row to the index in the same step.

## 3. Finishing

1. Set the task's Status to `validating` (or `blocked` if stuck) in
   its owning phase file's Tasks table, and update `info.md` to match.
   These two are the only places task status lives — nothing else
   needs updating.
2. Commit (see [../../workflow.md §13](../../workflow.md#13-commit-discipline)).
   Stop for `task-validation` — see [../../../info.md](../../../info.md)
   (read fresh) for whether that's yours to run (→
   [workflow-validation](../workflow-validation/SKILL.md)) or a human's.
3. Do not mark the task complete yourself — completion requires
   validation and review to pass first (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)).

## Output

Modified project files; an updated row in the owning phase file's
Tasks table; `info.md` updated; a new ADR and
`decisions/decisions.md` row if an architectural decision was made;
the task ready for validation.
