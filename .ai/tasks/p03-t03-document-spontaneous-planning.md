# P03-T03 — Document the spontaneous-phase-planning pattern

Phase: [`../phases/p03-spec-rigor-and-loop.md`](../phases/p03-spec-rigor-and-loop.md).

## Context

See phase file Context/Plan step 3, and `workflow.md`'s own history:
P02 through P05 all started as a bare title-only `roadmap.md` row,
planned one at a time from live conversation, not from a pre-existing
detailed Plan. `README.md` already documents part of this mechanism
(added in P02-T05): a phase enters `roadmap.md` title-only, full detail
comes later via `define-phase`, and the human should share context now
in case the session clears before that happens. What's still missing:
nothing names this as an intentional, normal way to *plan a whole
project* — one phase at a time, no roadmap needed up front — as
opposed to just describing the mechanical two-step sequence.

Per the phase-stability convention
(`.ai/context/workflow-doc-conventions.md`): add this as a subsection
within an existing `workflow.md` section, not a new top-level one.
`§5. Lifecycle & gates` is the natural home — it's about how planning
actually starts and flows.

## In scope

- A new subsection in `workflow.md §5` naming this pattern explicitly,
  using this repo's own roadmap history (P02–P05) as the concrete
  evidence it already works.
- Checking `README.md`'s existing P02-T05 paragraph against the new
  subsection — cross-reference them rather than duplicate; light edit
  only if needed to connect the two.

## Out of scope

- Any change to `create-constitution-full` or `define-phase`'s actual
  mechanics — both already support this; this task only names and
  documents the pattern.
- A task-level equivalent mechanism — already out of scope for the
  whole phase (existing append path, P02-T02, already covers small
  increments; only documentation was ever missing, and that's not
  this task's subject either).

## Implementation

**Objective:** Name "plan one phase at a time, starting from a bare
roadmap row, no pre-existing detailed Plan required" as an explicit,
intentional, supported way of working — not an implicit side effect of
how two skills happen to compose.

**Files to modify:**

- `workflow.md` — new subsection in §5.
- `README.md` — only if the new subsection and the existing P02-T05
  paragraph need a connecting link; check first, don't edit
  speculatively.

**Files to create:** none.

**Steps:**

1. In `workflow.md §5`, after the `### Execution modes` subsection,
   add a new subsection (working title `### Starting without a plan`)
   stating: it's normal and expected to plan one phase at a time
   rather than the whole project up front — `create-constitution-full`
   appends a single title-only row for whatever's next, then
   `define-phase` drafts that phase's full content from the live
   conversation, not from anything already written down. Name this
   repo's own `roadmap.md` (P02 through P05) as the concrete example.
2. Read the existing README paragraph (added P02-T05, currently right
   after the "normal loop" description, before "## Updating the
   workflow") and decide whether it needs a pointer to the new
   `workflow.md` subsection, or whether the two already read
   consistently without one. Only edit `README.md` if a genuine gap or
   duplication exists.
3. Confirm `workflow.md`'s `## `-level heading list is unchanged (a
   `###` subsection doesn't affect `##` anchors, but verify — per
   `.ai/context/workflow-doc-conventions.md`).

**Dependencies:** none — independent of T01/T02 and of T04.

**Expected result:** an agent or human reading `workflow.md §5` (or
`README.md`) understands that starting a project with just a mission
and no roadmap detail, then planning phases one at a time as they're
identified, is a first-class supported mode.

**Automatic validations:**

1. `grep -n "### " workflow.md` — confirm the new subsection exists
   under §5 and no `## ` heading changed (rerun the same `grep -n "^## "`
   comparison T01/T02 used).
2. `git diff --stat` for this task's commit touches only `workflow.md`
   (and `README.md` only if step 2 above determined an edit was
   actually needed).

**Manual validations:**

1. Read the new `workflow.md` subsection and judge whether it reads as
   confident, intentional guidance — not a hedge, not an afterthought,
   and not simply restating the existing README paragraph's session-
   context-loss framing (this is a different point: it's about
   planning philosophy, not about not losing context).
2. If `README.md` was touched: confirm the two documents complement
   rather than duplicate each other.
