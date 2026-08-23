---
name: workflow-validation
description: Use this skill to run task- or phase-level validation after implementation, before review — check requirements, report pass/fail. Not for fixing failing code (return to implementation) or code-quality/architectural review (see workflow-review).
---

# Skill: workflow.validation

Operation for the **Validation Agent**. Contract:
[.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts).

**All `.ai/`-artifact paths below are relative to the project root,
not to this skill file — write the full `.ai/...` path.** Status
values you set here (`validating`, `in-progress`) are two of exactly
eight in a closed enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)
for the full list; never invent one not on it.

## When to use

After implementation, before review — at task level (`task-validation`
gate) or phase level (`phase-validation` gate).

## Before anything else: check authority, freshly

Read `.ai/info.md` now, even if you already read it earlier in this
session — it can change mid-session, and relying on a stale read is
exactly what causes a gate's authority setting to get silently
ignored. Confirm whether `task-validation`/`phase-validation` is yours
to self-certify (`agent`, the `assisted`-mode default) or requires a
human. Don't proceed on the assumption that whatever you last saw is
still current.

## Inputs

- Task: the task file's Implementation section (validation instructions).
- Phase: the phase file's Validations section and its Tasks table.

## Procedure — task validation

1. Set the task's Status to `validating` in its owning
   `.ai/phases/p{NN}-{name}.md` Tasks table if not already set, and
   update `.ai/info.md`'s Status section to match.
2. Read the task file's Implementation section (requirements + plan).
3. Execute the validation instructions (automated tests, integration
   checks).
4. Report pass/fail. On failure, do **not** edit implementation to
   force a pass — set Status back to `in-progress` in both places and
   return the task to the implementation loop (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).
5. Record any accepted exceptions explicitly rather than silently
   ignoring a failure.

## Procedure — phase validation

1. Set the phase's Status to `validating` in
   `.ai/constitution/roadmap.md` if not already set, and update
   `.ai/info.md` to match.
2. Read the phase file's Validations section and its Tasks table (every
   task's result in the phase).
3. Check cross-task/integration behavior and phase acceptance criteria.
4. Report pass/fail per validation item, not just an overall verdict.
   On failure, set Status back to `in-progress` in both places rather
   than leaving it at `validating`.

## Output

Pass/fail result recorded against the task (in its owning phase file's
Tasks table) or phase (in `.ai/constitution/roadmap.md` and the phase
file itself) — not a separate permanent log file. `.ai/info.md`
updated to match.
