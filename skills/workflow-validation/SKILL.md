---
name: workflow-validation
description: Use this skill to run task-level or phase-level validation after implementation is complete, before review. Trigger this whenever the user wants to check whether a task or phase satisfies its stated requirements, run the validation instructions from a task.md or phase.md, or report pass/fail results against acceptance criteria. Do not use this to fix failing code — validation only reports failures; fixes return to the implementation loop. Do not use this for code-quality or architectural review; see workflow-review for that.
---

# Skill: workflow.validation

Operation for the **Validation Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

After implementation, before review — at task level (`task-validation`
gate) or phase level (`phase-validation` gate). See
[../../../policy.md](../../../policy.md) for who holds each gate.

## Inputs

- Task: `task.md`'s Implementation section (validation instructions).
- Phase: `phase.md`'s Validations section and all task results in the phase.

## Procedure — task validation

1. Set the task's Status to `validating` in the phase's `tasks/index.md` if not
   already set.
2. Read `task.md`'s Implementation section (requirements + plan).
3. Execute the validation instructions (automated tests, integration
   checks).
4. Report pass/fail. On failure, do **not** edit implementation to
   force a pass — set Status back to `in-progress` and return the task
   to the implementation loop (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)).
5. Record any accepted exceptions explicitly rather than silently
   ignoring a failure.

## Procedure — phase validation

1. Set the phase's Status to `validating` in
   `../../../constitution/roadmap.md` if not already set.
2. Read `phase.md`'s Validations section and every task's result in
   the phase (`tasks/index.md`).
3. Check cross-task/integration behavior and phase acceptance criteria.
4. Report pass/fail per validation item, not just an overall verdict.
   On failure, set Status back to `in-progress` rather than leaving it
   at `validating`.

## Output

Pass/fail result recorded against the task (in `task.md` or
`tasks/index.md`, per project convention) or phase (`phase.md`) — not
a separate permanent log file.
