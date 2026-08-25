# P04 — Brownfield context-building skill

Roadmap entry: `.ai/constitution/roadmap.md`.

## Context

For a project that hasn't been bootstrapped yet, or was bootstrapped
recently and has little in `.ai/context/`, there's currently no
structured way to populate it from an existing codebase — the only
guidance is `workflow.md §9`'s propagation rules, which assume context
accumulates from *doing* phases/tasks, not from surveying a codebase
that already exists. The user described a specific iterative process,
directly, in detail:

1. The agent looks at the project's files — **listing only, no
   reading file contents** — and writes an assumptions document:
   inferred structure, purpose, and mission, explicitly marked as
   assumptions/questions, not asserted fact.
2. The human can annotate that document — correcting, confirming, or
   commenting — but must **never delete** what the agent wrote or
   asked. The record of "what was assumed" has to survive intact even
   after correction.
3. From the (possibly annotated) assumptions, the agent builds an
   **ordered iteration plan**: which files to actually read, in what
   order, in batches — **the human chooses the batch size**.
4. Each iteration reads that batch and builds real `.ai/context/`
   content from it (following the existing `context.md` convention
   already in place, `.ai/context/workflow-doc-conventions.md`).
5. The iteration plan tracks status per file (queued vs. read) and the
   process ends when the queue is empty.

This is a genuinely new capability, not a refinement of an existing
skill (unlike P03) — it needs its own entry in `workflow.md §2`'s
skill-lookup table (one new row; the table itself isn't restructured,
per the heading/structure-stability convention).

Requires a project already bootstrapped at least to the point
`.ai/info.md` and `.ai/context/context.md` exist (`create-constitution-full`
has run) — this skill grows `context/`, it doesn't bootstrap the
project from nothing.

## In scope

- A new skill (working name `build-context-full`) with distinct
  sub-operations mirroring `propagate-context`'s shape: an assumption
  pass (listing-only), a plan-from-assumptions step, and a repeatable
  iterate-and-build step.
- A template for the assumptions document, with an explicit
  Assumption/Question marker convention that makes "never delete this"
  unambiguous to a human editing it.
- An iteration-plan artifact with a per-file queued/read status
  tracker, and a user-configurable batch size.
- One new row in `workflow.md §2`'s skill-lookup table.

## Out of scope

- Making this a mandatory step of `create-constitution-full` or any
  existing bootstrap flow — it's an available, opt-in operation, not a
  forced one.
- Medium/lite/minimal profiles — Full only, same precedent as
  P01–P03. Medium also has `context/context.md`; a medium-profile
  version is a plausible future phase, not this one.
- Retroactively running this against this repo's own already-populated
  `.ai/context/` — nothing stops someone from trying it here later,
  but it's not part of this phase's deliverable or validation.
- A general "re-sync context when the codebase changes" mechanism —
  this phase is about building context for a project that doesn't have
  much yet, not ongoing drift detection (that's closer to P05's
  territory, and not merged with it here).

## Requirements

1. The assumption pass reads only file/directory *listings* (`tree`,
   `find`, `ls` — no `cat`/`Read` of file contents) and produces an
   assumptions document with every claim explicitly marked as an
   assumption or a question, never asserted as verified fact.
2. The marker convention makes it unambiguous, to a human editing the
   file, that agent-written assumptions/questions must not be deleted —
   only annotated. Stated both in the skill and in the document itself.
3. The iteration plan's read order is reasoned (e.g., entry points and
   config files first, since they're most informative for correcting
   assumptions early), not an arbitrary file listing.
4. The iteration plan has an explicit status tracker (queued/read per
   file), updated after every iteration — not implied or reconstructed
   from memory.
5. Batch size (how many files get read per iteration) is a value the
   human sets, not fixed by the skill.
6. Each iteration reconciles what was actually read against the
   assumptions document — confirming, correcting, or flagging
   discrepancies — not just appending new `context/*.md` content
   while ignoring what was assumed.
7. The process is explicitly bounded: it ends when the read queue is
   empty. No open-ended "keep exploring" mode.
8. `workflow.md §2`'s skill-lookup table has a new row for this skill;
   no other structural change to that section.
9. Zero changes outside the Full profile.

## Plan

1. Design and write the new skill (`skills/build-context-full/SKILL.md`):
   its sub-operations (assumption pass; plan-from-assumptions;
   iterate-and-build, repeatable), when to use it, its inputs/outputs,
   and how it reads `.ai/info.md`'s gate authority the same way every
   other skill does.
2. Design the assumptions-document template
   (`templates/context-temp-template.md`): the Assumption/Question
   marker convention, structure (project purpose/mission, inferred
   architecture, open questions), and the "never delete, only annotate"
   instruction stated in the file itself.
3. Design the iteration-plan artifact: format, location, the
   queued/read status tracker, and where batch size gets recorded.
4. Add the new skill's row to `workflow.md §2`'s lookup table.

Steps 1–4 are one cohesive design effort (they define one skill's
shape together) rather than independent slices — task breakdown
decides whether that's one task or several once the design is
concrete enough to see the natural seams.

## Automatic validations

- `grep -n "sub-operation\|assumption\|iteration" skills/build-context-full/SKILL.md` (or equivalent) confirms all three stages are named and documented.
- `grep -n "build-context-full" workflow.md` confirms the new
  lookup-table row exists; `grep -n "^## "` before/after confirms no
  heading changed.
- `templates/context-temp-template.md` (or the chosen name) exists and
  states the never-delete-only-annotate convention explicitly.
- `git diff --stat` for the whole phase touches only the new skill
  directory, the new template(s), and `workflow.md`'s lookup table —
  nothing under `workflow-medium.md`, `skills/*-medium/`,
  `workflow-lite/SKILL.md`, `workflow-minimal/SKILL.md`, or their
  templates.

## Manual validations

- Read the assumption-pass instructions and judge whether they'd
  actually produce an honestly-hedged document (real assumptions
  marked as such) rather than confidently-asserted claims dressed up
  with a label.
- Read the iteration-plan's ordering rationale and judge whether
  reading entry points/configs first is sound, or whether a different
  default order would serve better for a typical project.
- Confirm the human-annotation convention is clear enough that someone
  who's never seen this skill before would understand, from the
  document alone, not to delete agent content.

## Tasks

| ID | Title | Purpose | Depends on | Status |
|---|---|---|---|---|
| P04-T01 | Design and write the build-context-full skill | Plan steps 1-4: the skill (3 sub-operations), 2 templates, workflow.md §2/§10 wiring | — | awaiting-plan-review |
