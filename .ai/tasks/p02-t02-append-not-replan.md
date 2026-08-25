# P02-T02 — Append-not-replan mechanism

Phase: [`../phases/p02-workflow-doc-precision.md`](../phases/p02-workflow-doc-precision.md).

## Context

See phase file Context (item C) for the original framing. **Finding
from task planning, narrowing the scope:** `define-phase`'s existing
replan path already does most of what "append" needs — it already
says "fold in what's already complete rather than discarding it" and
"the existing Tasks table rows carry over unchanged." The actual gap
isn't missing mechanics, it's that (1) `define-phase`'s "When to use"
only mentions replanning "after a phase-level deviation," so an agent
asked to add pure new scope (nothing broken) has no documented path
that says this is fine without inventing a deviation to justify it,
and (2) `workflow.md §6` has no language distinguishing "append" from
"deviation-triggered replan," leaving it ambiguous whether an append
needs a deviation file (it doesn't — there's nothing to record as
`Expected/Discovered/Why it fails`). Same gap in `define-task-full`.
This is mostly a documentation/framing fix, not new mechanism-building
— scope is smaller than the phase file's Context originally implied.

Per T01's Context note (see phase file): add this as a short addition
to existing `workflow.md §6`, not a new top-level section — §6 already
has a similar pattern ("A task file's optional pseudocode is
guidance, not a contract... isn't a deviation by itself") of
clarifying what *isn't* a deviation; this is one more case of that
same pattern, not a new concept needing its own section.

## Requirements

1. `workflow.md §6` states, briefly, that adding new working-as-
   planned scope (a new phase, or new tasks in an existing phase's
   Plan) is not a deviation and doesn't require replanning already-
   approved/complete material — without adding a new top-level
   section (subsection or paragraph within §6 only).
2. `define-phase`'s "When to use" explicitly includes appending new
   Plan items to an already-approved phase, not tied to a deviation,
   as a normal, expected reason to invoke it.
3. `define-task-full`'s "When to use" explicitly includes appending
   new tasks to an existing phase's Plan (once `define-phase` has
   added the corresponding Plan items), not just "breaking a phase's
   plan into tasks" as a one-time operation.
4. The append path is still gated — `phase-review`/`task-review` still
   apply to the newly-added material. Nothing about this change makes
   any gate skippable.
5. No deviation file gets created or implied for a pure append — §6's
   file-naming/lifecycle rules for deviations stay scoped to actual
   deviations.

## Implementation

**Objective:** Document the append path as a normal, non-deviation
use of `define-phase`/`define-task-full`, distinguishing it from both
"define new" and "replan after a deviation" — without building new
mechanism, since the existing replan-path mechanics already cover it.

**Files to modify:**

- `workflow.md` — add a short paragraph to the end of §6.
- `skills/define-phase/SKILL.md` — broaden "When to use"; adjust
  Procedure step 1 and step 4 to explicitly name the append case
  alongside the existing replan case (same mechanics, just remove the
  implication that a deviation must exist to justify invoking this
  skill for additive changes).
- `skills/define-task-full/SKILL.md` — broaden "When to use" the same
  way. Procedure likely needs **no** change — step 1's "doesn't yet
  have a row for every step in its Plan section" logic already
  supports adding tasks incrementally across multiple invocations, as
  long as the corresponding Plan item already exists (which
  `define-phase` now explicitly supports adding). Confirm this during
  implementation rather than assuming — if it turns out a change is
  needed, make it, don't force-fit the "no change" expectation.

**Files to create:** none.

**Steps:**

1. In `workflow.md §6`, after the existing "Task-level/Phase-level/
   Project-level" routing bullets, add: "Adding new, working-as-
   planned scope to already-approved work — a new phase, or new tasks
   in an existing phase's Plan — is not a deviation (nothing broke)
   and doesn't require replanning what's already `plan-approved`/
   `in-progress`/`complete`. It still needs its own `phase-review`/
   `task-review` for the new material specifically. See
   `define-phase`/`define-task-full` for how an append is drafted."
   (Wording may be tightened; keep it short — this is a pointer/
   distinction, not a procedure.)
2. In `skills/define-phase/SKILL.md`'s "When to use," add a third case
   alongside "Defining a new phase" and "replanning one after a
   phase-level deviation": appending new Plan items to an
   already-approved phase, with nothing having gone wrong.
3. In its Procedure step 1 ("Read the roadmap entry... whether this is
   a first draft... or a replan"), add appending as a third case with
   the same "leave Status as-is until step 6" handling.
4. In its Procedure step 4 ("If replanning: fold in what's already
   complete..."), broaden to "If replanning or appending" — for an
   append specifically, there's no deviation to reference (unlike a
   replan, which may cite one); otherwise identical handling.
5. In `skills/define-task-full/SKILL.md`'s "When to use," add
   appending new tasks to an existing phase's Plan (once the Plan
   items exist) as an explicit, normal case — not framed as tied to a
   deviation.
6. Read `define-task-full`'s full Procedure and confirm whether step 1
   already fully supports this, or needs a small clarifying addition.
   Make the change only if actually needed.
7. Re-check `workflow.md §6`'s heading stayed unchanged (no
   renumbering) and that the new paragraph doesn't duplicate anything
   already in `define-phase`/`define-task-full`'s own procedures — it
   should point to them, not restate their steps (idea B).

**Dependencies:** none among P02-T02..T05 — all four are independent
of each other. T02 depended on T01 (already complete).

**Expected result:** an agent asked to add a new phase or new tasks to
an already-approved phase, with nothing having failed, has a clearly
documented path via `define-phase`/`define-task-full` that doesn't
require inventing a deviation, and both plan-review gates still apply
to exactly the new material.

**Validation instructions:**

1. Read the new `workflow.md §6` paragraph — confirm it's short, adds
   no procedural how-to, and doesn't duplicate skill content.
2. Read `define-phase`/`define-task-full`'s updated "When to use" and
   Procedure — confirm an append is now unambiguous and doesn't
   require framing as a deviation.
3. Confirm `phase-review`/`task-review` are still explicitly required
   for appended material — nothing silently became ungated.
4. Confirm `workflow.md`'s heading list is unchanged (no renumbering)
   — `grep -n "^## " workflow.md` before/after.
5. Confirm zero changes outside `workflow.md §6`, `define-phase/SKILL.md`,
   `define-task-full/SKILL.md`.
