# P06-T03: Adjust ADR timing: write when decided, propagate to context/ only at phase completion

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 3: `workflow.md` §7 carries a `[HUMAN]` comment questioning whether ADRs
should be written only at the phase's context-propagation step, rather than the
moment a decision is made. The resolved decision is **no** — ADR-writing timing is
unchanged (write when the decision is made, reference it from the owning phase/task
file immediately); only *propagating* that decision's relevance into `context/`
moves to line up with §9's existing phase-completion timing. This is a
clarification, not a behavior change to when ADRs get written.

**Also folds in a second, related item from the phase's own In-scope list**
("ADR-writing steps for phase/project scope" relocation to skills) and the repo
survey finding that §7's ADR how-to is only half-migrated: `implement-task-full`
already has a concrete ADR-writing step (its Procedure step 6 — check
`decisions.md`, copy the template, add the index row), but `define-phase` and
`create-constitution-full` don't, even though §10 already states both **Must**
write an ADR for phase-/project-level decisions. Since this task is already editing
§7's ADR content and is the only remaining task that touches §7, it's the natural
place to close that gap too — no other Plan item covers it.

**Also addresses P06-T01's leftover note** (see that task's result note in the phase
file): §7's ownership line — "the constitution operation (project) · the
phase-planning operation (phase) · the implementation operation (during
implementation)" — predates T01's `**{Operation} operation** (\`{skill-name}\`)`
labeling convention; this task brings it in line.

**Design call made during planning** (flagging since it isn't spelled out in the
Plan item): §7 keeps the "no other operation writes one" ownership rule and the
superseding-ADR rule as-is (cross-cutting rules that apply regardless of which
operation wrote the ADR — duplicating them into three separate skills would be
worse, not better). Only the *mechanical* steps (check the index first, copy the
template, fill it in, add the index row) move out of §7 and into each ADR-owning
operation's own skill procedure, matching how `implement-task-full` already does it.

## Implementation

### Objective

Update `workflow.md` §7's ownership line to match P06-T01's labeling, remove the
write-vs-propagate timing ambiguity, and relocate §7's ADR-writing mechanics into
`define-phase`'s and `create-constitution-full`'s own procedures (matching
`implement-task-full`'s existing step); add one sentence to §9 stating ADR relevance
follows the same phase-completion propagation cadence as everything else there.

### In scope

- `workflow.md` §7: ownership line rewording; removing the three `[HUMAN]` comments;
  removing the mechanical "check decisions.md, copy template, fill fields, add index
  row" paragraph (moves to skills); keeping the "write when a decision is deliberate"
  rule and the superseding-ADR rule.
- `workflow.md` §9: one new sentence stating ADR-relevance propagation timing matches
  the rest of the section.
- `skills/define-phase/SKILL.md`: one new ADR-writing step, between the existing
  "ask if there's more to add" step and the commit step.
- `skills/create-constitution-full/SKILL.md`: the equivalent new ADR-writing step, in
  the same relative position.

### Out of scope

- `skills/implement-task-full/SKILL.md` — already has this step; not touched.
- `workflow.md` §10's Phase-planning/Constitution operation paragraphs — their
  existing "Must: ADR for phase-/project-level decisions" clauses already state the
  requirement this task fulfills the how-to for; no wording change needed there.
- Any change to when validation/review flags a *missing* ADR — unaffected by this
  task.
- `P06-T02`'s gate-merge content in §5/§8 — separate decision, already implemented.

### Files to modify

- `workflow.md` — §7, §9.
- `skills/define-phase/SKILL.md` — insert a new step before the commit step.
- `skills/create-constitution-full/SKILL.md` — insert a new step before the commit
  step.

### Steps

1. In §7, replace the ownership line and remove the `[HUMAN]` comment beneath it:

   ```
   **Ownership — whoever's scope produced the decision writes it:** the
   constitution operation (`create-constitution-full`, project-level) · the
   phase-planning operation (`define-phase`, phase-level) · the implementation
   operation (`implement-task-full`, during implementation). No other operation
   writes one — review flags a missing ADR back to the owning scope. Write it and
   reference it from the owning phase/task file the moment the decision is made —
   never deferred to phase completion; only propagating its relevance into
   `context/` follows §9's timing.
   ```

   (flexible: exact prose — binding: skill names in backticks per operation, the
   "never deferred to phase completion" statement, and the pointer to §9 for
   propagation timing must all be present.)
2. In §7, remove the mechanical paragraph ("Check `../decisions/decisions.md`
   first. Copy [`templates/adr-template.md`]...") and its trailing `[HUMAN]`
   comment — this content moves into steps 4–5 below (and already exists in
   `implement-task-full`).
3. In §7, keep the superseding-ADR sentence ("A superseding ADR updates both rows'
   Relations...") but remove its trailing `[HUMAN]` comment — this stays as a
   cross-cutting rule, per the Context section's design note above.
4. In `skills/define-phase/SKILL.md`, insert a new step between the existing step 7
   ("Ask the user whether there's anything else to add...") and step 8 ("Commit the
   draft..."), renumbering step 8 onward by one:

   ```
   8. If a phase-level decision was made while drafting this phase that future
      work needs to know about, this is yours to document — check
      `.ai/decisions/decisions.md` first; a related decision may already exist. If
      not, write the ADR from
      [.ai/workflow/templates/adr-template.md](.ai/workflow/templates/adr-template.md)
      into `.ai/decisions/adr{NN}-{name}.md`, add its index row in the same step,
      and reference it from this phase file's own Context section.
   ```

   Update the Output section to note an ADR + index row as a possible output.
5. In `skills/create-constitution-full/SKILL.md`, insert the equivalent new step
   between the existing step 7 and step 8, renumbering step 8 onward by one:

   ```
   8. If a project-level decision was made while drafting mission/techstack/
      roadmap that future work needs to know about, this is yours to document —
      check `.ai/decisions/decisions.md` first; a related decision may already
      exist. If not, write the ADR from
      [.ai/workflow/templates/adr-template.md](.ai/workflow/templates/adr-template.md)
      into `.ai/decisions/adr{NN}-{name}.md` and add its index row in the same
      step.
   ```

   Update the Output section to note an ADR + index row as a possible output.
6. In §9, immediately after the "No lateral shared-context files exist (§4)..."
   paragraph, add: "An ADR's relevance to `context/` propagates on this same
   phase-completion cadence — writing the ADR itself never waits for it." (flexible:
   exact wording — binding: the literal substring "propagates on this same
   phase-completion cadence" must appear on one line, and the sentence must state
   ADR-writing itself doesn't wait for propagation.)

### Dependencies

`P06-T01` (already complete — this task reuses its `**{Operation} operation**
(\`{skill-name}\`)` labeling convention).

### Expected result

§7 states ADR-writing timing and ownership without ambiguity or leftover `[HUMAN]`
comments, and without the mechanical steps now duplicated in each ADR-owning skill.
§9 explicitly ties ADR-relevance propagation to its existing phase-completion
timing. `define-phase` and `create-constitution-full` each have their own concrete
ADR-writing step, matching `implement-task-full`'s.

### Automatic validations

- `grep -c "\[HUMAN\]" workflow.md` drops by exactly 3 (§7's three comments).
- `grep -n "adr-template.md" skills/define-phase/SKILL.md` returns one match.
- `grep -n "adr-template.md" skills/create-constitution-full/SKILL.md` returns one
  match.
- `grep -n "never deferred to phase completion" workflow.md` returns one match, in
  §7.
- `grep -n "propagates on this same phase-completion cadence" workflow.md` returns
  one match, in §9.
- `diff <(git show HEAD:skills/implement-task-full/SKILL.md) skills/implement-task-full/SKILL.md`
  — no output (confirms it's untouched; it already has this step).

### Manual validations

- Confirm §7 reads as a complete, ambiguity-free rule on its own — a reader who
  never sees the removed mechanical paragraph can still find "how" via the linked
  skill for their operation.
- Confirm the new steps in `define-phase`/`create-constitution-full` read as
  self-contained (name the actual template/target paths), matching the level of
  detail `implement-task-full`'s existing step already has.
- Confirm §9's new sentence doesn't read as introducing a new context-writing
  destination — it should be clear an ADR still lives only in `.ai/decisions/`; only
  its *relevance* (a fact worth knowing) may end up reflected in `context/`, same as
  any other phase-level fact.
