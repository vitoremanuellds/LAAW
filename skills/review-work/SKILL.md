---
name: review-work
description: Review a task's implementation and validation results for scope, complexity, architecture, missing validation, or context issues — at task-completion-review, after validation passes. Distinct from task-review (plan approval) and from validate-work (correctness). Never silently fix issues — report and stop for the gate.
---

# Skill: review-work

This skill performs the **review** operation — the second of the
completion-review gate's two internal checks (judgment, after
validation's mechanical check; see
[.ai/workflow/workflow.md §8](.ai/workflow/workflow.md#8-validation-vs-review)).

- **Can:** inspect everything, flag scope/requirement/complexity/
  architecture/validation/context issues and undocumented decisions,
  set Status `done`.
- **Must:** read `info.md` fresh before trusting a gate's authority;
  stop after reporting, even clean findings.
- **Should not:** silently fix issues.

Always use `tools/generate-id.py --prefix t` to generate IDs for any
project file that requires an ID. Never hardcode, guess, or manually
construct IDs — the script is the single source of truth for ID
generation across the entire project.

Always use `tools/generate-id.py --prefix c` to generate IDs for
context files.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for review.

**All `.ai/`-artifact paths below are relative to the project root,
not to this skill file — write the full `.ai/...` path.** Status
values you set here (`done`) are one of exactly four in a closed enum
— see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)
for the full list; never invent one not on it.

## When to use

After validation passes, before a task is marked `done` — this is the
"Review" step in the lifecycle (`Implement → Validate → Review →
Context Evaluation → Done`), a different moment from the `task-review`
gate (which approves the *plan*, before any implementation happens —
see [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)'s
naming note). Don't confuse the two just because both are called
"review." Distinct from validation too: see
[.ai/workflow/workflow.md §8](.ai/workflow/workflow.md#8-validation-vs-review).

## Inputs

- The task file, and the actual changes made.
- Tests and validation results (the task's Status in `.ai/tasks/tasks.md`).
- Relevant `.ai/context/` files (context rows).

## Procedure

1. Read `.ai/info.md` fresh — confirms `task-completion-review`
   authority; don't rely on a read from earlier in the session. Set
   Status to `done` — in `.ai/tasks/tasks.md`.
2. Confirm the change matches its stated scope — flag anything done
   that wasn't in the plan (scope violation) or required but missing
   (requirement mismatch).
3. Check for unnecessary complexity relative to the stated objective.
4. Check consistency with existing architecture and relevant
   context rows from `context/`.
5. Check that validation coverage actually matches what the
   requirements call for — flag missing validation.
6. Check that context files (`.ai/context/context.md` and its listed
   files) still accurately describe the result — flag context
   inconsistencies for the context skill to fix.
7. Check for undocumented decisions — an architectural choice with no
   corresponding context row. Flag it back to whichever operation
   produced it (ownership rule: see
   [.ai/workflow/workflow.md §7](.ai/workflow/workflow.md#7-decisions-adrs))
   — do not write the decision row yourself.
8. Report findings — approve, or changes requested. Do not silently
   fix issues yourself unless your entry in `.ai/info.md` explicitly
   grants implementation authority.
9. Commit: stage the Status change in `tasks.md` from step 1, plus
   any context files you touched while flagging; the message should
   say what was reviewed and the verdict (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline));
   exclude any gitignored files — gitignored layers simply have nothing
   to commit, not a violation of commit discipline.
   Stop for `task-completion-review` — see `.ai/info.md`.
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
against the checks above. If approved: the task left at Status `done`
in `tasks.md`, ready for `propagate-context` to mark it complete —
review itself never sets Status to `complete`.
