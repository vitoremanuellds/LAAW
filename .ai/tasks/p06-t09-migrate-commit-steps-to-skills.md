# P06-T09: Migrate commit-step detail into skills; trim the commit-discipline section to one line

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 9: no skill currently embeds its own commit-message logic — all 8
full-profile skills just link back to workflow.md's commit-discipline section
at their existing "Commit the draft" step. This task adds a concrete commit
step to each skill's own procedure and trims workflow.md's section to one
cross-cutting line, dropping the Conventional-Commits mandate (left to the
user's own `AGENTS.md`).

This section stays §13 regardless of `P06-T08` — that task was revised to
delete §12 without renumbering §13 (per
`.ai/context/workflow-doc-conventions.md`'s section-stability convention), so
this task can rely on `§13`/`#13-commit-discipline` staying fixed.

## Implementation

### Objective

Give each of the 8 full-profile skills a self-contained "commit now" step
(what to stage, what the message should convey); reduce workflow.md's
commit-discipline section to one rule, without a mandated message format.

### In scope

- workflow.md §13's content (heading, anchor, and number unchanged).
- Each of the 8 full-profile skills' existing "Commit the draft (see
  workflow.md §13)" step.

### Out of scope

- §13's heading, number, or anchor — unchanged by this task and by `P06-T08`.
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

1. Replace §13's content with: "Commit each draft immediately, before
   requesting review — the review happens via `git diff`. Message format and
   type selection are your project's own convention (see your `AGENTS.md`);
   each skill's own commit step says what to stage." Remove the
   Conventional-Commits examples and the `[HUMAN]` comment beneath them. Leave
   the `## 13. Commit discipline` heading itself untouched.
2. For each of the 8 skill files listed above, find its existing commit
   instruction (currently phrased like "Commit the draft (see
   [.ai/workflow/workflow.md §13](...))") and replace it with a self-contained
   version naming what that skill's own Output section says gets produced —
   e.g. for `define-phase`: "Commit the draft: stage
   `.ai/phases/p{NN}-{name}.md` and any `.ai/constitution/roadmap.md`/
   `.ai/info.md` changes from this step; the message should say what phase was
   drafted and why." (flexible: exact wording per skill — binding: it must
   name the actual files that skill's procedure just touched, not a generic
   placeholder). The `§13`/`#13-commit-discipline` link itself stays as-is —
   only the sentence around it changes.

### Dependencies

None (independent of `P06-T08`; §13's number/anchor is fixed either way).

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
