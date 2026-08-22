---
name: workflow-validation
description: Use this skill to run task-level or phase-level validation after implementation is complete, before review. Trigger this whenever the user wants to check whether a task or phase satisfies its stated requirements, run the validation instructions from a task file or phase file, or report pass/fail results against acceptance criteria. Do not use this to fix failing code — validation only reports failures; fixes return to the implementation loop. Do not use this for code-quality or architectural review; see workflow-review for that.
---

# Skill: workflow.validation

Operation for the **Validation Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

After implementation, before review — at task level (`task-validation`
gate) or phase level (`phase-validation` gate).

## Before anything else: check authority, freshly

Read [../../../info.md](../../../info.md) now, even if you already
read it earlier in this session — it can change mid-session, and
relying on a stale read of it is exactly what causes a gate's
authority setting to get silently ignored. Confirm whether
`task-validation`/`phase-validation` is yours to self-certify
(`agent`, the `assisted`-mode default) or requires a human. Don't
proceed on the assumption that whatever you last saw is still current.

## Inputs

- Task: the task file's Implementation section (validation instructions).
- Phase: the phase file's Validations section and its Tasks table.

## Procedure — task validation

1. Set the task's Status to `validating` in its owning phase file's
   Tasks table if not already set, and update `info.md`'s Status
   section to match.
2. Read the task file's Implementation section (requirements + plan).
3. Execute the validation instructions (automated tests, integration
   checks).
4. Report pass/fail. On failure, do **not** edit implementation to
   force a pass — set Status back to `in-progress` in both places and
   return the task to the implementation loop (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)).
5. Record any accepted exceptions explicitly rather than silently
   ignoring a failure.

## Procedure — phase validation

1. Set the phase's Status to `validating` in
   `../../../constitution/roadmap.md` if not already set, and update
   `info.md` to match.
2. Read the phase file's Validations section and its Tasks table (every
   task's result in the phase).
3. Check cross-task/integration behavior and phase acceptance criteria.
4. Report pass/fail per validation item, not just an overall verdict.
   On failure, set Status back to `in-progress` in both places rather
   than leaving it at `validating`.

## Output

Pass/fail result recorded against the task (in its owning phase file's
Tasks table) or phase (in `roadmap.md` and the phase file itself) —
not a separate permanent log file. `info.md` updated to match.
