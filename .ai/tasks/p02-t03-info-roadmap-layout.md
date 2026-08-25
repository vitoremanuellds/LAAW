# P02-T03 — info.md/roadmap.md layout fix

Phase: [`../phases/p02-workflow-doc-precision.md`](../phases/p02-workflow-doc-precision.md).

## Context

See phase file Context (item D). `medium-info-template.md`
(`profile: medium`), `lite-project-template.md` (`profile: lite`),
`minimal-tasks-template.md` (`profile: minimal`) already self-identify
via a fixed YAML field right after their heading; `templates/info-template.md`
(full) doesn't. Separately, `templates/info-template.md`'s Status
section currently has its explanation *after* the Status code block —
reorder so the block is the true tail. The same pattern (trailing note
after a table) exists in this project's own
`.ai/constitution/roadmap.md`, generated per
`create-constitution-full` step 6's current instructions, which don't
specify ordering.

**Scope includes fixing this project's own already-generated
`.ai/info.md` and `.ai/constitution/roadmap.md`** to match, not just
the template/skill instructions for future projects — trivial, safe
change, and leaving our own dogfooded files in the "before" state
while only fixing the instruction going forward would be inconsistent.

## Requirements

1. `templates/info-template.md` has `profile: full` as a fixed YAML
   field immediately after the `# Info` heading (matching the
   medium/lite/minimal convention).
2. `templates/info-template.md`'s Status section's explanatory prose
   precedes its code block, not follows — the code block is the last
   thing in the file.
3. `skills/create-constitution-full/SKILL.md` step 6 instructs writing
   `roadmap.md` with any explanatory/intro prose before the table, the
   table as the file's last element — not after, as currently happens.
4. `.ai/info.md` and `.ai/constitution/roadmap.md` (this project's own
   live artifacts) are updated to match both fixes above.

## Implementation

**Objective:** `profile: full` self-identification in `info.md`, plus
consistent "explanation before block/table, not after" layout in both
`info-template.md` and `roadmap.md`'s generation instructions —
applied to this project's own files too.

**Files to modify:**

- `templates/info-template.md`
- `skills/create-constitution-full/SKILL.md` (step 6)
- `.ai/info.md`
- `.ai/constitution/roadmap.md`

**Files to create:** none.

**Steps:**

1. In `templates/info-template.md`, add right after `# Info`:
   ```
   ```yaml
   profile: full   # fixed — this file is only ever used for the full profile
   ```
   ```
2. In the same file, move the Status section's trailing paragraph
   ("IDs only, no status values...") to precede its ` ``` ` code
   block, so the block ends the file.
3. In `skills/create-constitution-full/SKILL.md` step 6, add an
   explicit instruction: write any explanatory/intro prose about the
   roadmap before the table; the table is the file's last element.
4. Apply the same two structural fixes to `.ai/info.md` (add
   `profile: full`; reorder its Status section) — this file was
   already bootstrapped from the old template shape, so it needs the
   same edit the template just got, not a re-copy.
5. Reorder `.ai/constitution/roadmap.md`: merge its trailing note
   ("No detail beyond the title lives here...") into the existing
   intro paragraph before the table, leaving the table as the file's
   last element.

**Dependencies:** none among P02-T02..T05.

**Expected result:** `info.md` (template and this project's own copy)
states its profile and ends with its Status block; `roadmap.md` (this
project's own copy, and future ones per the updated skill instruction)
ends with its table, explanatory prose ahead of it.

**Validation instructions:**

1. `head -5 templates/info-template.md` and `head -5 .ai/info.md` both
   show the `profile: full` YAML block right after the heading.
2. Both files' Status section: the code block is the last content in
   the file (nothing trails it).
3. `.ai/constitution/roadmap.md`: the table is the last content in the
   file; the merged intro paragraph still contains everything the
   original trailing note said (no information lost, just reordered).
4. `skills/create-constitution-full/SKILL.md` step 6 explicitly says
   prose-before-table.
5. Confirm zero changes outside the four files listed above.
