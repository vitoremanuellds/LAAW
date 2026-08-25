---
name: validate-work-medium
description: Medium-profile skill to run task validation after implementation, before review — check requirements, report pass/fail. Not for fixing failing code (return to implementation), code-quality/architectural review (see review-work-medium), or the full profile (see validate-work-full).
---

# Skill: validate-work-medium

Operation for the **Validation Agent**. Contract:
[.ai/workflow/workflow-medium.md §10](.ai/workflow/workflow-medium.md#10-agent-contracts).

Read [.ai/workflow/workflow-medium.md](.ai/workflow/workflow-medium.md)
in full, same as every other medium-profile skill — do not skip it for
validation.

**All `.ai/`-artifact paths below are relative to the project root, not
to this skill file — write the full `.ai/...` path.** Status values you
set here (`validating`, `in-progress`) are two of exactly eight in a
closed enum — see
[.ai/workflow/workflow-medium.md §11](.ai/workflow/workflow-medium.md#11-status-the-fast-pointer-and-the-permanent-record)
for the full list; never invent one not on it.

## When to use

After implementation, before review — at the `task-validation` gate.
There is no phase-validation at this profile.

## Before anything else: check authority, freshly

Read `.ai/info.md` now, even if you already read it earlier in this
session — it can change mid-session. Confirm whether `task-validation`
is yours to self-certify (`agent`, the `assisted`-mode default) or
requires a human.

## Inputs

The task file's Implementation section (validation instructions).

## Procedure

1. Set the task's Status to `validating` in `.ai/constitution/
   roadmap.md` if not already set. `.ai/info.md`'s Active task pointer
   should already name this task — leave it as the ID only; the status
   word belongs in `roadmap.md`, never in `info.md` (§11).
2. Read the task file's Implementation section (requirements + plan).
3. Execute the validation instructions (automated tests, integration
   checks).
4. Report pass/fail. On failure, do **not** edit implementation to
   force a pass — set Status back to `in-progress` in both places and
   return the task to the implementation loop.
5. Record any accepted exceptions explicitly rather than silently
   ignoring a failure.

## Output

Pass/fail result recorded against the task's row in
`.ai/constitution/roadmap.md` — not a separate permanent log file.
`.ai/info.md`'s Active task pointer is unaffected — it already names
this task; the status word lives only in `roadmap.md` (§11).
