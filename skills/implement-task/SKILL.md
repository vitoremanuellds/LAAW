---
name: implement-task
description: Write, modify, or delete project code for a task with an already-approved task file — phase-linked or orphan. Requires task planning first — use define-task if the task file doesn't exist. Not for planning what a task should do.
---

# Skill: implement-task

This skill performs the **implementation** operation
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from).

- **Can:** read the task file + context; modify project files; run
  tools.
- **Must:** update the task's Status as it progresses (its owning
  phase file's Tasks table if phase-linked, `.ai/tasks/tasks.md` if
  orphan); write an ADR for decisions made along the way, scaffolding
  `.ai/decisions/` first if this is the project's first-ever one;
  treat pseudocode as guidance.
- **Cannot:** silently change approved requirements/plan.

This is the most frequently invoked skill in the workflow — it runs
once per task, potentially many times per phase.

**All `.ai/`-artifact paths below (`.ai/info.md`, `.ai/phases/...`,
`.ai/tasks/...`) are relative to the project root, not to this skill
file — write the full `.ai/...` path, never a bare or dot-relative
one.** Project source paths (the actual code you're editing) are
correctly relative to the project root already, same as normal.

## 1. What to read

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full,
same as every other skill — do not skip it for implementation. This
skill used to say the opposite (skip the reread, rules are compiled
here); that carve-out is gone because it was wrong in a way that
actually happened: an agent invented a status value that isn't in the
closed enum (§2 below has the real list), because this skill's own
partial summary of it wasn't enough to stop that. A shorter read here
is not worth an agent inventing rules. Then read:

1. `.ai/info.md` — read fresh, not from earlier in the session;
   confirms whether `task-validation`/`task-review` are yours to
   self-certify.
2. The task's file (`.ai/tasks/p{NN}-t{NN}-{name}.md` if phase-linked,
   `.ai/tasks/t{NN}-{name}.md` if orphan — Context + Implementation
   sections, including its Files to modify/create, Steps, and any
   Pseudocode).
3. Only the files the task's Context section lists as relevant, plus
   whatever those reference and you actually end up touching. Don't
   pull in unrelated modules "for context."
4. Explore the actual codebase with `tree`/`find`/`grep`/`ls` directly
   when you need to locate something — there's no structure map to
   consult or keep in sync; the filesystem is the source of truth.

## 2. Procedure

1. Read the task file's Implementation section in full: objective,
   files to modify, files to create, ordered steps, pseudocode if
   present, dependencies, expected result, validation instructions.
2. Read the Context section and only the referenced files it names.
3. Check the task's current Status — in its owning phase file's Tasks
   table if phase-linked (`.ai/phases/p{NN}-{name}.md`), or in
   `.ai/tasks/tasks.md` if orphan; the task file itself never tracks
   its own status, that table is the only place it lives. It should be
   `plan-approved` — if it's still `awaiting-plan-review`, task-review
   hasn't actually passed yet; stop and check before proceeding rather
   than assuming being asked to implement implies approval happened.
   Once confirmed, set Status to `in-progress` there.
   **The Status enum is exactly these eight values, nothing else:**
   `not-planned` · `awaiting-plan-review` · `plan-approved` ·
   `in-progress` · `validating` · `reviewing` · `complete` ·
   `blocked`. If you find yourself wanting a status this list doesn't
   have, that's a signal you've misunderstood the situation, not a
   reason to invent one — stop and re-read
   [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-permanent-record)
   rather than write something new into the table.
4. Follow the task's Files-to-modify/Files-to-create and Steps in
   order. If Pseudocode is present, treat it as guidance for the
   approach, not a literal script — adapt it to what you actually find
   in the codebase; this is its own, separate, unconditional latitude
   (pseudocode is meant to be translated, not copied), not tied to the
   marking convention below. **For Steps specifically: adjust freely
   only where the task file explicitly marked a detail flexible**
   (e.g. `(flexible: ...)`) — everything else that doesn't match, even
   something that would once have read as a small, adjustable mismatch
   (a function living in a different file than expected), gets raised
   as a deviation per step 5 below, not silently adjusted; see
   [.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations).
5. If the plan turns out wrong in a way that changes scope, the
   library/API doesn't support what was planned, or the strategy
   itself has to change — stop and raise a deviation. Do not silently
   expand scope or improvise past what was approved.
6. If you make an architectural decision along the way (a new
   dependency, a new pattern) that future work needs to know about,
   this is yours to document — you don't escalate it. Check
   `.ai/decisions/decisions.md` first; a related decision may already
   exist. If `.ai/decisions/` doesn't exist yet, scaffold it per
   [reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)
   first. Then write the ADR from
   [.ai/workflow/templates/adr-template.md](.ai/workflow/templates/adr-template.md)
   into `.ai/decisions/adr{NN}-{name}.md` and add its row to the index
   in the same step.

## 3. Finishing

1. Set the task's Status to `validating` (or `blocked` if stuck) — in
   its owning phase file's Tasks table if phase-linked, or
   `.ai/tasks/tasks.md` if orphan.
2. Commit: stage the modified/created project files, the updated
   Status row (phase file or `tasks.md`), and any new ADR +
   `.ai/decisions/decisions.md` row you wrote; the message should say
   what was implemented (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
   Stop for `task-validation` — see `.ai/info.md` (read fresh) for
   whether that's yours to run (→
   [validate-work](.ai/workflow/skills/validate-work/SKILL.md)) or a human's.
3. Do not mark the task complete yourself — completion requires
   validation and review to pass first (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).

## Output

Modified project files; an updated Status row (owning phase file's
Tasks table if phase-linked, `.ai/tasks/tasks.md` if orphan); a new ADR
and `.ai/decisions/decisions.md` row (scaffolded first if needed) if an
architectural decision was made; the task ready for validation.
