# P06-T06: Add explicit active-pointer-lifecycle statement to §11

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 6: documentation clarity only, no behavior change. §10's Phase Planning
and Task Planning contracts already say to refresh the Active pointer when
creating the phase/task file, and `propagate-context` already clears it at
completion — but §11 never states this lifecycle explicitly in one place. This
task adds one sentence making it explicit.

## Implementation

### Objective

Add one sentence to workflow.md §11 stating when the Active phase/task pointer
is set and cleared, matching existing behavior exactly.

### In scope

- One new sentence in §11, near its description of the Status section as a
  "fast pointer."

### Out of scope

- Any change to when `define-phase`, `define-task-full`, or `propagate-context`
  actually set/clear the pointer — this task only documents existing behavior.

### Files to modify

- `workflow.md` — §11.

### Steps

1. Re-read `define-phase` step 5, `define-task-full` step 7, and
   `propagate-context`'s completion steps to confirm the pointer is set at the
   start of planning (phase or task) and cleared once that phase/task is marked
   complete — this is asserting existing behavior, not introducing new
   behavior, so verify before writing it down.
2. In §11, immediately after the paragraph introducing the Status section
   ("fast, IDs only, no status values... Tells you which two files to open,
   nothing more"), add: "The Active phase pointer is set the moment phase
   planning starts (`define-phase`) and cleared once the phase is marked
   complete (`propagate-context`); Active task follows the same pattern one
   level down (`define-task-full` sets it, `propagate-context` clears it)."
   (flexible: exact wording, binding: which skill sets/clears which pointer,
   confirmed in step 1).
3. Remove the `[HUMAN]` comment line associated with this point (originally
   after the "Active task pointer" discussion in §11).

### Dependencies

None.

### Expected result

§11 states the pointer's set/clear lifecycle explicitly; no behavior changes.

### Automatic validations

- `grep -n "cleared once the phase is marked complete" workflow.md` returns
  one match.

### Manual validations

- Confirm the new sentence matches what `define-phase`, `define-task-full`,
  and `propagate-context` actually do — this task must describe current
  behavior accurately, not a wish.
