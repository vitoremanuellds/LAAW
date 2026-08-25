# P02-T01 — Restructure workflow.md into core + reference/

Phase: [`../phases/p02-workflow-doc-precision.md`](../phases/p02-workflow-doc-precision.md).

## Context

See the phase file's Context (item A+B) for the full rationale. This
task's addition: a concrete, section-by-section categorization of
`workflow.md`'s current 13 sections, worked out during task planning
so implementation is close to mechanical rather than a from-scratch
judgment call.

**Classification rule:** a passage stays in **core** if it's a rule or
definition an agent needs on essentially every operation, and it's
short. It moves to **reference** if it's genuinely occasional-need
(rationale, historical-incident explanation, a lookup table consulted
only when uncertain) — one file per concept, per the user's explicit
choice, exact file boundaries decided during implementation based on
what actually doesn't fit in trimmed core (don't force a
predetermined file count). It's **deleted outright** (not moved) only
if it's step-by-step procedure already fully duplicated in a skill's
own Procedure section — moving dead-duplicate content to reference
would just give it a second home for no reason.

**Per-section starting point** (confirm each against the actual current
text at implementation time — this is a plan, not a diff):

- §1 Principles — core, unchanged.
- §2 Starting point for any agent — core, unchanged. This is a
  standing rule ("read info.md fresh, open the matching skill"), not a
  task-specific how-to, despite being phrased as steps.
- §3 Directory structure — core keeps: the tree diagram, naming
  conventions, size target, and a **short** (1–2 sentence) warning
  that paths must be `.ai/`-prefixed. Reference gets: the full
  "bare/dot-relative path caused a phase file outside `.ai/`"
  incident story, and the full "Link rule" rationale (the
  `sync-skills.sh` mirroring story) — core keeps just the rule itself
  ("skill cross-references use `.ai/workflow/`-anchored paths, not
  dot-relative") with a pointer to reference for why.
- §4 Artifact hierarchy & context rule — core, unchanged (already
  tight; the "what is a phase" paragraph is short and needed often
  enough to stay).
- §5 Lifecycle & gates — core keeps: the lifecycle diagram, the new
  compact gate list (format below), execution modes, "gates block
  advancing not producing," "each gate unlocks only the next,"
  "unlocking ≠ starting," and the Task/Phase-complete-requires bullet
  lists (all already short). **Delete outright** (not move): the
  "Diagram label / Gate key / Distinct from" table — the new compact
  list format supersedes it; keeping both would be redundant, not
  complementary.
- §6 Deviations — core, largely unchanged (already tight). This is
  also where P02-T02 will add the append-vs-replan subsection later —
  leave room but don't draft that content in this task.
- §7 Decisions (ADRs) — core keeps: when to write one, the ownership
  rule, the superseding-ADR rule (all short). **Important nuance,
  verify before touching:** `implement-task-full` already has its own
  full copy of the "check decisions.md, copy template, fill in, add
  index row" procedure, so deleting it from core loses nothing there —
  but `create-constitution-full` and `define-phase` do **not** have an
  equivalent step of their own today (checked directly — neither
  skill's Procedure mentions writing an ADR at all, even though
  `workflow.md §10` requires both Constitution Agent and Phase
  Planning Agent to write ADRs for their own decisions). Re-verify
  this at implementation time (skills may have changed since this was
  checked) and if still true: keep one canonical procedural line for
  ADR-writing in core (or reference, with a pointer skills the other
  two skills can point to) rather than deleting it outright — don't
  let this task silently regress two agents' only source of "how to
  write an ADR."
- §8 Validation vs Review — core, unchanged (two lines).
- §9 Context propagation — core, unchanged (already lean): diagram,
  the propagate/never-propagate lists, "never write to context/
  directly," "no lateral shared-context files." Only trim if a
  specific sentence turns out to be pure incident-story rather than
  rule — check before cutting, don't cut by default.
- §10 Agent contracts — core, unchanged in full. This is exactly
  "what is," already tight per agent.
- §11 Status — core keeps: the fast-pointer/permanent-record
  distinction (short), the status enum diagram, and the "never write a
  status word into `info.md`" rule (this one gets violated in practice
  if dropped — keep it prominent). Reference gets: the "Set by" table
  (8 rows — a lookup table, not a per-operation need; each skill's own
  procedure already states what status it sets, so this table serves
  cross-checking, not routine reads), and the extended
  plan-review-vs-`reviewing` explanation. **Keep in core, as a
  one-line pointer, not silently drop:** the "ID order ≠ execution
  order" caveat — link to wherever its fuller explanation lands in
  reference, but don't remove the warning itself from core; it's
  short and prevents a real category of mistake (see
  `workflow.md §11`'s current text).
- §12 Multi-agent / multi-human — core, unchanged (one paragraph).
- §13 Commit discipline — **stays in core**, not reference. It's
  short (~15 lines) and used by literally every skill's closing step —
  moving it to reference would mean nearly every operation needs both
  core and this one reference file, which defeats the point of the
  split. Light trim of examples is fine; don't relocate the section.

**New gate-list format for §5** (replaces the current prose + table):

```
- `constitution-review` — after the constitution draft. Unlocks phase
  planning.
- `phase-review` — after a phase plan draft. Unlocks task planning for
  that phase only.
- `task-review` — after a task-batch plan draft. Unlocks
  implementation of those tasks only.
- `task-validation` — after implementation. Mechanical: does it meet
  the task's requirements?
- `task-completion-review` — after validation passes. Judgment: is it
  appropriate/coherent? Unlocks marking the task complete.
- `phase-validation` — after every task in a phase is complete.
  Mechanical, phase-wide.
- `phase-completion-review` — after phase validation passes. Judgment,
  phase-wide. Unlocks marking the phase complete.
- `context-update` — evaluating what to propagate; runs alongside
  task/phase completion, not a separate blocking step in the lifecycle
  diagram.
```
Adjust wording as needed once actually placed in context — this is the
shape to hit, not verbatim required text.

## Implementation

**Objective:** Produce a trimmed `workflow.md` (what-is only, new
compact gate list, no how-to duplicated from skills) plus
`.ai/workflow/reference/*.md` holding the relocated occasional-need
material, with every cross-reference across the repo still resolving
correctly afterward.

**Files to modify:**

- `workflow.md` — the restructure itself.
- `skills/create-constitution-full/SKILL.md`,
  `skills/define-phase/SKILL.md`, `skills/define-task-full/SKILL.md`,
  `skills/implement-task-full/SKILL.md`,
  `skills/validate-work-full/SKILL.md`,
  `skills/review-work-full/SKILL.md`,
  `skills/propagate-context/SKILL.md` — fix any
  `.ai/workflow/workflow.md §N`/`#N-...` link whose target moved to
  `reference/` or whose section number changed.
- `README.md` — same cross-reference fix, wherever it links into
  `workflow.md` by section.
- `templates/info-template.md`, `templates/context-template.md`,
  `templates/decisions-template.md`, `templates/adr-template.md` —
  same cross-reference fix if any of them link into `workflow.md` by
  section (check each; not all currently do).

**Files to create:**

- `.ai/workflow/reference/*.md` — final file count/names decided
  during this task based on what doesn't fit trimmed core (see
  Context above); at minimum expect one covering §3's directory/link
  rationale and one covering §11's Set-by table + extended status
  notes, since both are confirmed candidates.

**Steps:**

1. Re-read current `workflow.md` in full (don't rely on the summary
   above — confirm against the actual live text, which may have
   shifted since this task was planned).
2. Draft the trimmed core, section by section, per the classification
   above — including the new §5 gate-list format. Keep section numbers
   stable where content didn't move, to minimize link churn; renumber
   only where a section was fully removed or merged.
3. Draft `.ai/workflow/reference/*.md` for whatever got relocated
   (not deleted) — group by concept per the user's one-file-per-concept
   choice. Each reference file needs a one-line "what this is for"
   opener (reference files get read standalone, out of workflow.md's
   narrative order) and gets linked from the specific core sentence
   that points to it.
4. Resolve the §7 ADR-procedure nuance per Context above: verify
   `create-constitution-full` and `define-phase` still lack their own
   ADR-writing step; if so, either add a short one to each, or keep a
   single canonical instruction in core/reference both can link to —
   don't delete the only copy.
5. Grep every occurrence of `workflow.md §` and `workflow.md#` (and,
   for anything that moved, add the new `reference/*.md#` links) across
   `skills/*-full/*.md`, `README.md`, and the four Full-profile
   templates listed above. Fix every one to point at a real, current
   target.
6. Read the finished core `workflow.md` start-to-finish and confirm no
   step-by-step procedure remains that's a duplicate of a skill's own
   Procedure section (the thing idea B is actually for).
7. Sanity-check size: core should be meaningfully shorter than the
   pre-task line count (`wc -l` before/after, roughly — not a hard
   target).

**Dependencies:** none — this is P02's first task, nothing to sequence
against. P02-T02 (append mechanism) depends on this one landing first.

**Expected result:** `workflow.md` reads as pure "what is," is
noticeably shorter, has a compact gate list, and every cross-reference
anywhere in the repo that used to point into it still resolves.

**Validation instructions:**

1. `grep -rn "workflow\.md §\|workflow\.md#" skills/ README.md templates/`
   — for each hit, open the target and confirm it resolves to real
   content (not a section that moved or was renumbered without the
   link being updated).
2. Read `workflow.md` core end to end — confirm no duplicated
   step-by-step procedure remains, and confirm the §7 ADR-procedure
   nuance was actually resolved (not silently dropped).
3. Confirm `.ai/workflow/reference/` files each have at least one
   inbound link from core — no orphaned reference file.
4. `wc -l workflow.md` before vs. after — core should be materially
   shorter (sanity check, not a hard number).
5. Confirm zero changes under `workflow-medium.md`, `skills/*-medium/`,
   `skills/workflow-lite/`, `skills/workflow-minimal/`, and their
   templates.
