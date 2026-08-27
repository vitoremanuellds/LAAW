# P06-T01: Collapse agent-role framing to role-agnostic operation contracts

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md)
for the phase's full Context and the decisions this phase operationalizes. This
task is Plan item 1 (decision 1): the workflow is meant to be run by one generic
agent aware of the current phase/step and what it can/cannot do there — not by
named personas (Constitution Agent, Phase Planning Agent, etc.) restated per
skill. `skills/workflow-lite/SKILL.md` and `skills/workflow-minimal/SKILL.md`
are the existing precedent: they state Can/Must/Cannot per step without ever
naming a role, and this task brings the full and medium profiles' `§10` sections
and skill headers to the same style, without changing what any Can/Must/Cannot
list actually says.

Only the *proper-noun* role names ("Constitution Agent", "Phase Planning Agent",
etc.) are in scope — the generic word "agent" (e.g. §1's "Agents do not
reconstruct information...", §10's own "No agent determines its own authority")
already describes a single undifferentiated agent and stays as-is.

## Implementation

### Objective

Replace every named-agent-persona reference in `workflow.md`, `workflow-medium.md`,
and their skills' header lines with an operation-keyed label tied to the skill
that performs it, preserving every Can/Must/Cannot bullet's content unchanged.

### In scope

- `workflow.md` §10's heading and its 7 contract paragraphs (Constitution, Phase
  Planning, Task Planning, Implementation, Validation, Review, Context).
- `workflow.md`'s other role-name mentions: §4 (line ~130), §6 (lines ~254, 256),
  §7 (lines ~277–279).
- `workflow-medium.md`'s equivalent §10 (5 contract paragraphs: Constitution,
  Task Planning, Implementation, Validation, Review — medium has no separate
  Phase Planning or Context contract) and its own role-name mentions in §6
  (line ~178) and §7 (lines ~192–196).
- The header line ("Operation for the **X Agent**. Contract: ...") in all 8
  full-profile skills and all 5 medium-profile skills, and every
  `#10-agent-contracts` anchor link anywhere that needs to become
  `#10-operation-contracts` after the heading rename.

### Out of scope

- The Validation/Review gate *merge* itself (P06-T02) — this task only renames
  the two contracts from "Validation Agent"/"Review Agent" to "Validation
  operation"/"Review operation"; it does not combine them into one gate. Leave
  them as two separate contract paragraphs.
- Any content change to what a Can/Must/Cannot bullet actually permits or
  forbids — this task is a rename/reframe only.
- `workflow-lite`/`workflow-minimal` — already role-agnostic, nothing to change.

### Files to modify

- `workflow.md` — rename `## 10. Agent contracts` to `## 10. Operation
  contracts`; rewrite its 7 contract paragraphs' labels; update the role-name
  prose at §4/§6/§7 noted above; update this file's own internal
  `#10-agent-contracts` anchor links to `#10-operation-contracts`.
- `workflow-medium.md` — same treatment: heading rename, its 5 contract
  paragraphs' labels, §6/§7 role-name prose, internal anchor links.
- `skills/create-constitution-full/SKILL.md` — header line: Constitution → 
  constitution operation.
- `skills/define-phase/SKILL.md` — header line: Phase Planning → phase-planning
  operation.
- `skills/define-task-full/SKILL.md` — header line: Task Planning →
  task-planning operation.
- `skills/implement-task-full/SKILL.md` — header line: Implementation →
  implementation operation.
- `skills/validate-work-full/SKILL.md` — header line: Validation → validation
  operation.
- `skills/review-work-full/SKILL.md` — header line: Review → review operation.
- `skills/propagate-context/SKILL.md` — header line: Context → context
  operation.
- `skills/build-context-full/SKILL.md` — header line: Context → context
  operation (same label as `propagate-context` — both perform the Context
  contract, as today).
- `skills/create-constitution-medium/SKILL.md` — header line, pointing at
  `workflow-medium.md`'s renamed anchor.
- `skills/define-task-medium/SKILL.md` — header line, same.
- `skills/implement-task-medium/SKILL.md` — header line, same.
- `skills/validate-work-medium/SKILL.md` — header line, same.
- `skills/review-work-medium/SKILL.md` — header line, same.

### Files to create

None.

### Steps

1. In `workflow.md`, rename the `## 10. Agent contracts` heading to `## 10.
   Operation contracts`. Do not change its intro line's use of the generic word
   "agent" ("No agent determines its own authority...") — that's already
   role-agnostic phrasing, keep it.
2. Rewrite each of §10's 7 contract paragraph labels from `**{Name} Agent**` to
   `**{Operation} operation** ({skill-name})`, keeping every Can/Must/Cannot
   bullet's wording unchanged (flexible: exact label wording, e.g. "Constitution
   operation" vs "Constitution-drafting operation" — binding: the skill-name
   parenthetical must name the real skill, and no bullet content may change):
   - Constitution Agent → **Constitution operation** (`create-constitution-full`)
   - Phase Planning Agent → **Phase-planning operation** (`define-phase`)
   - Task Planning Agent → **Task-planning operation** (`define-task-full`)
   - Implementation Agent → **Implementation operation** (`implement-task-full`)
   - Validation Agent → **Validation operation** (`validate-work-full`)
   - Review Agent → **Review operation** (`review-work-full`)
   - Context Agent → **Context operation** (`propagate-context`,
     `build-context-full`)
3. In `workflow.md` §4 (the "what a phase is" paragraph, ~line 130), change "the
   Phase Planning Agent's contract in §10" to "the phase-planning contract in
   §10."
4. In `workflow.md` §6 (deviation escalation bullets, ~lines 254/256), change:
   - "Phase-level → Phase Planning Agent replans ..." to "Phase-level →
     replanned via `define-phase` ..."
   - "Project-level → Constitution Agent replans, always writes an ADR." to
     "Project-level → replanned via `create-constitution-full`, always writes
     an ADR."
5. In `workflow.md` §7 (ADR ownership line, ~lines 277–279), change "Constitution
   Agent (project) · Phase Planning Agent (phase) · Implementation Agent (during
   implementation). No one else writes one — Review Agent flags a missing ADR
   back to the owning scope." to name the operations instead: "the constitution
   operation (project) · the phase-planning operation (phase) · the
   implementation operation (during implementation). No other operation writes
   one — review flags a missing ADR back to the owning scope."
6. Update every remaining `#10-agent-contracts` anchor link inside `workflow.md`
   itself to `#10-operation-contracts`.
7. Repeat steps 1–2 and 6 for `workflow-medium.md`: rename its `## 10. Agent
   contracts` heading the same way, rewrite its 5 contract paragraph labels
   (Constitution, Task Planning, Implementation, Validation, Review — no Phase
   Planning or Context contract exists here), and fix its own internal anchor
   links.
8. In `workflow-medium.md` §6 (~line 178), change "Project-level → Constitution
   Agent replans, always writes an ADR." the same way as step 4's second bullet.
9. In `workflow-medium.md` §7 (~lines 192–196, the ADR ownership paragraph —
   note this one also mentions "Task Planning Agent cannot write one" and
   escalating "to the Constitution Agent"), reword every role name to its
   operation label, keeping the sentence's actual meaning (who can/can't write
   an ADR, and where an escalation goes) unchanged.
10. In each of the 8 full-profile skill files listed above, replace the header
    line — currently "Operation for the **{Name} Agent**. Contract:
    [.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts)."
    — with: "This skill performs the **{operation}** operation. Its
    Can/Must/Cannot contract: [.ai/workflow/workflow.md
    §10](.ai/workflow/workflow.md#10-operation-contracts)." (flexible: exact
    sentence wording, as long as it names the operation and points at the
    corrected anchor).
11. In each of the 5 medium-profile skill files listed above, apply the same
    header-line change, pointing at `.ai/workflow/workflow-medium.md`'s
    corrected `#10-operation-contracts` anchor instead.
12. Grep both `workflow.md` and `workflow-medium.md` and every `skills/*/SKILL.md`
    for the pattern `Agent\*\*` and for `#10-agent-contracts` to confirm nothing
    was missed (see Automatic validations).

### Pseudocode

Not needed — this is a mechanical text-editing task with a literal find/replace
list per step, not an algorithm.

### Dependencies

None — this is the first task planned for this phase.

### Expected result

`workflow.md` and `workflow-medium.md` no longer name any agent persona anywhere
(only the generic, already-role-agnostic word "agent" remains where it already
was); every skill header names the operation it performs and links to the
corrected `§10` anchor; every Can/Must/Cannot bullet's actual content is
byte-identical to before, just relabeled.

### Automatic validations

- `grep -rn "Agent\*\*" workflow.md workflow-medium.md skills/*/SKILL.md`
  returns no matches.
- `grep -rn "#10-agent-contracts" workflow.md workflow-medium.md skills/*/SKILL.md`
  returns no matches (confirms the anchor rename propagated everywhere it was
  referenced).
- `grep -n "^## 10\. Operation contracts" workflow.md workflow-medium.md`
  each return one match (heading renamed); `grep -rlc "10-operation-contracts"
  skills/*/SKILL.md | grep -v ":0" | wc -l` returns 13 (every skill's header
  references the new anchor).

### Manual validations

- Read `workflow.md` §4, §6, §7, §10 and `workflow-medium.md` §6, §7, §10
  end-to-end and confirm each reads naturally after the rename — no leftover
  pronoun mismatch ("it" referring to a now-absent "Agent" noun) or broken
  sentence structure.
- Spot-check 2–3 of the 13 updated skill headers (e.g. `define-phase`,
  `validate-work-medium`) to confirm the operation name matches what that skill
  actually does and the anchor link resolves to the right heading.
- Confirm every Can/Must/Cannot bullet's wording is unchanged from before this
  task, by diffing against the pre-task version of each contract paragraph.
