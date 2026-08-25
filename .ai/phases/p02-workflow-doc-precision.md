# P02 — Workflow doc precision & extensibility

Roadmap entry: `.ai/constitution/roadmap.md`.

## Context

Scope for this whole phase is **Full profile only**, per explicit user
decision: `workflow.md`, `skills/*-full/` (create-constitution-full,
define-phase, define-task-full, implement-task-full, validate-work-full,
review-work-full, propagate-context), and the Full-profile templates
(`templates/info-template.md`, `context-template.md`,
`decisions-template.md`, `adr-template.md`). `workflow-medium.md`,
`workflow-lite/SKILL.md`, `workflow-minimal/SKILL.md`, and their
templates are **not** touched by this phase — medium hasn't been
field-tested yet (`mission.md` Goals), and lite/minimal are
deliberately one undivided "rules and procedure in the same file" by
design; splitting them would fight their own stated purpose.

`workflow.md` today is 13 sections (§1 Principles … §13 Commit
discipline), read in full by every skill on every invocation
(deliberate — see README's "compiled into this skill" lesson: a
partial summary once caused an agent to invent a status value outside
the closed enum). That guarantee must survive this phase — trimming
is about removing genuinely redundant/occasional-need content, not
about going back to partial summaries.

Five items, gathered directly from the user, all still inside
`mission.md`'s existing Goals:

**A — Core/reference split + gate-list reformat.** Split into a
trimmed core (kept in `workflow.md`) and `.ai/workflow/reference/`
(new folder, mirrors `templates/`/`skills/` as a sibling — mounted
automatically since it lives inside the `.ai/workflow/` submodule).
One reference file per concept (user's explicit choice over fewer/
larger files) — candidates, to be finalized at task-planning time
against the actual current section boundaries: gates/lifecycle detail,
artifact definitions (constitution/phase/task/context/decisions,
currently spread across §3/§4), deviations/ADR detail, agent
contracts detail, status/`info.md` detail (§11's "Set by" table and
extended naming notes). Core keeps: Principles, a compact gate list
(new format — see below), the lifecycle diagram, the skill-lookup
table, one-line definitions of each artifact type, `info.md`'s role,
execution modes, agent-contract summaries. Reference gets: rationale,
historical-incident explanations (e.g. §3's bare-path bug story, the
`sync-skills.sh` link-rule story), lookup tables not needed on every
read (§11's "Set by" table), and anything a specific operation needs
only occasionally rather than every time.

New gate-list format, replacing §5's current prose + "Diagram label /
Gate key / Distinct from" table + separate "Full gate list" sentence:

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
(Exact wording to be finalized at task-planning/implementation time —
this is the shape, not the final text.)

**B — Remove how-to, keep only what-is.** Not a separate pass from A —
while restructuring, delete (don't relocate) any step-by-step content
already duplicated in a skill's own Procedure section (e.g. §7's ADR
copy-steps, already fully stated in `implement-task-full` §2.6 and
`define-phase`/other skills' own ADR-writing instructions). Keep
standing rules even when phrased as steps (§2's "read info.md fresh,
open the matching skill file" is a rule every operation must follow,
not a task-specific how-to — stays in core).

**C — Append, not replan.** Today `define-phase`/`define-task-full`
only support "define new" or "replan after a deviation"
(`define-phase`'s own "When to use"). There's no path for "nothing
broke, we're adding more scope" that avoids re-triggering review of
already-approved, already-complete material. This phase itself is
living proof of the gap — P02 had to become a whole new phase instead
of an addition to P01 specifically to sidestep this. Needs: a short
new `workflow.md` subsection (near §5/§6, exact placement TBD at
implementation) defining what qualifies as append vs. replan, plus a
branch in `define-phase`'s procedure (adding a new phase's worth of
Plan items without resetting anything already `plan-approved`/
`in-progress`/`complete`) and in `define-task-full`'s procedure
(adding new tasks to an existing phase's Plan/Tasks table without
touching already-approved rows). The append path is still gated —
`phase-review`/`task-review` still apply to the new material — only
the "re-review everything" cost is what's being cut.

**D — `info.md` profile field; tables/status at the end.**
`medium-info-template.md` (`profile: medium`), `lite-project-template.md`
(`profile: lite`), `minimal-tasks-template.md` (`profile: minimal`)
already self-identify; `templates/info-template.md` (full) doesn't —
add `profile: full` there, same fixed-field convention. Separately:
`info-template.md` currently has its Status explanation *after* the
Status code block — reorder so explanation precedes the block (which
becomes the true tail of the file), matching the general principle
that nothing an agent needs to read should trail a block it might stop
reading at. `roadmap.md`, as generated by `create-constitution-full`
step 6, has the same pattern (trailing note after the table) — fix
that skill's instruction to front-load the note instead.

**F — Tell the user, at bare-title roadmap-append time, that fuller
context comes later (and can be lost if the session clears first).**
Noticed directly from this session: `create-constitution-full` just
appended P02 to `roadmap.md` as a title-only row, with all the actual
detail (the five items above) living only in this conversation until
`define-phase` captured it into the phase file. If a session ends
between those two moments, that detail is gone unless the user
happens to restate it. Doc-only fix (no new gate, no new mechanism):
`create-constitution-full` should tell the user, right when it adds a
bare phase-title row, that full planning (Context/Requirements/Plan/
Validations) happens next via `define-phase`, and invite them to share
any context/detail they already have now rather than waiting —
because a cleared session before that planning step means that context
may need to be restated. Document this both in `README.md` (so a human
skimming the bootstrap/lifecycle docs understands why the tool says
this) and in `create-constitution-full/SKILL.md`'s own procedure step.

**E — Ask if there's more, before requesting review.** New final
drafting sub-step in `create-constitution-full`, `define-phase`, and
`define-task-full` — placed immediately before each skill's existing
"commit and stop for the gate" step (drafting is ungated per
`workflow.md §5`, so this belongs inside the ungated drafting phase,
not after): ask the human whether more should be folded into this
draft before it goes to review. Purpose: batch review, not react to
whatever was asked and only that, redundant with how this session
already works ad hoc.

## Context (accumulated during the phase)

**From T01 (workflow.md restructure, complete):** every one of
`workflow.md`'s 13 section headings/numbers is now stable — T01
deliberately preserved every heading byte-for-byte so no cross-
reference anywhere in the repo needed editing. Later tasks that touch
`workflow.md` should preserve this property: prefer adding content as
a new subsection within an existing section (like §5's `### Execution
modes`) over inserting a brand-new numbered section, since a new
section shifts every following section's number and reintroduces the
exact cross-reference risk T01 just eliminated. If a genuinely new
top-level section is unavoidable (e.g. T02's append-vs-replan
mechanism, if it doesn't fit as a §6 subsection), redo the full
cross-reference sweep T01 did, don't assume it's still safe.

`reference/` file convention established by T01: each file opens with
a one-line "what this is for, referenced from workflow.md §N" pointer,
and is linked from the *specific* core sentence that needs it — not
just dropped in the folder. Follow this for any new reference file a
later task adds.

## Requirements

1. `workflow.md`'s core is materially shorter and contains no
   procedural how-to already covered by a skill's own Procedure —
   every fact an agent needs on *every* operation is still present in
   one read, without needing `reference/` for the common path.
2. `.ai/workflow/reference/` holds exactly the occasional-need
   material, one file per concept, each reachable from a specific
   named link in core — not a folder an agent has to browse to find
   the right file.
3. The gate list in core is the compact `- gate: after step. essential
   info` format; the current separate prose/table/diagram trio for
   gate identification is gone (the lifecycle diagram itself stays —
   it's the flow, the list is the detail).
4. Zero broken cross-references: every `.ai/workflow/workflow.md §N`/
   `#N-...` link across `skills/*-full/`, `README.md`, and the four
   Full-profile templates resolves correctly after the restructure —
   either still valid in trimmed core, or updated to point at the
   correct `reference/` file.
5. A genuinely new (non-deviation) phase or task can be added via a
   documented append path that does not require re-approving already-
   `plan-approved`/`in-progress`/`complete` material — but still
   requires its own `phase-review`/`task-review` for the new material.
   This requirement is satisfied by design + a worked example (P02
   itself, once this mechanism exists, is a candidate to retroactively
   demonstrate the difference — not required, just illustrative).
6. `.ai/info.md` (as generated from the updated `info-template.md`)
   states `profile: full`; its Status section's explanatory prose
   precedes the Status code block, not follows.
7. `.ai/constitution/roadmap.md` (as generated per
   `create-constitution-full`'s updated step 6) has its explanatory
   note before the table, not after.
8. `create-constitution-full`, `define-phase`, and `define-task-full`
   each have an explicit "anything else to add?" sub-step positioned
   before their commit-and-stop-for-gate step.
9. `workflow-medium.md`, `workflow-lite/SKILL.md`,
   `workflow-minimal/SKILL.md`, and their templates are untouched —
   `git diff --stat` for this phase shows zero changes under those
   paths.
10. When `create-constitution-full` adds a bare, title-only phase row
    to `roadmap.md`, it tells the user that full planning happens next
    via `define-phase` and invites them to share any context now,
    noting a cleared session before that planning step may lose
    context stated only in conversation. Documented in both
    `README.md` and `create-constitution-full/SKILL.md`.

## Plan

1. Restructure `workflow.md`: draft the trimmed core and the new
   `.ai/workflow/reference/*.md` files together (A + B are one
   undertaking, not sequential passes) — including the reformatted
   gate list. Then sweep every cross-reference in `skills/*-full/`,
   `README.md`, and the four Full-profile templates that points into
   `workflow.md`, and fix each to resolve correctly (core or the right
   reference file). This is the largest, highest-risk item — treat the
   cross-reference sweep as part of *this* step's own definition of
   done, not a follow-up.
2. Design and add the append-not-replan mechanism (C): the new
   `workflow.md` subsection defining append vs. replan, plus the
   `define-phase`/`define-task-full` procedure branches. Sequenced
   after step 1 so it's written directly into the already-restructured
   doc rather than needing to be re-diffed against two versions of
   `workflow.md`.
3. `info.md`/`roadmap.md` layout fix (D): add `profile: full` to
   `templates/info-template.md`, reorder its Status section;
   fix `create-constitution-full` step 6's roadmap.md-generation
   instruction to front-load its explanatory note.
4. Add the "anything else to add?" sub-step (E) to
   `create-constitution-full`, `define-phase`, `define-task-full`.
5. Document the bare-title roadmap-append notice (F) in `README.md`
   and `create-constitution-full/SKILL.md`'s procedure.

Steps 3, 4, and 5 are independent of 1/2 and of each other — safe to
do in any order or in parallel once 1/2 land, since none of them touch
`workflow.md`'s section structure in a way 1/2 would conflict with
(step 3 touches templates + one skill's step 6 prose; step 4 touches
three skills' procedures, additive sub-steps only; step 5 touches
`README.md` + one skill's procedure, additive). Steps 4 and 5 both
touch `create-constitution-full/SKILL.md` — fine to land in the same
task since they're both small, additive edits to the same file.

## Validations

- Cross-reference sweep: every `workflow.md §`/`workflow.md#` (or,
  post-restructure, `reference/*.md#`) occurrence across
  `skills/*-full/*.md`, `README.md`, and the four Full-profile
  templates resolves to a real section/file. Zero dangling references.
- `workflow.md` core, read start-to-finish, contains no step-by-step
  procedure that's a duplicate of content already in a skill's own
  Procedure section.
- Rough size check: core `workflow.md` is meaningfully shorter than
  its pre-phase ~436 lines (not a hard target, a sanity check that the
  split actually happened).
- `.ai/workflow/reference/` has one file per concept, and every file
  in it is linked from at least one place in core (no orphaned
  reference file nothing points to).
- Read the new append-mechanism subsection plus the
  `define-phase`/`define-task-full` branches and confirm
  `phase-review`/`task-review` are still required for the new
  material — the append path must not silently drop a gate.
- `templates/info-template.md` has `profile: full` and its Status
  block trails the prose explaining it; `create-constitution-full`'s
  step 6 instruction produces the same ordering for `roadmap.md`.
- `create-constitution-full`, `define-phase`, `define-task-full`: the
  "anything else to add?" sub-step exists in each, positioned before
  the commit-and-stop-for-gate step, not after.
- `git diff --stat` for the whole phase shows zero changes under
  `workflow-medium.md`, `skills/*-medium/`, `skills/workflow-lite/`,
  `skills/workflow-minimal/`, `templates/medium-*`,
  `templates/lite-*`, `templates/minimal-*`.
- `create-constitution-full/SKILL.md`'s roadmap-row-adding step
  explicitly instructs telling the user that full planning happens
  next via `define-phase` and inviting them to share context now, with
  the cleared-session caveat; `README.md` documents the same thing
  somewhere a human would actually see it (the bootstrap/lifecycle
  section, not buried).

## Tasks

| ID | Title | Purpose | Depends on | Status |
|---|---|---|---|---|
| P02-T01 | Restructure workflow.md into core + reference/, fix all cross-references | Plan step 1 (A+B): trim core to what-is only, new compact gate-list format, build .ai/workflow/reference/, sweep every cross-reference in skills/*-full, README.md, and the 4 Full templates | — | complete |
| P02-T02 | Add append-not-replan mechanism | Plan step 2 (C): workflow.md §6 addition + define-phase/define-task-full "When to use" clarification (scope narrowed at task-planning — mostly framing, not new mechanism) | P02-T01 (complete) | complete |
| P02-T03 | info.md/roadmap.md layout fix | Plan step 3 (D): profile: full field, tables/status moved after their explanatory prose, in info-template.md, create-constitution-full's roadmap.md step, and this project's own .ai/info.md + roadmap.md | — | awaiting-plan-review |
| P02-T04 | Add "anything else to add?" step to planning skills | Plan step 4 (E): create-constitution-full, define-phase, define-task-full each get this sub-step before their gate-stop | — | awaiting-plan-review |
| P02-T05 | Document bare-title roadmap-append notice | Plan step 5 (F): README.md + create-constitution-full's procedure | — | awaiting-plan-review |
