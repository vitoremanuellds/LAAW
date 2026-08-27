# P06-T08: Fold §12's single-active-item constraint into §11; delete the rest of §12

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 8: workflow.md §12 ("Multi-agent / multi-human") is mostly advisory
content about team usage this repo doesn't need to own, but it states one real
constraint found nowhere else: "`info.md` tracks only one active phase/task by
design." This task moves that one fact into §11 and deletes the rest of §12.

Because §12 is the second-to-last section, deleting it renumbers what's
currently §13 ("Commit discipline") down to §12 — every place that names it as
"§13" or links to `#13-commit-discipline` needs updating. This task owns that
whole renumbering ripple; `P06-T09` (which rewrites the commit-discipline
section's *content*) is written to check the section's live number/anchor at
implementation time rather than assume, so the two tasks can run in either
order.

## Implementation

### Objective

Delete workflow.md §12 except its single-active-item constraint, which moves
into §11; renumber the former §13 to §12 and fix every reference to it.

### In scope

- workflow.md §11 (add the constraint sentence), §12 (delete), and the section
  currently numbered §13 (renumber heading + anchor to §12).
- Every `§13` / `#13-commit-discipline` reference across `workflow.md` itself
  and all `skills/*/SKILL.md` files that point at the commit-discipline
  section.

### Out of scope

- The commit-discipline section's actual content — that's `P06-T09`'s scope
  entirely; this task only renumbers its heading and fixes references to it.
- `workflow-medium.md` — it has its own independent section numbering; not
  touched by this task (its §12/§13 aren't affected by a change to the full
  profile's `workflow.md`).

### Files to modify

- `workflow.md` — §11 (add sentence), §12 (delete), §13→§12 (renumber heading
  + internal anchor).
- Every `skills/*/SKILL.md` file that currently links to
  `workflow.md#13-commit-discipline` or says "workflow.md §13" — grep first to
  get the exact list (expected: all 8 full-profile skills, since every one has
  a commit step that cites §13).

### Steps

1. In §11, add one sentence (near the pointer-lifecycle sentence added by
   `P06-T06`, if already present — otherwise as its own addition): "`info.md`
   tracks only one active phase/task by design; genuinely parallel work needs
   each agent tracking its own item some other way until this format supports
   more than one."
2. Delete workflow.md §12 in full: its heading, the "Independent tasks or
   phases may run in parallel..." paragraph, and the `[HUMAN]` comment
   following it.
3. Rename the section currently headed `## 13. Commit discipline` to
   `## 12. Commit discipline`.
4. Grep `workflow.md` for `#13-commit-discipline` and `§13` and update every
   remaining self-reference to `#12-commit-discipline` / `§12`.
5. Grep every `skills/*/SKILL.md` for `#13-commit-discipline` and `§13` (in the
   context of a workflow.md reference, not an unrelated "13") and update each
   to point at `#12-commit-discipline` / `§12`.

### Dependencies

None.

### Expected result

§11 states the single-active-item constraint; §12 no longer exists as
"Multi-agent / multi-human"; the former §13 is now §12 everywhere it's
referenced, with no dangling `#13-commit-discipline` links left anywhere in
the repo.

### Automatic validations

- `grep -rn "13. Commit discipline" workflow.md` returns no matches (renamed).
- `grep -rln "#13-commit-discipline" workflow.md skills/*/SKILL.md` returns no
  matches.
- `grep -n "12. Commit discipline" workflow.md` returns exactly one match.
- `grep -n "info.md.*tracks only one active" workflow.md` returns one match,
  inside §11.

### Manual validations

- Confirm no skill's commit-related instruction now points at a broken or
  wrong anchor.
- Confirm §11 reads coherently with the added sentence, whether or not
  `P06-T06`'s sentence is already present.
