# P06: Workflow Doc Pruning

## Context

`workflow.md` accumulated 28 inline `[HUMAN]` review comments proposing to trim it
back to descriptive/rule-only content, per its own stated design (rules live in
`workflow.md`, rationale in `reference/`, how-to in `skills/` — see
[.ai/context/workflow-doc-conventions.md](../context/workflow-doc-conventions.md)).
A companion review pass over `feedback.md`'s "Workflow, Gates and Status
simplification" sketch and the current `workflow.md` produced 9 concrete decisions,
each already resolved with the human in conversation (see Plan below — this phase
operationalizes those decisions, nothing here is still open).

Repo survey findings that shape the Plan:
- `create-constitution-full`, `define-phase`, `define-task-full`,
  `implement-task-full`, `validate-work-full`, `review-work-full` already contain
  real procedural how-to; they mostly don't duplicate `workflow.md`.
- `propagate-context`'s skill already fully operationalizes §9's principle — that
  section is the cleanest case of "the skill already has it."
- ADR how-to (§7) is only half-migrated: `implement-task-full` has a partial version
  for implementation-time ADRs; `define-phase`/`create-constitution-full` don't yet
  have their own steps for phase-/project-level ADRs.
- No skill currently embeds commit-message logic (§13) — they all just link back to it.
- No separate deviation files exist anywhere in this repo's own history; the
  lighter-profile templates (`lite-project-template.md`, `minimal-tasks-template.md`)
  already use an inline `**Deviation (if any):**` field instead of a separate file —
  a usable precedent for Full.
- `workflow-lite/SKILL.md` and `workflow-minimal/SKILL.md` are already fully
  role-agnostic (no named-agent framing anywhere) — the template for collapsing §10.
- All 8 full-profile skills (and the 5 medium-profile skills that mirror the same
  framing) currently open with "Operation for the **Named Agent**," linking to §10
  for that role's contract — 13 hits total across full-profile skills.

**P06-T01 result (for T02/T03/T10, which edit text this task touched):**
§10 is now headed `## 10. Operation contracts` (anchor
`#10-operation-contracts`, not the old `#10-agent-contracts`). Each
contract is labeled `**{Operation} operation** (\`{skill-name}\`)` —
Constitution (`create-constitution-full`), Phase-planning
(`define-phase`), Task-planning (`define-task-full`), Implementation
(`implement-task-full`), Validation (`validate-work-full`), Review
(`review-work-full`), Context (`propagate-context`,
`build-context-full`) — same pattern in `workflow-medium.md` minus
Phase-planning/Context. Every skill header now reads "This skill
performs the **{operation}** operation. Its Can/Must/Cannot contract:
[...§10](...#10-operation-contracts)." T02 should merge the Validation
and Review paragraphs under this labeling; T03 should edit the ADR
ownership line's "the constitution operation (project) · the
phase-planning operation (phase) · the implementation operation
(during implementation)" phrasing (§7); T10 should edit the
already-renamed `define-phase`/`create-constitution-full` mentions
"replanned via `define-phase`" / "replanned via
`create-constitution-full`" in §6's escalation bullets.

## In scope

- Rewriting `workflow.md` per the 9 resolved decisions (Plan, items 1–9).
- Rewriting §10 and all 8 full-profile skills' role framing to be role-agnostic,
  modeled on `workflow-lite`/`workflow-minimal`; carrying the equivalent change into
  the 5 medium-profile skills that mirror the same framing, so full/medium don't
  diverge in how they express agent contracts.
- The Validation/Review gate consolidation (one named gate, two internal checks) in
  §5/§8, including the execution-mode default tables.
- The ADR-propagation-timing clarification in §7/§9 (or their rewritten equivalents).
- Relocating the two identified bug-traced/how-to items (the re-read-every-time
  lesson; ADR-writing steps for phase/project scope) to `reference/`/skills
  respectively, and the inline-deviation-file convention into `define-task-full`.
- Adding the two genuinely new, small rules identified during review: an explicit
  context-resolution search order, and an explicit active-pointer-lifecycle
  statement in §11.
- Re-running `sync-skills.sh` and refreshing this repo's own `.ai/workflow/`
  self-mounted copy once the root files are final, so the mirrors aren't left stale.

## Out of scope

- `feedback.md`'s "Workflow profiles separation" idea (per-profile repos with a
  parent, a README bootstrap downloader, profile-aware `sync-skills.sh`) — a
  separate, larger infrastructure idea; not part of this doc-pruning pass.
- Any independent redesign of `workflow-medium.md`'s own content — medium-profile
  files only get the role-agnostic and gate-merge changes needed for consistency
  with the full profile, nothing else.
- Writing ADRs retroactively about past decisions — this phase only changes how
  ADR timing/propagation works going forward, per P05's own separate scope for
  "notice human edits," this phase doesn't touch that topic either.

## Requirements

- `workflow.md`'s always-read content is descriptive/rule-only; every relocated
  how-to or rationale item has a real, findable home in `skills/` or `reference/` —
  nothing is silently dropped.
- All 8 full-profile skills (and the 5 medium-profile skills that mirror them)
  state their own Can/Must/Cannot contract without depending on §10's named-role
  framework existing.
- The Validation/Review gate consolidation preserves `assisted` mode's current
  behavior: the mechanical check still auto-passes, the judgment check still holds
  for a human.
- ADR-writing timing is unchanged (write when a decision is made); only
  propagation of that ADR into `context/` moves to phase-completion time.
- `.ai/workflow/` (this repo's self-mounted copy) and `.agents/skills/` are
  byte-identical to the canonical root copies after the final sync.

## Plan

1. **§10 + skills role-agnostic rewrite** (decision 1) — Rewrite `workflow.md` §10
   to state Can/Must/Cannot per *operation* (constitution, phase-planning,
   task-planning, implementation, validation+review, context) without naming an
   agent role. Update all 8 full-profile skills' opening "Operation for the
   **Named Agent**" line and any role-name references to match. Carry the
   equivalent change into the 5 medium-profile skills that mirror the same framing.
2. **§8/§5 Validation+Review gate merge** (decision 2) — Consolidate the two-gate
   task lifecycle (`task-validation` + `task-completion-review`) and phase
   lifecycle (`phase-validation` + `phase-completion-review`) into one named gate
   each, internally still sequencing a mechanical check then a judgment check.
   Update the lifecycle diagram, the gate bullet list, and the execution-mode
   default tables so `assisted` mode's auto-pass/hold-for-human split survives
   under the new single-gate name.
3. **ADR-propagation timing** (decision 3) — Update §7 and §9 (or their
   role-agnostic replacements) to state ADRs are written the moment a decision is
   made and referenced from the phase/task immediately, but propagated to
   `context/` only at phase completion, alongside the rest of §9's step.
4. **Line-45 lesson relocation** (decision 4) — Remove the "gate-skip/scope-overstep
   bugs traced back to this step" sentence from §2; add it to a `reference/` file
   (new or existing), linked from §2.
5. **Line-267 scope-clarification trim** (decision 5) — Keep a one-line "new
   approved scope isn't a deviation" rule in §6; move the "how an append is
   drafted" detail into `define-phase`/`define-task-full` if not already covered.
6. **Line-432 pointer-lifecycle statement** (decision 6) — Add one explicit line to
   §11: the active pointer is set at start of planning, cleared at completion. No
   behavior change.
7. **Line-438 ID-order rule** (decision 7) — Keep the one-line "resolve against
   Depends-on + Status, never lowest ID" rule in §11; confirm
   `reference/status-and-info.md` still holds only the worked examples/reasoning.
8. **§12 fold-in** (decision 8) — Move "`info.md` tracks only one active
   phase/task by design" into §11; delete the rest of §12.
9. **§13 commit-step migration** (decision 9) — Add a concrete commit step (what to
   stage, what the message should say — no Conventional-Commits mandate) to each
   of the 8 full-profile skills' own procedure, at their existing "commit the
   draft" step. Trim §13 to one cross-cutting line: commit each draft immediately,
   before requesting review.
10. **Inline-deviation convention** — Define an inline `**Deviations**` subsection
    convention for full-profile task files in `define-task-full`, replacing the
    separate `tasks/p{NN}-t{NN}-{name}-deviation.md` file mechanism described in
    §6; update §6's text accordingly.
11. **Context-resolution search order** — Add a short rule (§2 or §4) that an agent
    resolves context by following the task/phase file's own links first, not by
    searching the codebase for context docs — new content, from `feedback.md`'s
    "Execution" idea, not a trim.
12. **Other confirmed-safe trims** — Opening/§1 (drop redundant intro prose, the
    "use terminal tools to discover structure" principle); §3 (drop the "this is a
    fix" clause, safe since `reference/directory-and-links.md` already tells the
    story); §4 (add a short `phase: …; task: …` glossary line); §9 (drop the
    now-redundant how-to prose, safe since `propagate-context` already
    operationalizes it).
13. **Sync mirrors** — Run `sync-skills.sh` and refresh `.ai/workflow/`'s copy of
    `workflow.md`, `skills/`, `templates/`, `reference/` once the root files are
    final.

## Automatic validations

- `grep -rln "Operation for the \*\*" skills/*/SKILL.md` returns no matches after
  step 1, across all 8 full-profile skill files.
- `grep -n "Conventional Commits" workflow.md` returns nothing after step 9.
- `grep -rn "\-deviation.md" workflow.md` returns nothing after step 10 (confirms
  §6 describes the inline convention instead of the separate-file one).
- `diff -rq skills/ .agents/skills/` and `diff -rq skills/ .ai/workflow/skills/`
  report no differences after step 13's sync.

## Manual validations

- Read the rewritten `workflow.md` end-to-end and confirm it reads as
  descriptive/rule-only, with no orphaned "why" prose that should have moved to
  `reference/`.
- Spot-check 2–3 rewritten skills (e.g. `define-phase`, `implement-task-full`) to
  confirm their Can/Must/Cannot contract still fully constrains behavior without
  §10's named-role framing.
- Confirm the Validation/Review gate merge still reads clearly for `assisted`
  mode — a reader can tell the mechanical part auto-passes while the judgment part
  still waits for a human.
- Cross-check the final `workflow.md` against the 9 resolved decisions (recorded
  in the planning conversation that produced this phase) to confirm nothing was
  silently dropped or reinterpreted differently from what was agreed.

## Tasks

| ID | Title | Purpose | Depends on | Status |
|---|---|---|---|---|
| P06-T01 | Collapse agent-role framing to role-agnostic operation contracts | Remove named-agent-persona framing from workflow.md/workflow-medium.md §10 (+ their other role mentions) and all 13 full/medium skill headers, keeping every Can/Must/Cannot bullet's content unchanged | — | complete |
| P06-T02 | Merge Validation and Review into one gate per task/phase, still running two internal checks | Consolidate task/phase lifecycle gates while preserving assisted mode's auto-pass-mechanical / hold-for-human split | P06-T01 | not-planned |
| P06-T03 | Adjust ADR timing: write when decided, propagate to context/ only at phase completion | Separate "write the ADR" from "propagate it," matching §9's existing phase-completion timing | P06-T01 | not-planned |
| P06-T04 | Relocate the gate-skip/scope-overstep bug-traced lesson to reference/ | Preserve the lesson without keeping it in workflow.md's always-read path | — | complete |
| P06-T05 | Trim the new-scope-isn't-a-deviation clarification to one line | Keep the rule in workflow.md §6; move "how an append is drafted" detail to define-phase/define-task-full | — | plan-approved |
| P06-T06 | Add explicit active-pointer-lifecycle statement to §11 | Documentation clarity only — no behavior change | — | plan-approved |
| P06-T07 | Keep the one-line ID-order-≠-execution-order rule in §11 | Keep the operating rule in workflow.md; reasoning/examples stay only in reference/status-and-info.md | — | plan-approved |
| P06-T08 | Fold §12's single-active-item constraint into §11; delete the rest of §12 (renumber §13→§12) | Preserve the one real constraint, drop the multi-agent advisory content | — | plan-approved |
| P06-T09 | Migrate commit-step detail into each of the 8 full-profile skills; trim the commit-discipline section to one line | Drop the Conventional-Commits mandate from workflow.md; keep "commit each draft immediately" as the one cross-cutting rule | — | plan-approved |
| P06-T10 | Define an inline in-task-file deviation convention; update §6 | Replace the separate deviation-file mechanism, precedented by lite/minimal's inline field | P06-T01 | not-planned |
| P06-T11 | Add an explicit context-resolution search-order rule | New rule: follow the task/phase file's own links first, don't search the codebase for context docs | — | plan-approved |
| P06-T12 | Apply remaining confirmed-safe trims (opening/§1, §3, §4 glossary, §9) | Low-risk cleanup already confirmed safe against reference/ and propagate-context's existing content | — | plan-approved |
| P06-T13 | Sync mirrors: run sync-skills.sh and refresh .ai/workflow/'s copy | Keep .agents/skills/ and .ai/workflow/ byte-identical to the canonical root copies | P06-T01…T12 | not-planned |
