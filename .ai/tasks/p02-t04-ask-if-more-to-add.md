# P02-T04 — "Anything else to add?" step in planning skills

Phase: [`../phases/p02-workflow-doc-precision.md`](../phases/p02-workflow-doc-precision.md).

## Context

See phase file Context (item E). Drafting is ungated (`workflow.md §5`)
— only *advancing past* a draft needs approval — so this new step
belongs inside each skill's existing ungated drafting sequence,
immediately before the step that commits and stops for the review
gate, not after.

## Requirements

1. `create-constitution-full`, `define-phase`, and `define-task-full`
   each have an explicit step: before committing and stopping for
   their review gate, ask the human whether there's more to fold into
   this draft.
2. The step is positioned immediately before the existing
   commit-and-stop step in each skill's Procedure (renumbering
   subsequent steps as needed), not appended after.
3. No gate behavior changes — this is an additional drafting step, not
   a new gate.

## Implementation

**Objective:** Add a batching checkpoint to the three planning skills
so a human's later "oh, also add X" doesn't trigger a second review
cycle for something that could have been included in the first.

**Files to modify:**

- `skills/create-constitution-full/SKILL.md` — insert before current
  step 7 ("Commit the draft... Stop. Constitution review is a
  gate...").
- `skills/define-phase/SKILL.md` — insert before current step 7
  ("Commit the draft... Stop for phase plan review...").
- `skills/define-task-full/SKILL.md` — insert before current step 8
  ("Once every task in scope for this invocation is drafted, commit
  everything together... Stop for task plan review...").

**Files to create:** none.

**Steps:**

1. In `create-constitution-full/SKILL.md`, insert a new step before
   the commit-and-stop step: "Ask the user whether there's anything
   else to add to this draft (mission, techstack, or roadmap) before
   requesting review — batch it in now rather than triggering a
   second review cycle later." Renumber the old step 7 to 8 (and
   update its own internal step-number references if any).
2. Same insertion in `define-phase/SKILL.md`, scoped to the phase's
   Context/Requirements/Plan/Validations. Renumber old step 7 to 8.
3. Same insertion in `define-task-full/SKILL.md`, scoped to "more
   tasks to draft this invocation, or missing scope in the ones just
   drafted." Renumber old step 8 to 9.
4. Re-read each modified skill file end to end to confirm step
   numbering is internally consistent (no skipped or duplicate
   numbers, no stale reference to an old step number elsewhere in the
   same file).

**Dependencies:** none among P02-T02..T05.

**Expected result:** all three planning skills ask "anything else?"
as their last drafting action before requesting review.

**Validation instructions:**

1. Read each of the three modified skill files end to end — confirm
   the new step exists, is positioned immediately before the
   commit-and-stop step, and step numbering is consistent throughout
   the rest of the file.
2. Confirm no gate's default authority or behavior changed — this is
   additive to drafting only.
3. Confirm zero changes outside the three files listed above.
