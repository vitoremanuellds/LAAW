---
name: workflow-validation
description: Use this skill to run task-level or phase-level validation after implementation is complete, before review. Trigger this whenever the user wants to check whether a task or phase satisfies its stated requirements, run the validation instructions from an implementation.md or validations.md, or report pass/fail results against acceptance criteria. Do not use this to fix failing code — validation only reports failures; fixes return to the implementation loop. Do not use this for code-quality or architectural review; see workflow-review for that.
---

# Skill: workflow.validation

Operation for the **Validation Agent**. Contract:
[../../agents.md#validation-agent](../../agents.md#validation-agent).

## When to use

After implementation, before review — at task level (`task-validation`
gate) or phase level (`phase-validation` gate). See
[../../policy.md](../../policy.md) for who holds each gate.

## Inputs

- Task: `implementation.md`'s validation instructions.
- Phase: `validations.md` and all task validation results in the phase.

## Procedure — task validation

1. Read the task's requirements and implementation plan.
2. Execute the validation instructions in `implementation.md`
   (automated tests, integration checks).
3. Report pass/fail. On failure, do **not** edit implementation to force
   a pass — return the task to the implementation loop (see
   [../../lifecycle.md](../../lifecycle.md)).
4. Record any accepted exceptions explicitly rather than silently
   ignoring a failure.

## Procedure — phase validation

1. Read `validations.md` and every task's validation result in the
   phase.
2. Check cross-task/integration behavior and phase acceptance criteria.
3. Report pass/fail per validation item, not just an overall verdict.

## Output

Pass/fail result recorded against the task or phase (per project
convention — e.g. appended to `implementation.md` or `validations.md`,
not a separate permanent log file).
