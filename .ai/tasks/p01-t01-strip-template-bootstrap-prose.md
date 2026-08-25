# P01-T01 — Strip bootstrap prose from templates

Phase: [`../phases/p01-efficiency-pass.md`](../phases/p01-efficiency-pass.md).

## Context

See the phase file's Context section for the full research (which
templates carry meta prose, which skills already own the copy
instruction independently). Task-specific addition: the exact
before/after text for each file, captured below so implementation is
mechanical — no need to re-derive line ranges.

## Implementation

**Objective:** Remove agent-facing "copy this to `.ai/X`..." bootstrap
paragraphs from the five templates that carry them, leaving pure
artifact content; keep `decisions-template.md`'s genuine usage-
guidance sentence.

**Files to modify:**

- `templates/info-template.md` — remove the bootstrap paragraph.
- `templates/medium-info-template.md` — remove the bootstrap
  paragraph.
- `templates/lite-project-template.md` — remove the bootstrap
  paragraph.
- `templates/minimal-tasks-template.md` — remove the bootstrap
  paragraph.
- `templates/decisions-template.md` — remove only the "copy this"
  sentence, keep the usage-guidance sentence that follows it.

**Files to create:** none.

**Steps:**

1. In `templates/info-template.md`, delete this paragraph (currently
   lines 3–8, immediately under `# Info`) and the blank line after
   it, so the heading is followed directly by `## Policy...`:
   ```
   Copy this to `.ai/info.md` in your project and edit — this file is
   yours, never touched by a submodule update. It's read at the start of
   every operation (see `.ai/workflow/workflow.md §2`) — always read it
   fresh, never rely on what you saw earlier in a session; it can change
   mid-session and stale memory of it is exactly what causes a gate to
   get ignored.
   ```
2. In `templates/medium-info-template.md`, delete the equivalent
   paragraph (currently lines 3–8, under `# Info (medium profile)`)
   and the blank line after it, so the heading is followed directly by
   the ` ```yaml\nprofile: medium...` block:
   ```
   Copy this to `.ai/info.md` in your project and edit — this file is
   yours, never touched by a submodule update. It's read at the start of
   every operation (see `.ai/workflow/workflow-medium.md §2`) — always
   read it fresh, never rely on what you saw earlier in a session; it can
   change mid-session and stale memory of it is exactly what causes a
   gate to get ignored.
   ```
3. In `templates/lite-project-template.md`, delete this paragraph
   (currently lines 3–7, under `# Project: {name}`) and the blank line
   after it, so the heading is followed directly by the ` ```yaml`
   block:
   ```
   Copy this to `.ai/project.md` in your project and edit — this is the
   **only** workflow file a lite-profile project has. Read it fresh at
   the start of every operation; it can change between sessions and a
   stale read is what causes a gate to get silently ignored. Full rules:
   [`.ai/workflow/skills/workflow-lite/SKILL.md`](.ai/workflow/skills/workflow-lite/SKILL.md).
   ```
4. In `templates/minimal-tasks-template.md`, delete this paragraph
   (currently lines 3–7, under `# Tasks: {name}`) and the blank line
   after it, so the heading is followed directly by the ` ```yaml`
   block:
   ```
   Copy this to `.ai/tasks.md` in your project and edit — this is the
   **only** workflow file a minimal-profile project has. Read it fresh at
   the start of every operation; it can change between sessions and a
   stale read is what causes a gate to get silently ignored. Full rules:
   [`.ai/workflow/skills/workflow-minimal/SKILL.md`](.ai/workflow/skills/workflow-minimal/SKILL.md).
   ```
5. In `templates/decisions-template.md`, the opening paragraph
   (currently lines 3–5, under `# Decisions`) is:
   ```
   Copy this to `.ai/decisions/decisions.md` in your project. One row per
   ADR. Check here before writing a new one — a related decision may
   already exist (see `.ai/workflow/workflow.md §7`).
   ```
   Remove only the leading sentence "Copy this to
   `.ai/decisions/decisions.md` in your project." — the paragraph
   becomes:
   ```
   One row per ADR. Check here before writing a new one — a related
   decision may already exist (see `.ai/workflow/workflow.md §7`).
   ```
6. Leave `templates/context-template.md` and `templates/adr-template.md`
   untouched — confirmed clean, no meta prose to remove.
7. Re-read `skills/create-constitution-full/SKILL.md`,
   `skills/create-constitution-medium/SKILL.md`,
   `skills/workflow-lite/SKILL.md`, `skills/workflow-minimal/SKILL.md`
   after the edits above and confirm each still independently states
   its destination path and "copy ... unedited" instruction without
   depending on anything just removed. No edit expected; if one of
   them turns out to depend on removed text, stop and report it as a
   deviation rather than silently patching around it.
8. `grep -rn "Copy this to" README.md workflow.md workflow-medium.md
   skills/` and confirm no result references the removed text (the
   research already found none; this is a final confirmation, not a
   fresh search).

**Dependencies:** none — this task is self-contained text edits, no
other task in this phase to sequence against.

**Expected result:** the five templates hold only real artifact
content; every copying skill remains independently sufficient;
nothing else in the repo references the removed text.

**Validation instructions:**

1. `grep -n "Copy this to" templates/*.md` → zero matches.
2. Open each of the five edited templates and confirm it reads
   cleanly: heading, then immediately real content, no orphaned blank
   paragraph.
3. `git diff --stat` for this task's changes touches exactly the five
   `templates/*.md` files listed above (plus whatever step 7/8 above
   turns up, if anything — expected: nothing).
4. Confirm `templates/context-template.md` and `templates/adr-template.md`
   are unchanged.
