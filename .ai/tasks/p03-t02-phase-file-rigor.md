# P03-T02 — Phase-file rigor: In-scope/Out-of-scope + Automatic/Manual validations

Phase: [`../phases/p03-spec-rigor-and-loop.md`](../phases/p03-spec-rigor-and-loop.md).

## Context

See phase file Context (T01's propagated note) and Plan step 2. Same
treatment as T01, at phase granularity: `define-phase`'s output
structure and `validate-work-full`'s phase-validation procedure.
**Not in scope here:** a phase-level "flexible detail" marking
convention — phases don't have literal implementation steps (a
phase's Plan section is explicitly required *not* to read like a task
list, `workflow.md §4`); that granularity is task-only and T01 already
covers it. Phase-level rigor is scope boundaries + validation split
only, nothing about adjustable-vs-binding detail.

## In scope

- `define-phase/SKILL.md` step 2: add In scope/Out of scope sections
  to the phase file it instructs writing (placed after Context, before
  Requirements — same position T01 used in this very phase's own
  file).
- `define-phase/SKILL.md` step 2: split Validations into Automatic
  validations / Manual validations.
- `validate-work-full/SKILL.md`'s phase-validation procedure: run
  Automatic validations first (mechanical, as written), then Manual
  (judgment), and report them as two separate groups, not one merged
  verdict.
- `README.md` line ~330 (the "Full:" directory-tree comment
  enumerating a phase file's sections): update to stay accurate.

## Out of scope

- Task-level rigor — already done, P03-T01.
- A phase-level equivalent of the `(flexible: ...)` marker — doesn't
  apply at this granularity (see Context above).
- Retroactively rewriting P01/P02's already-complete phase files.
- `workflow-medium.md`, `skills/*-medium/`, `workflow-lite/SKILL.md`,
  `workflow-minimal/SKILL.md`, or their templates.
- `workflow.md` itself — no section there enumerates a phase file's
  exact section list in a way that needs updating (checked: §3 and §4
  use short, deliberately abbreviated forms like "own Context + task
  table," not a full enumeration — only `README.md`'s tree comment
  spells it out in full).

## Implementation

**Objective:** Give phase files the same explicit scope boundary and
split validation section that P03-T01 gave task files.

**Files to modify:**

- `skills/define-phase/SKILL.md` — step 2.
- `skills/validate-work-full/SKILL.md` — "Procedure — phase
  validation."
- `README.md` — the phase-file section-list tree comment.

**Files to create:** none.

**Steps:**

1. In `define-phase/SKILL.md` step 2's section list, insert **In
   scope** and **Out of scope** immediately after **Context**, before
   **Requirements**: In scope — a short bullet list of exactly what
   this phase covers. Out of scope — a short bullet list of adjacent
   things this phase deliberately does *not* cover (things a reader
   might otherwise assume are included, given the title/Context) —
   name a separate phase explicitly where relevant, same pattern this
   phase's own file already uses.
2. In the same list, replace the single **Validations** bullet with
   two: **Automatic validations** (mechanically checkable — a command,
   a grep, a test run) and **Manual validations** (requires a human or
   agent judgment call — architecture coherence, whether scope was
   actually honored). Both present where applicable, never merged.
3. In `validate-work-full/SKILL.md`'s "Procedure — phase validation":
   update step 2 to read the phase file's Automatic validations and
   Manual validations sections (not one "Validations" section); update
   step 3 to run every Automatic item first, exactly as written, then
   work through Manual items with judgment (cross-task/integration
   checks belong in the Manual pass); update step 4 to report pass/fail
   grouped by Automatic vs. Manual, not merged into one verdict.
4. In `README.md`, update the "Full:" tree comment for `p01-name.md`
   from "own Context + Requirements + Plan + Validations + task table"
   to reflect the new section list (Context + In/Out of scope +
   Requirements + Plan + Automatic/Manual validations + task table).
5. Confirm `workflow.md`'s heading list is unchanged (this task
   doesn't touch `workflow.md` at all — verify nothing crept in).

**Dependencies:** none beyond P03-T01 (already complete) — same
sequencing note as the phase Plan (T02 depends on T01 having
established the conventions being mirrored here).

**Expected result:** `define-phase` generates phase files with
explicit In-scope/Out-of-scope and split Automatic/Manual validations;
`validate-work-full` runs and reports them as two distinct groups;
`README.md`'s structural description stays accurate.

**Automatic validations:**

1. `grep -n "In scope\|Out of scope\|Automatic validations\|Manual validations" skills/define-phase/SKILL.md` — all four present in step 2.
2. `grep -n "Automatic\|Manual" skills/validate-work-full/SKILL.md` — both appear in the phase-validation procedure, not just the task-validation one.
3. `grep -n "In/Out of scope\|Automatic/Manual" README.md` (or equivalent updated phrasing) — the tree comment reflects the new sections.
4. `git diff --stat` for this task's commit touches exactly `skills/define-phase/SKILL.md`, `skills/validate-work-full/SKILL.md`, `README.md` — nothing under `workflow.md` or any medium/lite/minimal path.

**Manual validations:**

1. Read the updated `define-phase/SKILL.md` step 2 and judge whether a
   phase file drafted under it would read as more scope-bounded than
   before — In scope/Out of scope narrows rather than restates the
   Plan.
2. Read `validate-work-full/SKILL.md`'s updated phase procedure and
   confirm the Automatic-then-Manual sequencing and separate reporting
   actually make sense as written, not just present as labels.
