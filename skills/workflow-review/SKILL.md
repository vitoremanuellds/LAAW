---
name: workflow-review
description: Use this skill to review a task or phase's plan, implementation, and validation results for scope violations, requirement mismatches, unnecessary complexity, architectural inconsistencies, missing validation, or context inconsistencies. Trigger this at a task-review or phase-review gate, after validation has passed. This is distinct from workflow-validation — validation checks correctness against requirements, review checks whether the work is appropriate, coherent, and consistent with project direction. Do not use this to silently fix issues found; report them instead unless the execution policy explicitly grants implementation authority.
---

# Skill: workflow.review

Operation for the **Review Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

At the `task-review` or `phase-review` gate — after validation passes,
before the task/phase is marked complete. Distinct from validation: see
[../../workflow.md §8](../../workflow.md#8-validation-vs-review).

## Inputs

- `task.md` or `phase.md`, and the actual changes made.
- Tests and validation results (`tasks/index.md` Status, `phase.md`
  Validations section).
- Relevant context files and ADRs.

## Procedure

1. Set the task's Status to `reviewing` in the phase's `tasks/index.md` if
   applicable (task-level review only; phase-level review has no
   per-task status to set).
2. Confirm the change matches its stated scope — flag anything done
   that wasn't in the plan (scope violation) or required but missing
   (requirement mismatch).
3. Check for unnecessary complexity relative to the stated objective.
4. Check consistency with existing architecture and any relevant ADRs
   in [../../../decisions/](../../../decisions/).
5. Check that validation coverage actually matches what the
   requirements call for — flag missing validation.
6. Check that context files (task/phase) still accurately describe the
   result — flag context inconsistencies for the context skill to fix.
7. Check for undocumented decisions — an architectural choice with no
   corresponding ADR. Flag it back to the agent whose scope produced
   it (see [../../workflow.md §10](../../workflow.md#10-agent-contracts)) —
   do not write the ADR yourself.
8. Report findings. Do not silently fix issues yourself unless your
   entry in [../../../policy.md](../../../policy.md) explicitly grants
   implementation authority.

## Output

A review verdict (approve / changes requested) with findings listed
against the checks above.
