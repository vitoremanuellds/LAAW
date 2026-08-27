# P06-T12: Apply remaining confirmed-safe trims (opening/§1, §3, §4 glossary, §9)

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Four small, independent, already-confirmed-safe edits that don't warrant their
own tasks: trimming the opening/§1 per the file's own "rules here, rationale in
reference/" design; dropping a redundant "this is a fix" clause in §3 (the
story already lives in `reference/directory-and-links.md`); adding a short
phase/task glossary line to §4; and trimming §9's now-redundant how-to prose
(`propagate-context` already operationalizes it), while keeping its bug-traced
rationale and its Propagate/Never criteria intact.

## Implementation

### Objective

Apply the four confirmed-safe trims below, each independently, without losing
any rule, rationale, or bug-traced lesson — only redundant or filler prose
should be removed.

### In scope

- **Opening/§1**: shorten the intro to state the no-duplication rule and the
  `reference/` pointer; drop the "Procedural how-to lives in skills/... Gate
  authority lives in info.md" sentence (redundant with the §2 table and §5);
  drop §1 principle 4 (using terminal tools to discover structure — generic
  agent competence, not a workflow-specific rule).
- **§3**: drop the clause "each is the fix for a bug that actually happened,
  not a stylistic preference" — the story is already told in full in
  `reference/directory-and-links.md`; keep "See reference/directory-and-links.md
  for why both rules exist."
- **§4**: add a short glossary line after the "what a phase is" paragraph.
- **§9**: replace the last sentence of the paragraph starting "No lateral
  shared-context files exist (§4)..." — the part instructing to update
  `context/context.md`'s table — with a pointer to `propagate-context`, since
  that skill already states this exact step. Keep everything else in §9
  unchanged, including the "this happened in practice and produced context/
  that skipped review" bug-traced clause and the Propagate/Never lists — those
  are a rule and its rationale, not how-to, and stay.

### Out of scope

- Any other section of workflow.md.
- `reference/directory-and-links.md` — read-only, to confirm it still tells
  the "fix for a bug" story before cutting the teaser clause from §3.
- `propagate-context`'s own content — verified already correct; not edited by
  this task.

### Files to modify

- `workflow.md` — opening/§1, §3, §4, §9.

### Steps

1. **Opening/§1**: Replace the current opening (from "# Agent Workflow" through
   the end of §1) with:
   ```
   # Agent Workflow

   Source of truth for how work is organized, performed, and by whom. Do not
   duplicate this file's rules elsewhere — reference it. Detailed rationale,
   lookup tables, and historical context that's genuinely occasional-need
   lives in `reference/`, one file per concept, linked from the specific place
   below that needs it.

   ---

   ## 1. Principles

   1. Agents do not reconstruct information that can be persisted cheaply.
   2. Persist knowledge, not reasoning.
   3. Read only what the current task needs. Never load the whole `.ai/` tree
      speculatively.
   ```
   Remove both `[HUMAN]` comments from this region along with the text they
   were commenting on.
2. **§3**: Change "See [reference/directory-and-links.md](reference/directory-and-links.md)
   for why both rules exist — each is the fix for a bug that actually happened,
   not a stylistic preference." to "See
   [reference/directory-and-links.md](reference/directory-and-links.md) for why
   both rules exist." Remove the `[HUMAN]` comment following it.
3. **§4**: Immediately after the "what a phase is" paragraph (ending "...for
   the same reason)."), add: "**Quick reference:** `phase` — a
   feature/capability-sized slice of work with its own Context and Plan;
   `task` — one mechanical, close-to-implementable unit of work within a
   phase's Plan." Remove the `[HUMAN]` comment this addresses.
4. **§9**: In the paragraph "No lateral shared-context files exist (§4) — a
   fact belongs in the specific phase/task file, or gets promoted to
   `context/`. Touching `context/` means updating its row in
   `context/context.md`'s table in the same step," replace the last sentence
   with "See `skills/propagate-context/SKILL.md` for the exact procedure."
   Remove the three `[HUMAN]` comment lines in §9 (they're all addressed by
   this same trim).

### Dependencies

None.

### Expected result

Four independent trims applied; no rule, rationale, or bug-traced lesson lost;
`propagate-context`'s content unchanged (it already covers what §9 now points
to instead of restating).

### Automatic validations

- `grep -n "no separate structure map to maintain" workflow.md` returns no
  matches (§1 principle 4 removed).
- `grep -n "each is the fix for a bug" workflow.md` returns no matches.
- `grep -n "Quick reference.*phase.*task" workflow.md` returns one match in §4.
- `grep -n "updating its row in" workflow.md` returns no matches (§9's last
  sentence replaced).
- `grep -c "\[HUMAN\]" workflow.md` — count drops by exactly the number of
  `[HUMAN]` comments this task addresses (2 in opening/§1, 1 in §3, 1 in §4,
  3 in §9 = 7).

### Manual validations

- Confirm the shortened opening still states the no-duplication rule clearly.
- Confirm §9's bug-traced "this happened in practice" clause and its
  Propagate/Never lists are still present, unchanged — only the how-to
  sentence at the end was replaced.
- Confirm the §4 glossary line reads as a helpful summary, not a restatement
  that makes the paragraph above it redundant.
