---
name: workflow-review
description: Use this skill to review a task or phase's implementation and validation results for scope violations, requirement mismatches, unnecessary complexity, architectural inconsistencies, missing validation, or context inconsistencies. Trigger this at the task-completion-review or phase-completion-review gate, after validation has passed — not the same as task-review/phase-review, which approve the plan before implementation. Distinct from workflow-validation — validation checks correctness against requirements, review checks whether the work is appropriate, coherent, and consistent with project direction. Do not use this to silently fix issues found; report them and stop for the completion-review gate, same as any other gate.
---

# Skill: workflow.review

Operation for the **Review Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

After validation passes, before a task or phase is marked complete —
this is the "Review" step in the lifecycle
(`Implement → Validate → Review → Context Evaluation → Complete`), a
different moment from the `task-review`/`phase-review` gates (which
approve the *plan*, before any implementation happens — see
[../../workflow.md §11](../../workflow.md#11-status-the-fast-pointer-and-the-permanent-record)'s
naming note). Don't confuse the two just because both are called
"review." Distinct from validation too: see
[../../workflow.md §8](../../workflow.md#8-validation-vs-review).

## Inputs

- The task file or phase file, and the actual changes made.
- Tests and validation results (the task's Status in its owning phase
  file's Tasks table; the phase file's Validations section).
- Relevant `context/` files and ADRs.

## Procedure

1. Read [../../../info.md](../../../info.md) fresh — confirms
   `task-completion-review`/`phase-completion-review` authority; don't
   rely on a read from earlier in the session. Set Status to
   `reviewing` — in the task's row in its owning phase file's Tasks
   table for a task-level review, or the phase's row in
   `../../../constitution/roadmap.md` for a phase-level review. Update
   `info.md`'s Status section to match.
2. Confirm the change matches its stated scope — flag anything done
   that wasn't in the plan (scope violation) or required but missing
   (requirement mismatch).
3. Check for unnecessary complexity relative to the stated objective.
4. Check consistency with existing architecture and any relevant ADRs
   in [../../../decisions/](../../../decisions/).
5. Check that validation coverage actually matches what the
   requirements call for — flag missing validation.
6. Check that context files (`context/context.md` and its listed
   files, the phase file's own Context section) still accurately
   describe the result — flag context inconsistencies for the context
   skill to fix.
7. Check for undocumented decisions — an architectural choice with no
   corresponding ADR. Flag it back to the agent whose scope produced
   it (see [../../workflow.md §10](../../workflow.md#10-agent-contracts)) —
   do not write the ADR yourself.
8. Report findings — approve, or changes requested. Do not silently
   fix issues yourself unless your entry in
   [../../../info.md](../../../info.md) explicitly grants
   implementation authority.
9. Commit if you made any changes to context/ADR files as part of
   flagging (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)).
   Stop for `task-completion-review` (task-level) or
   `phase-completion-review` (phase-level) — see
   [../../../info.md](../../../info.md). **Clean findings are not
   themselves approval** — even if you found nothing wrong, stop and
   wait for an explicit yes before anything gets marked complete; don't
   treat "I approve of what I found" as the same thing as the human's
   sign-off (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)). If
   changes were requested instead, return to the implementation loop —
   there's nothing to stop for until it comes back for review again.
10. **When approval comes back, that's a separate turn:** in
    `manual`/`assisted` mode, report the approval and explicitly ask
    whether to run `workflow-context` now to finalize completion,
    rather than starting it in the same response.

## Output

A review verdict (approve / changes requested) with findings listed
against the checks above. If approved: the task/phase left at Status
`reviewing` in the relevant table and `info.md`, ready for
`workflow-context` to mark it `complete` — review itself never sets
Status to `complete`.
