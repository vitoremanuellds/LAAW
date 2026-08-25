# P04-T01 — Design and write the build-context-full skill

Phase: [`../phases/p04-brownfield-context-building.md`](../phases/p04-brownfield-context-building.md).

## Context

See phase file Context/Plan (steps 1–4, kept as one task — they define
one skill's shape together, not independent slices). Mirrors
`propagate-context`'s multi-sub-operation shape: `.assess` (listing-
only assumption pass), `.plan` (iteration plan from assumptions, after
human review), `.iterate` (read a batch, build real context/, repeat).
Attributed to the existing **Context Agent** role (`workflow.md §10`)
as a second operation alongside `propagate-context`, not a new agent
role — both operate on `.ai/context/`, just from different triggers
(post-completion propagation vs. fresh codebase survey).

## In scope

- `skills/build-context-full/SKILL.md` — the full skill, three
  sub-operations.
- `templates/context-temp-template.md` — the assumptions-document
  template with the `[ASSUMPTION]`/`[QUESTION]`/`[HUMAN]` marker
  convention.
- `templates/context-build-plan-template.md` — the iteration-plan
  template with its queued/read status table.
- One new row in `workflow.md §2`'s skill-lookup table.
- A short addition to `workflow.md §10`'s Context Agent contract
  naming this as its second operation.

## Out of scope

- Actually running the skill against any project (this repo's own
  `.ai/context/` included) — this task builds the skill, doesn't
  invoke it.
- Medium/lite/minimal profiles.
- Anything not already named in the phase file's In scope.

## Implementation

**Objective:** Write a complete, usable `build-context-full` skill and
its two supporting templates, wired into `workflow.md`'s lookup table
and the Context Agent's contract.

**Files to modify:**

- `workflow.md` — §2 (one new table row), §10 (one added sentence to
  the Context Agent's Can/Must line — no heading changes either
  section).

**Files to create:**

- `skills/build-context-full/SKILL.md`
- `templates/context-temp-template.md`
- `templates/context-build-plan-template.md`

**Steps:**

1. Write `skills/build-context-full/SKILL.md` with frontmatter
   `name: build-context-full` and a `description` stating: populates
   `.ai/context/` via a listing-only assumption pass, human-annotated
   review, then a batch-sized, status-tracked iteration; not for
   post-completion propagation (see `propagate-context`); requires
   `.ai/info.md`/`.ai/context/context.md` to already exist. Body:
   operation-for-Context-Agent line linking `workflow.md §10`;
   `workflow.md` full-read instruction, same as every skill; a "When
   to use" section (thin `context/` relative to codebase size, not a
   forced bootstrap step); then the three sub-operations:
   - **`build-context.assess`** — inputs are directory/file listings
     only (`tree`/`find`/`ls`), **never** file contents in this
     sub-operation. Steps: (1) recursive listing, excluding `.git/`,
     `.ai/workflow/`, and name-inferred build/dependency directories;
     (2) from names/extensions/structure alone, write
     `.ai/context/context.temp.md` (from
     `templates/context-temp-template.md`) with purpose/mission,
     architecture/module breakdown, and open questions, each claim
     its own `[ASSUMPTION]` line and each genuine unclear point its
     own `[QUESTION]` line — never folded together; (3) commit, then
     stop and tell the human it's ready for annotation — they may add
     `[HUMAN]` lines but must never delete an `[ASSUMPTION]`/
     `[QUESTION]` line, even a wrong one. Not a plan-review gate (no
     Status change) — a stop-and-wait for input before `.plan`.
   - **`build-context.plan`** — precondition: `context.temp.md`
     exists. Steps: (1) read it in full, including `[HUMAN]`
     annotations; (2) ask the human for batch size if not already
     given; (3) order the real file-read list — entry points/config/
     manifest files first (they correct the most assumptions per
     file), then the rest grouped by the inferred module breakdown;
     (4) write `.ai/context/build-plan.md` (from
     `templates/context-build-plan-template.md`): the ordered list,
     each row `queued`, the batch size, a link back to
     `context.temp.md`; (5) commit, report the plan and first batch.
   - **`build-context.iterate`** — precondition: `build-plan.md` has
     at least one `queued` row. Steps: (1) take the next batch-size
     count of `queued` files, in order; (2) read each in full; (3) for
     each, reconcile against `context.temp.md`'s assumptions (confirm/
     correct/flag) and write or update the relevant `.ai/context/*.md`
     file(s) — group by module/domain, not one file per source file,
     same convention as `.ai/context/workflow-doc-conventions.md`;
     update `context.md`'s table for every file touched; (4) set each
     processed file's row to `read` in `build-plan.md`; (5) commit;
     (6) if rows remain `queued`, stop and report progress (X read, Y
     queued) — don't auto-continue to the next batch in the same
     turn, batch size is the human's pacing control; if the queue is
     now empty, report completion and ask whether `context.temp.md`
     should be archived or deleted — never delete it unilaterally.
   Output section: lists all artifacts each sub-operation
   produces/updates.
2. Write `templates/context-temp-template.md`: heading, a note that
   this is temporary/unverified, the `[ASSUMPTION]`/`[QUESTION]`
   convention explained in the file itself (so a human opening it cold
   understands the never-delete rule without having read the skill),
   and section skeleton (Purpose/mission, Architecture/module
   breakdown, Open questions) with one commented-out example line each.
3. Write `templates/context-build-plan-template.md`: heading, a note
   on what writes/reads it, a `Batch size: {N}` line, and a
   `| File | Status |` table skeleton with one commented-out example
   row.
4. In `workflow.md §2`'s lookup table, add one row: "Populate
   `.ai/context/` for a project with little context yet |
   `skills/build-context-full/`".
5. In `workflow.md §10`'s **Context Agent** entry, add one sentence
   naming `build-context-full` as a second operation (surveying an
   unread codebase) alongside `propagate-context` (propagating what a
   completed task/phase learned) — no change to the Agent's existing
   Can/Must/Cannot lines otherwise.
6. Confirm `workflow.md`'s `## `-level heading list is unchanged (both
   edits are within existing sections' bodies).

**Dependencies:** none — only task in P04 so far.

**Expected result:** a complete, usable `build-context-full` skill and
its two templates exist; `workflow.md` references it from both the
lookup table and the Context Agent's contract, with no heading churn.

**Automatic validations:**

1. `grep -n "build-context.assess\|build-context.plan\|build-context.iterate" skills/build-context-full/SKILL.md` — all three present.
2. `grep -n "\[ASSUMPTION\]\|\[QUESTION\]\|\[HUMAN\]" templates/context-temp-template.md skills/build-context-full/SKILL.md` — marker convention present in both.
3. `grep -n "build-context-full" workflow.md` — appears in both §2 and §10.
4. `grep -n "^## " workflow.md` before/after — unchanged.
5. `git diff --stat` for this task's commit touches exactly
   `skills/build-context-full/SKILL.md`,
   `templates/context-temp-template.md`,
   `templates/context-build-plan-template.md`, `workflow.md` —
   nothing else.

**Manual validations:**

1. Read the `.assess` sub-operation and judge whether it would
   actually stay listing-only in practice (no tempting shortcut into
   reading a file "just to check").
2. Read the `.iterate` sub-operation's reconciliation step and judge
   whether "confirm/correct/flag" against `context.temp.md` is
   concrete enough to follow mechanically, not just a vague nod at
   reconciliation.
3. Read `templates/context-temp-template.md` cold (as if seeing it for
   the first time, no skill file read) and judge whether the never-
   delete convention is unambiguous from the file alone.
