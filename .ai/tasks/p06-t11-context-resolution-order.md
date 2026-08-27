# P06-T11: Add an explicit context-resolution search-order rule

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
From `feedback.md`'s "Execution" idea: "The task should first read the context,
and before reading any other document inside the codebase to find context, it
should follow the links of the context. The same thing for the phase." §4
already states a general read order ("Read: `info.md` → the artifact defining
current work → direct references → further links only if genuinely needed. A
link is a pointer, not a preload.") — what's missing is the explicit
prohibition: don't go searching the codebase for context beyond what's linked.
This task adds that clarification; it's new content, not a trim.

## Implementation

### Objective

Add one explicit sentence to workflow.md §4 stating that context resolution
follows the task/phase file's own links first, and doesn't fall back to
searching the codebase for context docs.

### In scope

- One new sentence in §4, immediately after the existing "Read: `info.md` →
  ... A link is a pointer, not a preload." sentence.

### Out of scope

- Any change to the existing read-order sentence itself.
- `P06-T01`'s edit to a different paragraph in §4 (the "what a phase is"
  paragraph, further down) — no overlap, different sentence.

### Files to modify

- `workflow.md` — §4.

### Steps

1. Locate the sentence in §4: "Read: `info.md` → the artifact defining current
   work → direct references → further links only if genuinely needed. A link
   is a pointer, not a preload."
2. Immediately after it, add: "Resolve context by following the task or phase
   file's own links first — don't search the rest of the codebase for context
   documents it doesn't already point to; if the context you need isn't linked
   from where you're working, that's a gap in the task/phase file, not a cue to
   go looking elsewhere." (flexible: exact wording, binding: the rule itself —
   follow links first, don't search the codebase speculatively for context).

### Dependencies

None.

### Expected result

§4 explicitly forbids codebase-wide context-searching as a substitute for
following the task/phase file's own links.

### Automatic validations

- `grep -n "don't search the rest of the codebase for context" workflow.md`
  returns one match.

### Manual validations

- Confirm the new sentence reads as a context-*resolution* rule specifically,
  not a blanket ban on using terminal tools for other purposes (e.g. structure
  discovery) — the two concerns are distinct and shouldn't read as
  contradictory regardless of what `P06-T12` does to §1's structure-discovery
  principle.
