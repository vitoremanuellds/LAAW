# P06-T04: Relocate the gate-skip/scope-overstep bug-traced lesson to reference/

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 4: workflow.md §2's instruction to open and read the matching skill file
every operation currently justifies itself inline — "Gate-skip and scope-overstep
bugs traced back to this step being skipped, every time." That's a hard-won,
bug-traced lesson, the same category the file elsewhere preserves in `reference/`
(see `reference/directory-and-links.md`'s own bug-traced stories) rather than
deleting outright. This task moves it out of workflow.md's always-read path
without losing it.

## Implementation

### Objective

Remove the justification sentence from workflow.md §2; preserve it in a new
`reference/` file, linked from §2, following this repo's existing reference-file
convention.

### In scope

- The sentence in workflow.md §2 item 2.
- A new `reference/` file holding that lesson.
- The inbound link from §2 to the new file (every reference file needs one — an
  orphaned reference file is treated as a bug per
  `.ai/context/workflow-doc-conventions.md`).

### Out of scope

- Any change to `reference/directory-and-links.md` or `reference/status-and-info.md`
  beyond reading them to confirm the established convention.
- The rest of §2 item 2 (the instruction to open and read the skill file itself
  stays exactly as it is — only its justification clause moves).

### Files to modify

- `workflow.md` — §2 item 2: remove the justification sentence, add a link.

### Files to create

- `reference/reread-skill-discipline.md` — new reference file holding the lesson.

### Steps

1. Read `reference/directory-and-links.md` and `reference/status-and-info.md` to
   confirm the established convention: open with a "referenced from workflow.md
   §N" pointer, hold only rationale/lookup detail not needed on every read.
2. Create `reference/reread-skill-discipline.md` following that convention: open
   with "Referenced from workflow.md §2." then state the lesson — gate-skip and
   scope-overstep bugs have repeatedly traced back to a skill file being skipped
   or half-remembered rather than freshly read, which is why every operation
   re-reads its skill file in full even when the agent believes it already knows
   the procedure (flexible: exact phrasing, as long as the lesson and its
   consequence are both stated).
3. In workflow.md §2 item 2, remove the sentence "Gate-skip and scope-overstep
   bugs traced back to this step being skipped, every time," and add a link to
   the new file in the same style §3 uses for its `reference/directory-and-links.md`
   link (e.g. "See [reference/reread-skill-discipline.md](reference/reread-skill-discipline.md)
   for why.").
4. Remove the `[HUMAN]` comment line following item 2 in §2 (it's now addressed).
5. Check `.ai/context/workflow-doc-conventions.md` for a maintained list of
   `reference/` files; if one exists, add this file to it.

### Pseudocode

Not needed — text relocation only.

### Dependencies

None.

### Expected result

workflow.md §2 item 2 states only the rule (re-read the skill file, every
operation) plus a link; the justification lives in
`reference/reread-skill-discipline.md`, which nothing outside this task's new
link references it from is missing.

### Automatic validations

- `grep -n "Gate-skip and scope-overstep" workflow.md` returns no matches.
- `test -f reference/reread-skill-discipline.md` succeeds.
- `grep -n "reread-skill-discipline" workflow.md` returns at least one match.

### Manual validations

- Confirm the new reference file reads consistently in tone and format with
  `reference/directory-and-links.md` and `reference/status-and-info.md`.
- Confirm §2 item 2 still reads naturally with the sentence removed.
