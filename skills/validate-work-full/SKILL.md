---
name: validate-work-full
description: Full-profile skill to run task- or phase-level validation after implementation, before review — check requirements, report pass/fail. Not for fixing failing code (return to implementation) or code-quality/architectural review (see review-work-full).
---

# Skill: validate-work-full

Operation for the **Validation Agent**. Contract:
[.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts).

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for validation.

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
   `.ai/phases/p{NN}-{name}.md` Tasks table if not already set.
   `.ai/info.md`'s Active task pointer should already name this task —
   leave it as the ID only; the status word belongs in the phase
   file's table, never in `info.md` (§11).
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
   `.ai/constitution/roadmap.md` if not already set. `.ai/info.md`'s
   Active phase pointer should already name this phase — leave it as
   the ID only; the status word belongs in `roadmap.md`, never in
   `info.md` (§11).
2. Read the phase file's Automatic validations and Manual validations
   sections (separately — never treat them as one merged list) and its
   Tasks table (every task's result in the phase).
3. Run every Automatic validation item first, exactly as written —
   these are mechanical, no judgment involved. Then work through every
   Manual validation item, applying judgment; cross-task/integration
   behavior and phase acceptance criteria belong in this Manual pass.
4. Report pass/fail per validation item, **grouped by Automatic vs.
   Manual, not merged into one overall verdict.** On failure, set
   Status back to `in-progress` in both places rather than leaving it
   at `validating`.

## Output

Pass/fail result recorded against the task (in its owning phase file's
Tasks table) or phase (in `.ai/constitution/roadmap.md` and the phase
file itself) — not a separate permanent log file. `.ai/info.md`'s
Active task/phase pointer is unaffected — it already names this item;
the status word lives only in the phase file's table or `roadmap.md`
(§11).
