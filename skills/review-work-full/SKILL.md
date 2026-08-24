---
name: review-work-full
description: Full-profile skill to review a task or phase's implementation and validation results for scope, complexity, architecture, missing validation, or context issues — at task-completion-review/phase-completion-review, after validation passes. Distinct from task-review/phase-review (plan approval) and from validate-work-full (correctness). Never silently fix issues — report and stop for the gate.
---

# Skill: review-work-full

Operation for the **Review Agent**. Contract:
[.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts).

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for review.

**All `.ai/`-artifact paths below are relative to the project root,
not to this skill file — write the full `.ai/...` path.** Status
values you set here (`reviewing`, `complete`) are two of exactly eight
in a closed enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)
for the full list; never invent one not on it.

## When to use

After validation passes, before a task or phase is marked complete —
this is the "Review" step in the lifecycle
(`Implement → Validate → Review → Context Evaluation → Complete`), a
different moment from the `task-review`/`phase-review` gates (which
approve the *plan*, before any implementation happens — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)'s
naming note). Don't confuse the two just because both are called
"review." Distinct from validation too: see
[.ai/workflow/workflow.md §8](.ai/workflow/workflow.md#8-validation-vs-review).

## Inputs

- The task file or phase file, and the actual changes made.
- Tests and validation results (the task's Status in its owning phase
  file's Tasks table; the phase file's Validations section).
- Relevant `.ai/context/` files and ADRs.

## Procedure

1. Read `.ai/info.md` fresh — confirms `task-completion-review`/
   `phase-completion-review` authority; don't rely on a read from
   earlier in the session. Set Status to `reviewing` — in the task's
   row in its owning phase file's Tasks table for a task-level review,
   or the phase's row in `.ai/constitution/roadmap.md` for a
   phase-level review. `.ai/info.md`'s Active task/phase pointer
   should already name this item — leave it as the ID only; the status
   word belongs in the phase file's table or `roadmap.md`, never in
   `info.md` (§11).
2. Confirm the change matches its stated scope — flag anything done
   that wasn't in the plan (scope violation) or required but missing
   (requirement mismatch).
3. Check for unnecessary complexity relative to the stated objective.
4. Check consistency with existing architecture and any relevant ADRs
   in `.ai/decisions/`.
5. Check that validation coverage actually matches what the
   requirements call for — flag missing validation.
6. Check that context files (`.ai/context/context.md` and its listed
   files, the phase file's own Context section) still accurately
   describe the result — flag context inconsistencies for the context
   skill to fix.
7. Check for undocumented decisions — an architectural choice with no
   corresponding ADR. Flag it back to the agent whose scope produced
   it (see [.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts)) —
   do not write the ADR yourself.
8. Report findings — approve, or changes requested. Do not silently
   fix issues yourself unless your entry in `.ai/info.md` explicitly
   grants implementation authority.
9. Commit if you made any changes to context/ADR files as part of
   flagging (see
   [.ai/workflow/workflow.md §13](.ai/workflow/workflow.md#13-commit-discipline)).
   Stop for `task-completion-review` (task-level) or
   `phase-completion-review` (phase-level) — see `.ai/info.md`.
   **Clean findings are not themselves approval** — even if you found
   nothing wrong, stop and wait for an explicit yes before anything
   gets marked complete; don't treat "I approve of what I found" as
   the same thing as the human's sign-off (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)). If
   changes were requested instead, return to the implementation loop —
   there's nothing to stop for until it comes back for review again.
10. **When approval comes back, that's a separate turn:** in
    `manual`/`assisted` mode, report the approval and explicitly ask
    whether to run `propagate-context` now to finalize completion,
    rather than starting it in the same response.

## Output

A review verdict (approve / changes requested) with findings listed
against the checks above. If approved: the task/phase left at Status
`reviewing` in the relevant table (`.ai/info.md`'s pointer is
unaffected — see §11), ready for `propagate-context` to mark it
`complete` — review itself never sets Status to `complete`.
