# P03 — Task/phase specification rigor & closing the planning loop

Roadmap entry: `.ai/constitution/roadmap.md`.

## Context

Direct feedback from using P01/P02: task and phase files should read
close to, but not be, the implementation itself — precise enough that
an agent follows them strictly, with flexibility reserved only for
details explicitly marked low-importance, not a general "adjust minor
mismatches" latitude. Two concrete gaps named: (1) task/phase files
don't currently separate "what's in scope" from "what's explicitly
not," and (2) validation is currently one undifferentiated list,
not split into what's mechanically checkable (automatic) vs. what
needs a human's judgment (manual).

Separately, this session demonstrated (informally, for P02) a
lightweight planning entry point that doesn't start from a fully-
formed roadmap: `create-constitution-full` appends a bare title-only
phase row, then `define-phase` drafts the whole phase from the live
conversation — no pre-existing Plan detail required. The user
confirmed this is the pattern they want formalized: "we create the
vision, and then... we plan new features" iteratively, one at a time,
rather than up-front. What's still missing to make this a real loop
rather than a one-off: nothing currently asks, at the moment a task or
phase actually finishes, whether there's more to plan next — the
loop's "implement → plan the next thing" step has no explicit trigger
today; the human has to remember to ask for it.

This phase's own file **uses the target structure being built** (In
scope/Out of scope + Automatic/Manual validations below), even though
`define-phase` doesn't generate that shape yet — this file is also the
worked example.

## In scope

- `define-task-full`'s output structure: explicit In-scope/Out-of-
  scope, and Automatic/Manual validation sections.
- `implement-task-full`'s flexibility language: tightened so only
  details a task file explicitly marks low-importance/adjustable may
  be freely adjusted; anything else that doesn't match triggers a
  deviation (`workflow.md §6`), not a silent adjustment.
- `define-phase`'s output structure: the same two additions, at phase
  granularity.
- `validate-work-full`'s phase procedure: checks Automatic and Manual
  validations explicitly, as distinct steps.
- Documenting the "spontaneous phase planning" pattern (bare roadmap
  row → `define-phase` drafts from conversation) as a named, supported
  way of working, in `workflow.md` and/or `README.md`.
- `propagate-context.task`: a new closing question — does the phase
  need more tasks?
- `propagate-context.project`: a new closing question — does the
  project need another phase?

## Out of scope

- P04's brownfield context-building skill — separate phase, not
  touched here.
- Any change to `workflow-medium.md`, `skills/*-medium/`,
  `workflow-lite/SKILL.md`, `workflow-minimal/SKILL.md`, or their
  templates — Full profile only, same precedent as P01/P02.
- Retroactively rewriting P01/P02's already-complete task/phase files
  to the new structure — the new structure applies going forward, not
  as a backfill.
- Building a task-level equivalent of the bare-title-phase pattern
  (a task with no corresponding Plan-section item at all) — the
  existing append mechanism (P02-T02: `define-phase` appends a Plan
  item, `define-task-full` drafts its task) already covers small
  increments without needing a second new mechanism; only the
  documentation/naming (this phase's Plan step 3) is new.

## Context (accumulated during the phase)

**From T01 (task-file rigor, complete):** the exact wording/placement
conventions to mirror at phase level in T02: In scope/Out of scope go
right after Objective (or the phase-level equivalent); Automatic/Manual
validations replace any single undifferentiated validation list, never
merged; a flexible-detail marker uses the literal form `(flexible: ...)`
inline. Pseudocode-equivalent content (if the Plan section ever has
any) keeps its own separate, unconditional adaptation latitude — don't
fold it into whatever the phase-level marking convention ends up being.

## Requirements

1. A freshly-drafted task file states, explicitly, what's in scope and
   what's out of scope for that task — not left to be inferred from
   the Steps list alone.
2. A freshly-drafted task file's validation is split into **Automatic
   validations** (mechanically checkable: a command, a grep, a test
   run) and **Manual validations** (requires a human or agent judgment
   call that can't be scripted) — both present where applicable, never
   merged back into one undifferentiated list.
3. `implement-task-full` only allows free adjustment for details a
   task file explicitly flags as low-importance/flexible. Anything
   else that doesn't match the plan — even something that used to
   qualify as a "minor mismatch" under the old language — gets raised
   as a deviation instead of silently adjusted.
4. A freshly-drafted phase file states in-scope/out-of-scope and
   splits its Validations section into Automatic/Manual, mirroring
   requirements 1–2 at phase granularity.
5. `validate-work-full`'s phase procedure explicitly runs Automatic
   validations first, then Manual ones, reporting each separately —
   not one merged pass/fail.
6. `workflow.md` and/or `README.md` names the "plan one phase at a
   time, starting from a bare roadmap row, no pre-existing detailed
   Plan required" pattern explicitly, using P02 as the worked example,
   so it reads as an intentional supported mode, not an implicit side
   effect of how `create-constitution-full`/`define-phase` happen to
   compose.
7. `propagate-context.task`, after marking a task complete, asks
   whether the phase needs more tasks — before ending its turn.
8. `propagate-context.project`, after marking a phase complete, asks
   whether the project needs another phase — before ending its turn.
   (This is in addition to, not a replacement for, `create-constitution-full`'s
   existing "anything else to add?" step, which fires *before*
   requesting review, not after completion.)
9. Zero changes outside the Full profile — `workflow-medium.md`,
   `skills/*-medium/`, `workflow-lite/SKILL.md`,
   `workflow-minimal/SKILL.md`, and their templates untouched.

## Plan

1. Redesign task-file rigor: add In-scope/Out-of-scope and
   Automatic/Manual validation sections to `define-task-full`'s
   Procedure (the sections it instructs writing into
   `.ai/tasks/p{NN}-t{NN}-{name}.md`); tighten `implement-task-full`'s
   deviation-vs-adjustment language so only explicitly-flagged
   low-importance details stay flexible. Touch `workflow.md §6` only
   if the deviation definition itself needs sharpening to match —
   check first, don't assume a change is needed.
2. Redesign phase-file rigor the same way: add In-scope/Out-of-scope
   and Automatic/Manual validations to `define-phase`'s Procedure;
   update `validate-work-full`'s phase-validation steps to check both
   explicitly and report them separately.
3. Document the spontaneous-phase-planning pattern in `workflow.md`
   and/or `README.md`, using P02 as the concrete example of how it
   already worked.
4. Add the closing-loop question to `propagate-context.task` (phase
   needs more tasks?) and `propagate-context.project` (project needs
   another phase?), positioned after marking complete, not before.

Steps 1 and 2 are the same treatment at different granularity —
keep as separate tasks for independent review, following P01/P02's
precedent of granular, single-purpose tasks. Steps 3 and 4 are
independent of 1/2 and of each other; 3 is documentation-only, 4 is a
small additive step in two skills (mirrors how P02-T04 added a
question before each planning skill's gate-stop — this is the
completion-side counterpart).

## Automatic validations

- `grep` confirms `define-task-full/SKILL.md` and
  `define-phase/SKILL.md`'s Procedure sections both instruct writing
  In-scope/Out-of-scope and Automatic/Manual validation
  subsections into their respective output files.
- `grep` confirms `propagate-context/SKILL.md` has a closing question
  in both `propagate-context.task` and `propagate-context.project`,
  positioned after the "mark complete" step, not before.
- If `workflow.md` is touched: `grep -n "^## "` before/after confirms
  every existing heading is still present and byte-identical (per
  `.ai/context/workflow-doc-conventions.md`'s stability rule) —
  cross-reference sweep re-run the same way T01 did.
- `git diff --stat` for the whole phase shows zero changes under
  `workflow-medium.md`, `skills/*-medium/`, `skills/workflow-lite/`,
  `skills/workflow-minimal/`, and their templates.

## Manual validations

- Read a task file drafted under the new `define-task-full` and judge
  whether its In-scope/Out-of-scope actually narrows what the
  implementer can do, rather than restating the Steps list in
  different words — a check no grep can perform.
- Read `implement-task-full`'s updated flexibility language and judge
  whether it's genuinely tighter (would a plausible small deviation
  now correctly get escalated instead of silently absorbed?), using a
  concrete hypothetical mismatch as the test case.
- Read the new spontaneous-planning documentation and judge whether
  it reads as an intentional, confident description of a supported
  mode — not a hedge or an afterthought.
- Confirm the two new closing questions read naturally as genuine
  questions expecting an answer, not rhetorical or buried at the end
  of a long paragraph where they'd be easy to skip past.

## Tasks

| ID | Title | Purpose | Depends on | Status |
|---|---|---|---|---|
| P03-T01 | Task-file rigor: In-scope/Out-of-scope + Automatic/Manual validations | Plan step 1: define-task-full's output structure + implement-task-full's flexibility language + workflow.md §6's deviation definition | — | complete |
| P03-T02 | Phase-file rigor: In-scope/Out-of-scope + Automatic/Manual validations | Plan step 2: define-phase's output structure + validate-work-full's phase-validation steps | — | complete |
| P03-T03 | Document the spontaneous-phase-planning pattern | Plan step 3: name the bare-roadmap-row → define-phase pattern in workflow.md/README.md, using P02 as the worked example | — | complete |
| P03-T04 | Closing-loop questions in propagate-context | Plan step 4: propagate-context.task asks if the phase needs more tasks; propagate-context.project asks if the project needs another phase | — | complete |
