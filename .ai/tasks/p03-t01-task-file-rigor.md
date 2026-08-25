# P03-T01 — Task-file rigor: In-scope/Out-of-scope + Automatic/Manual validations

Phase: [`../phases/p03-spec-rigor-and-loop.md`](../phases/p03-spec-rigor-and-loop.md).

This task's own file uses the target structure it's building (In
scope/Out of scope + Automatic/Manual validations), same reasoning as
the phase file — a worked example, drafted by hand since
`define-task-full` doesn't generate this shape yet.

## Context

See phase file Context/Plan step 1. `implement-task-full`'s current
step 4 says "minor mismatches... adjust and continue, no deviation
needed" — a general latitude with no explicit boundary. The fix isn't
to remove that latitude entirely (some flexibility is genuinely
useful, e.g. exact variable names), it's to make the boundary
explicit: a task file marks specific details as flexible; everything
else, even something that used to read as "minor," is binding.
`workflow.md §6`'s deviation definition currently says "a wrong file
or small mismatch is not one" — this needs to change to match, or the
two documents contradict each other.

## In scope

- `define-task-full/SKILL.md` step 4: add In-scope/Out-of-scope
  subsections to the Implementation section it instructs writing.
- `define-task-full/SKILL.md` step 4: add an explicit convention for
  marking a Step detail as flexible/low-importance inline.
- `define-task-full/SKILL.md` step 4: split "Dependencies, expected
  result, validation instructions" into separate Automatic
  validations / Manual validations bullets.
- `implement-task-full/SKILL.md` step 4: tighten the "minor
  mismatches" language to only cover details explicitly marked
  flexible.
- `workflow.md §6`: update the deviation definition's "small mismatch
  is not one" sentence to match the same, stricter standard.

## Out of scope

- Phase-level rigor (`define-phase`, `validate-work-full`) — P03-T02.
- Retroactively rewriting P01/P02's already-complete task files.
- `workflow-medium.md`, `skills/*-medium/`, `workflow-lite/SKILL.md`,
  `workflow-minimal/SKILL.md`, or their templates.
- Changing `implement-task-full` step 5 (raising a deviation) itself —
  only step 4 (what counts as adjustable vs. not) changes; step 5
  already correctly says to stop and raise a deviation when something
  doesn't match.

## Implementation

**Objective:** Give task files an explicit scope boundary and a
split validation section, and make "what's freely adjustable during
implementation" an explicit, task-file-stated set rather than an
implicit, agent-judged one.

**Files to modify:**

- `skills/define-task-full/SKILL.md` — step 4.
- `skills/implement-task-full/SKILL.md` — step 4.
- `workflow.md` — §6, one sentence.

**Files to create:** none.

**Steps:**

1. In `define-task-full/SKILL.md` step 4's Implementation subsection
   list, insert **In scope** and **Out of scope** immediately after
   **Objective**, before **Files to modify**: In scope — a short
   bullet list of exactly what this task covers. Out of scope — a
   short bullet list of adjacent things this task deliberately does
   *not* do (things a reader might otherwise assume are included,
   given the Objective).
2. In the same list's **Steps** bullet, add: any step detail that's
   genuinely low-importance/flexible must be marked explicitly inline
   (e.g. "(flexible: exact variable name)") — unmarked details are
   binding. A mismatch against an unmarked detail during
   implementation is a deviation, not a minor adjustment.
3. Replace the trailing "**Dependencies**, **expected result**,
   **validation instructions**" bullet with three separate bullets:
   **Dependencies**, **expected result**, **Automatic validations**
   (mechanically checkable — a command, a grep, a test run, literal
   enough to run without judgment), **Manual validations** (requires a
   human or agent judgment call that can't be scripted). Both
   validation kinds present where applicable; never merged back into
   one undifferentiated list.
4. In `implement-task-full/SKILL.md` step 4, replace "Minor mismatches
   (a function living in a different file than expected, or an
   implementation detail that differs from the pseudocode's
   specifics) — adjust and continue, no deviation needed" with:
   adjust freely only where the task file explicitly marks a detail
   flexible (per step 2 above); anything else that doesn't match —
   even something that used to read as a small, adjustable mismatch —
   gets raised as a deviation per step 5, not silently adjusted.
5. In `workflow.md §6`, replace "A wrong file or small mismatch is not
   one — adjust and continue." with: a mismatch against a detail the
   task file explicitly marked flexible is not one — adjust and
   continue; everything else that doesn't match the approved plan is,
   even something that used to read as a small, adjustable mismatch —
   see `define-task-full`'s task-file conventions for how flexible
   details get marked.
6. Confirm `workflow.md`'s heading list is unchanged — §6's heading
   itself isn't touched, only a sentence within its body, so no
   cross-reference sweep should be needed, but verify rather than
   assume (per `.ai/context/workflow-doc-conventions.md`).

**Dependencies:** none — first task in P03.

**Expected result:** `define-task-full` generates task files with
explicit In-scope/Out-of-scope, an explicit flexible-detail marking
convention, and split Automatic/Manual validations; `implement-task-full`
and `workflow.md §6` consistently treat only explicitly-flagged
details as freely adjustable.

**Automatic validations:**

1. `grep -n "In scope\|Out of scope\|Automatic validations\|Manual validations" skills/define-task-full/SKILL.md` — all four present in step 4's instructions.
2. `grep -n "flexible" skills/define-task-full/SKILL.md skills/implement-task-full/SKILL.md workflow.md` — the marking convention and its consequence appear in all three files.
3. `grep -n "minor mismatch" skills/implement-task-full/SKILL.md` — confirm the old unqualified phrase is gone (replaced, not just supplemented).
4. `grep -n "^## " workflow.md` before/after this task's edit — identical (no heading changed or moved).
5. `git diff --stat` for this task's commit touches exactly
   `skills/define-task-full/SKILL.md`, `skills/implement-task-full/SKILL.md`,
   `workflow.md` — nothing else.

**Manual validations:**

1. Read the updated `define-task-full/SKILL.md` step 4 and judge
   whether a task file drafted under it would actually narrow scope
   (In scope/Out of scope reads as more than a restatement of Steps).
2. Read `implement-task-full/SKILL.md`'s updated step 4 against a
   concrete hypothetical: task says modify `auth.py`, but the
   equivalent function actually lives in `auth_utils.py`, not flagged
   flexible in the task file. Confirm the new language would correctly
   route this to a deviation, not silently allow the adjustment.
