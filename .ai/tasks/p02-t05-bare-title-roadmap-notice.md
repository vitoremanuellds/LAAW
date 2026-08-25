# P02-T05 — Bare-title roadmap-append notice

Phase: [`../phases/p02-workflow-doc-precision.md`](../phases/p02-workflow-doc-precision.md).

## Context

See phase file Context (item F) — noticed directly from this session:
`create-constitution-full` appended P02 to `roadmap.md` as a
title-only row, with all the actual detail living only in conversation
until `define-phase` captured it later. If a session ends between
those two moments, that detail is gone unless restated. Doc-only fix,
no new gate or mechanism.

Insertion point identified in `README.md`: right after the "From
there the normal loop is..." paragraph (ends at what's currently line
211, before "## Updating the workflow") — a natural place since it's
already describing the full-profile loop phase-by-phase.

## Requirements

1. `create-constitution-full/SKILL.md`'s step for writing/updating
   `roadmap.md` tells the user, when a bare title-only phase row is
   added, that full planning happens next via `define-phase`, and
   invites them to share context now — noting a cleared session before
   that point may lose context stated only in conversation.
2. `README.md` documents the same thing, placed where a human reading
   the bootstrap/lifecycle docs would actually see it.

## Implementation

**Objective:** Make the context-loss risk between "phase title added"
and "phase fully planned" visible to the user, at the moment it
matters, in both the skill's own behavior and the human-facing docs.

**Files to modify:**

- `skills/create-constitution-full/SKILL.md` — step 6 (roadmap.md
  writing).
- `README.md` — insert after the "normal loop" paragraph, before
  "## Updating the workflow."

**Files to create:** none.

**Steps:**

1. In `skills/create-constitution-full/SKILL.md` step 6, add: when
   adding a phase row that doesn't yet have its own `.ai/phases/`
   file, tell the user that full planning (Context/Requirements/Plan/
   Validations) happens next via `define-phase`, and ask if they want
   to share any context/detail now — a cleared session before that
   planning step may lose context stated only in conversation.
2. In `README.md`, insert a short paragraph after the existing "normal
   loop" paragraph (full profile): a phase starts in `roadmap.md` as a
   title-only row; full detail is captured separately by `define-phase`
   only once that row is reviewed; if useful context already exists,
   say so when the row is added rather than waiting, since a session
   ending between those two steps can lose anything not yet captured
   in a file.

**Dependencies:** none among P02-T02..T05.

**Expected result:** the skill proactively surfaces this risk to the
user at the moment a bare phase row is added; `README.md` explains why,
for anyone reading the docs rather than experiencing it live.

**Validation instructions:**

1. Read `create-constitution-full/SKILL.md` step 6 — confirm the new
   instruction is present and would actually fire at the right moment
   (bare row added, not the initial full-roadmap write where every
   phase is stubbed at once and none have a file yet either — decide
   during implementation whether the notice applies to that case too,
   and make the instruction's scope explicit either way, not
   ambiguous).
2. Read the new `README.md` paragraph in context — confirm it reads
   naturally where it's placed and doesn't duplicate the surrounding
   paragraphs.
3. Confirm zero changes outside the two files listed above.
