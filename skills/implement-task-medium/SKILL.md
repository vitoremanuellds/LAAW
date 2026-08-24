---
name: implement-task-medium
description: Medium-profile skill to write, modify, or delete project code for a task with an already-approved task file. Requires task planning first — use define-task-medium if the task file doesn't exist. Not for the full profile (see implement-task-full) or for planning what a task should do.
---

# Skill: implement-task-medium

Operation for the **Implementation Agent**. Contract:
[.ai/workflow/workflow-medium.md §10](.ai/workflow/workflow-medium.md#10-agent-contracts).

This is the most frequently invoked skill in this profile — it runs
once per task.

**All `.ai/`-artifact paths below are relative to the project root, not
to this skill file — write the full `.ai/...` path, never a bare or
dot-relative one.** Project source paths are correctly relative to the
project root already, same as normal.

## 1. What to read

Read [.ai/workflow/workflow-medium.md](.ai/workflow/workflow-medium.md)
in full, same as every other medium-profile skill — do not skip it or
rely on a partial local summary being complete. Then read:

1. `.ai/info.md` — read fresh, not from earlier in the session;
   confirms this is genuinely the active task and tells you whether
   `task-validation`/`task-review` are yours to self-certify.
2. The task's file (`.ai/tasks/t{NN}-{name}.md`, Context +
   Implementation sections — including its Files to modify/create and
   Steps; there's no Pseudocode section at this profile).
3. Only the files the task's Context section lists as relevant, plus
   whatever those reference and you actually end up touching.
4. Explore the actual codebase with `tree`/`find`/`grep`/`ls` directly
   when you need to locate something.

## 2. Procedure

1. Read the task file's Implementation section in full: objective,
   files to modify, files to create, ordered steps, dependencies,
   expected result, validation instructions.
2. Read the Context section and only the referenced files it names.
3. Check the task's current Status in `.ai/constitution/roadmap.md`'s
   row for it — the task file itself never tracks its own status. It
   should be `plan-approved` — if it's still `awaiting-plan-review`,
   task-review hasn't actually passed yet; stop and check before
   proceeding. Once confirmed, set Status to `in-progress` there.
   `.ai/info.md`'s Active task pointer already names this task from
   task planning — leave it as the ID only; the status word belongs in
   `roadmap.md`, never in `info.md` (§11). **The Status enum
   is exactly these eight values, nothing else:** `not-planned` ·
   `awaiting-plan-review` · `plan-approved` · `in-progress` ·
   `validating` · `reviewing` · `complete` · `blocked`. If you find
   yourself wanting a status this list doesn't have, stop and re-read
   [.ai/workflow/workflow-medium.md §11](.ai/workflow/workflow-medium.md#11-status-the-fast-pointer-and-the-permanent-record)
   rather than write something new into the table.
4. Follow the task's Files-to-modify/Files-to-create and Steps in
   order. Minor mismatches (a function living in a different file than
   expected) — adjust and continue, no deviation needed; see
   [.ai/workflow/workflow-medium.md §6](.ai/workflow/workflow-medium.md#6-deviations).
5. If the plan turns out wrong in a way that changes scope, or the
   strategy itself has to change — stop and raise a deviation. Do not
   silently expand scope or improvise past what was approved.
6. If you make an architectural decision along the way that future
   work needs to know about, this is yours to document. Check
   `.ai/decisions/decisions.md` first; if not already covered, write
   the ADR from
   [.ai/workflow/templates/adr-template.md](.ai/workflow/templates/adr-template.md)
   into `.ai/decisions/adr{NN}-{name}.md` and add its row to the index
   in the same step.

## 3. Finishing

1. Set the task's Status to `validating` (or `blocked` if stuck) in
   `.ai/constitution/roadmap.md`. `.ai/info.md`'s Active task pointer
   already names this task — leave it as the ID only; the status word
   belongs in `roadmap.md`, never in `info.md` (§11).
2. Commit (see
   [.ai/workflow/workflow-medium.md §13](.ai/workflow/workflow-medium.md#13-commit-discipline)).
   Stop for `task-validation` — see `.ai/info.md` (read fresh) for
   whether that's yours to run (→
   [validate-work-medium](.ai/workflow/skills/validate-work-medium/SKILL.md))
   or a human's.
3. Do not mark the task complete yourself — completion requires
   validation and review to pass first.

## Output

Modified project files; an updated row in `.ai/constitution/
roadmap.md` (`.ai/info.md`'s pointer is unaffected — see §11); a new ADR and
`.ai/decisions/decisions.md` row if an architectural decision was
made; the task ready for validation.
