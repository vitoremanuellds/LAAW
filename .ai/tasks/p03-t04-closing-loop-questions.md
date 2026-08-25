# P03-T04 — Closing-loop questions in propagate-context

Phase: [`../phases/p03-spec-rigor-and-loop.md`](../phases/p03-spec-rigor-and-loop.md).

## Context

See phase file Context/Plan step 4. This is the completion-side
counterpart to P02-T04's "anything else to add?" (which fires *before*
requesting a plan-review gate). This one fires *after* marking
something complete — the moment the "spontaneous planning" loop
(`workflow.md §5`, "Starting without a plan," P03-T03) needs an
explicit trigger to actually close: implement → mark done → **ask
what's next** → plan the next thing (or stop, if genuinely done).
Without this, the human has to remember to ask every time.

## In scope

- `propagate-context.task`: after marking a task complete, ask whether
  the phase needs more tasks.
- `propagate-context.project`: after marking a phase complete, ask
  whether the project needs another phase.

## Out of scope

- `propagate-context.phase` (the mid-phase reconciliation
  sub-operation) — unaffected, it doesn't mark anything complete.
- Any change to the completion mechanics themselves (Status
  transitions, context promotion) — only a new question added at the
  end of each, after everything else already happens.
- `create-constitution-full`'s "anything else to add?" step (P02-T04)
  — that one already exists and fires at a different moment (before
  review, not after completion); not duplicated here.

## Implementation

**Objective:** Give both completion paths in `propagate-context` an
explicit closing question, so "plan the next thing" has a trigger
instead of relying on the human to ask.

**Files to modify:**

- `skills/propagate-context/SKILL.md` — `propagate-context.task` and
  `propagate-context.project` sub-operations.

**Files to create:** none.

**Steps:**

1. In `propagate-context.task`, after step 4 (set Status `complete`,
   clear `Active task`), add step 5: ask whether the phase needs more
   tasks — does the phase's Plan still look sufficient, or is there
   something to add before this unit of work is really closed. This
   is a question, not a gate — no Status changes on its own; if the
   answer is "yes, more tasks," that's a normal `define-task-full`
   invocation next, same as any other.
2. In `propagate-context.project`, after step 5 (commit), add step 6:
   ask whether the project needs another phase, or is done for now —
   referencing `workflow.md §5`'s "Starting without a plan" as the
   normal next step if the answer is "yes" (append a new bare title
   row via `create-constitution-full`, same as P02 through P05).
3. Confirm neither new step invents a Status value or a gate not in
   the closed eight-value enum (`workflow.md §11`) — these are plain
   questions, not new lifecycle states.

**Dependencies:** none — independent of T01/T02/T03.

**Expected result:** every task and phase completion ends with an
explicit "what's next?" question, closing the planning loop
`workflow.md §5`'s new subsection describes.

**Automatic validations:**

1. `grep -n "more tasks\|another phase" skills/propagate-context/SKILL.md` — both new questions present.
2. `git diff --stat` for this task's commit touches only `skills/propagate-context/SKILL.md`.
3. Confirm no new Status value appears in the diff (`grep` the diff for any word not in the closed enum: `not-planned`, `awaiting-plan-review`, `plan-approved`, `in-progress`, `validating`, `reviewing`, `complete`, `blocked`).

**Manual validations:**

1. Read both updated sub-operations end to end and judge whether the
   new questions read as genuine, expected-to-be-answered questions —
   not buried, not rhetorical, positioned as the clear last thing the
   skill does.
2. Confirm the `propagate-context.project` question naturally points
   back to `workflow.md §5`'s "Starting without a plan" rather than
   describing the append mechanism again from scratch (no duplicated
   how-to, per P02's idea B).
