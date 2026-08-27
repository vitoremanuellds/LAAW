# P06-T08: Fold §12's single-active-item constraint into §11; delete the rest of §12

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 8: workflow.md §12 ("Multi-agent / multi-human") is mostly advisory
content about team usage this repo doesn't need to own, but it states one real
constraint found nowhere else: "`info.md` tracks only one active phase/task by
design." This task moves that one fact into §11 and deletes the rest of §12.

**Revised during T04's implementation:** the original version of this task
planned to renumber §13 ("Commit discipline") down to §12 after deleting §12,
and to sweep every cross-reference to match. Reading
`.ai/context/workflow-doc-conventions.md` (surfaced while implementing T04)
found this repo has an explicit, already-established convention against
exactly that: "Every one of `workflow.md`'s 13 section headings/numbers is
deliberately kept stable... A new [or removed] top-level section shifts every
following section's number, which breaks every anchor pointing past it." The
convention's own guidance is to avoid the renumber, not to sweep it — so this
task no longer renumbers anything. §12 is simply removed; §13 ("Commit
discipline") keeps its number and anchor exactly as-is, with a gap where §12
used to be. This removes the entire cross-reference-sweep risk this task
previously carried.

## Implementation

### Objective

Delete workflow.md §12 except its single-active-item constraint, which moves
into §11. Leave §13 completely untouched — no renumbering, no anchor changes,
no cross-reference sweep.

### In scope

- workflow.md §11 (add the constraint sentence).
- workflow.md §12 (delete in full — heading, content, and its `[HUMAN]`
  comment).

### Out of scope

- Section numbering/renumbering of any kind — per
  `.ai/context/workflow-doc-conventions.md`'s section-stability convention,
  `workflow.md` simply goes from §11 to §13 with no §12, and that's fine.
- The commit-discipline section (§13) — untouched by this task; see `P06-T09`
  for its content changes (which also don't renumber it).
- `workflow-medium.md` — has its own independent section numbering, not
  touched by this task.

### Files to modify

- `workflow.md` — §11 (add sentence), §12 (delete).

### Steps

1. In §11, add one sentence (near the pointer-lifecycle sentence added by
   `P06-T06`, if already present — otherwise as its own addition): "`info.md`
   tracks only one active phase/task by design; genuinely parallel work needs
   each agent tracking its own item some other way until this format supports
   more than one."
2. Delete workflow.md §12 in full: its heading (`## 12. Multi-agent /
   multi-human`), the "Independent tasks or phases may run in parallel..."
   paragraph, and the `[HUMAN]` comment following it. Leave §13 immediately
   following §11 in the document — do not rename or renumber it.

### Dependencies

None.

### Expected result

§11 states the single-active-item constraint; §12 no longer exists as a
heading at all (the document goes §11 → §13); §13 ("Commit discipline") is
byte-identical to before this task, including its heading, anchor, and every
existing cross-reference to it.

### Automatic validations

- `grep -n "## 12\." workflow.md` returns no matches (no section 12 exists
  anymore, renumbered or otherwise).
- `grep -n "## 13. Commit discipline" workflow.md` returns exactly one match,
  unchanged from before this task.
- `grep -n "info.md.*tracks only one active" workflow.md` returns one match,
  inside §11.

### Manual validations

- Confirm §11 reads coherently with the added sentence, whether or not
  `P06-T06`'s sentence is already present.
- **Correction found during implementation:** deleting §12 outright (not just
  renumbering) still broke two inbound links — `define-phase` and
  `define-task-full` both linked to `#12-multi-agent--multi-human` for
  concepts now covered by §11. Fixing dangling anchors from a section
  *deletion* is not the same risk this task's original note warned about
  (renumbering ripple) — it's just completing the deletion correctly. Grep
  `workflow.md §12\|#12-multi-agent` across `skills/*/SKILL.md`, `README.md`,
  and `templates/*.md` to confirm zero remaining references before calling
  this done.
