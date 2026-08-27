# P06-T09: Migrate commit-step detail into skills; trim the commit-discipline section to one line

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 9: no skill currently embeds its own commit-message logic — all 8
full-profile skills just link back to workflow.md's commit-discipline section
at their existing "Commit the draft" step. This task adds a concrete commit
step to each skill's own procedure and trims workflow.md's section to one
cross-cutting line, dropping the Conventional-Commits mandate (left to the
user's own `AGENTS.md`).

This section may be numbered §13 or §12 by the time this task runs, depending
on whether `P06-T08` (which deletes §12 and renumbers §13→§12) has already run
— check the live file for the current heading/anchor rather than assuming
either number.

## Implementation

### Objective

Give each of the 8 full-profile skills a self-contained "commit now" step
(what to stage, what the message should convey); reduce workflow.md's
commit-discipline section to one rule, without a mandated message format.

### In scope

- The commit-discipline section's content in `workflow.md` (whichever number
  it currently has).
- Each of the 8 full-profile skills' existing "Commit the draft (see
  workflow.md §13)" step.

### Out of scope

- The section's heading number/anchor itself — that's `P06-T08`'s concern; this
  task edits the section's *content* regardless of what it's numbered.
- Medium-profile skills / `workflow-medium.md`'s own commit-discipline section —
  not part of this phase's scope (see the phase file's Out of scope).
- `workflow-lite`/`workflow-minimal` — already self-contained on this point.

### Files to modify

- `workflow.md` — the commit-discipline section.
- `skills/create-constitution-full/SKILL.md` — step 8's commit instruction.
- `skills/define-phase/SKILL.md` — step 8's commit instruction.
- `skills/define-task-full/SKILL.md` — step 9's commit instruction.
- `skills/implement-task-full/SKILL.md` — its finishing commit instruction.
- `skills/validate-work-full/SKILL.md` — its commit instruction.
- `skills/review-work-full/SKILL.md` — its commit instruction.
- `skills/propagate-context/SKILL.md` — its commit instruction.
- `skills/build-context-full/SKILL.md` — its commit instruction.

### Steps

1. Grep `workflow.md` for "Commit discipline" to find the section's current
   number, then replace its content with: "Commit each draft immediately,
   before requesting review — the review happens via `git diff`. Message
   format and type selection are your project's own convention (see your
   `AGENTS.md`); each skill's own commit step says what to stage." Remove the
   Conventional-Commits examples and the `[HUMAN]` comment beneath them.
2. For each of the 8 skill files listed above, find its existing commit
   instruction (currently phrased like "Commit the draft (see
   [.ai/workflow/workflow.md §13](...))") and replace it with a self-contained
   version naming what that skill's own Output section says gets produced —
   e.g. for `define-phase`: "Commit the draft: stage
   `.ai/phases/p{NN}-{name}.md` and any `.ai/constitution/roadmap.md`/
   `.ai/info.md` changes from this step; the message should say what phase was
   drafted and why." (flexible: exact wording per skill — binding: it must
   name the actual files that skill's procedure just touched, not a generic
   placeholder).
3. Update each skill's anchor link to the commit-discipline section to match
   whatever number `workflow.md` currently uses for it (re-check at
   implementation time — don't hardcode §13 or §12 from memory).

### Dependencies

None (order-independent with `P06-T08`; both re-read the live file rather than
assuming section numbers).

### Expected result

workflow.md's commit-discipline section is 4 lines instead of 20; each of the
8 full-profile skills states its own concrete commit step without depending on
Conventional Commits.

### Automatic validations

- `grep -n "Conventional Commits" workflow.md` returns no matches.
- `grep -rLn "Commit the draft" skills/create-constitution-full/SKILL.md
  skills/define-phase/SKILL.md skills/define-task-full/SKILL.md
  skills/implement-task-full/SKILL.md skills/validate-work-full/SKILL.md
  skills/review-work-full/SKILL.md skills/propagate-context/SKILL.md
  skills/build-context-full/SKILL.md` — confirm each still has *some* commit
  instruction (a still-present phrase or its self-contained replacement), i.e.
  no skill lost its commit step entirely.

### Manual validations

- Spot-check 2–3 of the rewritten skill commit steps to confirm they name real
  files that skill's procedure actually produces, not a generic restatement.
- Confirm workflow.md's trimmed section still reads as a complete rule on its
  own (commit timing + where format comes from), not an orphaned fragment.
