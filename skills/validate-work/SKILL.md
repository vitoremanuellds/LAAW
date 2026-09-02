---
name: validate-work
description: Run task- or phase-level validation after implementation, before review — check requirements, report pass/fail. Not for fixing failing code (return to implementation) or code-quality/architectural review (see review-work).
---

# Skill: validate-work

This skill performs the **validation** operation — the first of the
completion-review gate's two internal checks (mechanical, before
review's judgment call; see
[.ai/workflow/workflow.md §8](.ai/workflow/workflow.md#8-validation-vs-review)).

- **Can:** run validation, report failures, set Status `reviewing`.
- **Must:** read `info.md` fresh before trusting a gate's authority —
  never a cached read.
- **Should not:** edit implementation to force a pass.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for validation.

**All `.ai/`-artifact paths below are relative to the project root,
not to this skill file — write the full `.ai/...` path.** Status
values you set here (`reviewing`, `in-progress`) are two of
exactly six in a closed enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)
for the full list; never invent one not on it.

## When to use

After implementation, before review — at task level (`task-validation`
gate) or phase level (`phase-validation` gate; only applicable to a
project that uses phases at all).

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

1. Set the task's Status to `reviewing` if not already set — in its
   owning `.ai/phases/p{NN}-{name}.md` Tasks table if phase-linked, or
   `.ai/tasks/tasks.md` if orphan.
2. Read the task file's Implementation section (requirements + plan).
3. Execute the validation instructions (automated tests, integration
   checks).
4. Report pass/fail. On failure, do **not** edit implementation to
   force a pass — set Status back to `in-progress` there and return
   the task to the implementation loop (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).
5. Record any accepted exceptions explicitly rather than silently
   ignoring a failure.
6. Commit: stage the updated Status row (phase file's Tasks table or
   `.ai/tasks/tasks.md` — the change from step 1, or the revert from
   step 4 on failure); the message should say pass or fail and for
   which task (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline));
   exclude any gitignored files — gitignored layers simply have nothing to
   commit, not a violation of commit discipline.

## Procedure — phase validation

1. Set the phase's Status to `reviewing` in `.ai/phases/phases.md` if
   not already set.
2. Read the phase file's Automatic validations and Manual validations
   sections (separately — never treat them as one merged list) and its
   Tasks table (every task's result in the phase).
3. Run every Automatic validation item first, exactly as written —
   these are mechanical, no judgment involved. Then work through every
   Manual validation item, applying judgment; cross-task/integration
   behavior and phase acceptance criteria belong in this Manual pass.
4. Report pass/fail per validation item, **grouped by Automatic vs.
   Manual, not merged into one overall verdict.** On failure, set
   Status back to `in-progress` rather than leaving it at `reviewing`.
5. Commit: stage `.ai/phases/phases.md`'s updated Status (the change
   from step 1, or the revert from step 4 on failure); the message
   should say pass or fail and for which phase (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline));
   exclude any gitignored files — gitignored layers simply have nothing to
   commit, not a violation of commit discipline.

## Output

Pass/fail result recorded against the task (in its owning phase file's
Tasks table, or `.ai/tasks/tasks.md` if orphan) or phase (in
`.ai/phases/phases.md` and the phase file itself) — not a separate
permanent log file.
