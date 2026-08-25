---
name: review-work-medium
description: Medium-profile skill to review a task's implementation and validation results for scope, complexity, architecture, missing validation, or context issues at task-completion-review, then — once approved — propagate context and mark the task complete. Combines what the full profile splits across review-work-full and propagate-context, since there's no phase layer here to justify a separate context-propagation gate. Never silently fix issues — report and stop for the gate.
---

# Skill: review-work-medium

Operation for the **Review Agent**. Contract:
[.ai/workflow/workflow-medium.md §10](.ai/workflow/workflow-medium.md#10-agent-contracts).
Two parts — the review itself (gated), and finalization (only after
approval, a separate turn).

Read [.ai/workflow/workflow-medium.md](.ai/workflow/workflow-medium.md)
in full, same as every other medium-profile skill — do not skip it for
review.

**All `.ai/`-artifact paths below are relative to the project root, not
to this skill file — write the full `.ai/...` path.** Status values you
set here (`reviewing`, `complete`) are two of exactly eight in a closed
enum — see
[.ai/workflow/workflow-medium.md §11](.ai/workflow/workflow-medium.md#11-status-the-fast-pointer-and-the-permanent-record)
for the full list; never invent one not on it.

## When to use

After validation passes, before a task is marked complete — this is
the "Review" step in the lifecycle
(`Implement → Validate → Review → Task Complete`), a different moment
from the `task-review` gate (which approves the *plan*, before any
implementation happens). Distinct from validation too: see
[.ai/workflow/workflow-medium.md §8](.ai/workflow/workflow-medium.md#8-validation-vs-review).

## Inputs

- The task file, and the actual changes made.
- The task's Status in `.ai/constitution/roadmap.md`.
- `.ai/context/context.md` and relevant ADRs.

## Part 1 — Review (gated)

1. Read `.ai/info.md` fresh — confirms `task-completion-review`
   authority; don't rely on a read from earlier in the session. Set
   Status to `reviewing` in the task's row in `.ai/constitution/
   roadmap.md`. `.ai/info.md`'s Active task pointer should already
   name this task — leave it as the ID only; the status word belongs
   in `roadmap.md`, never in `info.md` (§11).
2. Confirm the change matches its stated scope — flag anything done
   that wasn't in the plan or required but missing.
3. Check for unnecessary complexity relative to the stated objective.
4. Check consistency with existing architecture and any relevant ADRs
   in `.ai/decisions/`.
5. Check that validation coverage actually matches what the
   requirements call for — flag missing validation.
6. Check for undocumented decisions — an architectural choice with no
   corresponding ADR. Flag it back to the agent whose scope produced
   it — do not write the ADR yourself.
7. Report findings — approve, or changes requested. Do not silently
   fix issues yourself unless your entry in `.ai/info.md` explicitly
   grants implementation authority.
8. Commit if you made any changes while flagging (see
   [.ai/workflow/workflow-medium.md §13](.ai/workflow/workflow-medium.md#13-commit-discipline)).
   Stop for `task-completion-review`. **Clean findings are not
   themselves approval** — even if you found nothing wrong, stop and
   wait for an explicit yes before anything gets marked complete. If
   changes were requested instead, return to the implementation loop —
   there's nothing to stop for until it comes back for review again.

## Part 2 — Finalization (only once `task-completion-review` is approved)

**Precondition:** the task's Status must already be `reviewing` with
an approved `task-completion-review` from Part 1 above — this doesn't
substitute for that approval, it finalizes it. **This is a separate
turn** from reporting the approval — don't chain straight into it in
`manual`/`assisted` mode; report the approval and ask first.

1. Inspect what the task actually produced.
2. Ask: does anything discovered here matter beyond this task? If not,
   skip to step 4.
3. If yes, update `.ai/context/context.md` with the persistent fact
   (not the task's history or reasoning) — see
   [.ai/workflow/workflow-medium.md §9](.ai/workflow/workflow-medium.md#9-context-propagation).
   Update its row in `.ai/context/context.md`'s own entry table in the
   same step.
4. Set the task's Status to `complete` in `.ai/constitution/
   roadmap.md` — this is the actual "task complete" marker. Clear
   `Active task` in `.ai/info.md`'s Status section.
5. Commit (see
   [.ai/workflow/workflow-medium.md §13](.ai/workflow/workflow-medium.md#13-commit-discipline)).

## Never propagate

Task history, temporary implementation details, information already
recorded elsewhere, internal reasoning, progress reports.

## Output

Part 1: a review verdict (approve / changes requested) with findings.
If approved: the task left at Status `reviewing`, ready for
finalization. Part 2: `.ai/context/context.md` updated if applicable;
the task's Status set to `complete` in `.ai/constitution/roadmap.md`;
`.ai/info.md`'s Status section cleared.
