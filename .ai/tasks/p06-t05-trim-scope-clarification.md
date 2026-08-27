# P06-T05: Trim the new-scope-isn't-a-deviation clarification to one line

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 5: workflow.md §6 currently spends three sentences explaining that
adding new, working-as-planned scope to already-approved work isn't a deviation.
This is a real rule (disambiguating a common false-positive: routine roadmap
growth vs. an actual deviation) worth keeping, but the procedural detail — "how
an append is drafted" — is already fully covered elsewhere: `define-phase`'s
"When to use" section already names appending as a first-class case and its
step 4 already states "For an append specifically, there's no deviation to
reference — just add the new Plan item(s) where they logically fit"; likewise
`define-task-full`'s "When to use" section already covers drafting tasks for a
phase's append. Nothing needs to be added to those skills — only workflow.md's
own paragraph needs trimming.

## Implementation

### Objective

Replace the three-sentence "new scope isn't a deviation" paragraph in workflow.md
§6 with one line stating the rule, keeping the existing pointer to
`define-phase`/`define-task-full`.

### In scope

- workflow.md §6's "Adding new, working-as-planned scope..." paragraph only.

### Out of scope

- `define-phase` and `define-task-full` — verified above to already document
  append mechanics; no changes needed there for this task. (If, at
  implementation time, either skill no longer covers this — re-verify before
  assuming — that would be a scope change worth flagging rather than silently
  reintroducing the detail into workflow.md.)

### Files to modify

- `workflow.md` — §6.

### Steps

1. Re-read `define-phase`'s "When to use" section and step 4, and
   `define-task-full`'s "When to use" section, to confirm they still describe
   how an append is drafted (verified true as of this task's planning).
2. Replace the paragraph "Adding new, working-as-planned scope to already-approved
   work — a new phase, or new tasks in an existing phase's Plan — is not a
   deviation (nothing broke) and doesn't require replanning what's already
   `plan-approved`/`in-progress`/`complete`. It still needs its own
   `phase-review`/`task-review` for the new material specifically. See
   `define-phase`/`define-task-full` for how an append is drafted." with one
   line: "Adding new, working-as-planned scope to already-approved work (a new
   phase, or new tasks in an existing phase's Plan) is not a deviation — it
   still needs its own `phase-review`/`task-review` for the new material,
   drafted per `define-phase`/`define-task-full`."
3. Remove the `[HUMAN]` comment line following this paragraph (it's now
   addressed).

### Dependencies

None.

### Expected result

§6 states the same rule in one sentence instead of three; no skill files
changed.

### Automatic validations

- `grep -c "is not a deviation" workflow.md` returns at least 1 (rule
  preserved, not deleted).

### Manual validations

- Confirm the one-liner reads clearly without the removed explanatory
  sentences, and that `define-phase`/`define-task-full` genuinely still cover
  the "how an append is drafted" detail this line points to.
