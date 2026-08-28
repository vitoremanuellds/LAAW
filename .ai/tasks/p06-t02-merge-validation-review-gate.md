# P06-T02: Merge Validation and Review into one gate per task/phase, still running two internal checks

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 2: `workflow.md` currently presents `task-validation`/`task-completion-review`
(and their phase-level equivalents `phase-validation`/`phase-completion-review`) as
four fully independent gates in §5's lifecycle diagram and gate list, and describes
Validation vs Review as two unrelated concerns in §8. The resolved decision is to
present each pair as **one named gate that internally sequences a mechanical check
then a judgment check** — a documentation restructuring, not a behavior or policy
change.

**This is presentational only — nothing about the underlying mechanism changes:**
`validate-work-full` and `review-work-full` (and their medium-profile equivalents)
stay exactly as they are; `.ai/info.md`'s Policy section keeps exactly the same four
gate keys it has today (`task-validation`, `task-completion-review`,
`phase-validation`, `phase-completion-review`); the execution-mode defaults for each
of those four keys are unchanged. What changes is how §5/§8 (and the leftover §10
paragraph split noted below) *narrate* the pair — as one gate with two internal
checks, not two gates — so a reader sees the mechanical-then-judgment sequencing as
one coherent step instead of two disconnected ones. The merged gate's outward name is
the existing completion-review name (`task-completion-review` / `phase-completion-review`)
— already used elsewhere in the file (e.g. `propagate-context`'s preconditions, §5's
"Task/Phase complete requires" bullets) as the name of the thing that ultimately
unlocks completion; `task-validation`/`phase-validation` become the name of the first
internal check within it, still individually addressable in `info.md`'s Policy (its
YAML keys and structure are untouched by this task).

**Leftover from P06-T01** (see that task's result note in the phase file): §10 was
rewritten to one paragraph per operation, each labeled `**{Operation} operation**
(\`{skill-name}\`)`. The Validation and Review paragraphs are still separate
(`**Validation operation** (\`validate-work-full\`)` and `**Review operation**
(\`review-work-full\`)`) — T01 deliberately left them unmerged for this task to
handle, since it's this decision's content, not T01's.

## Implementation

### Objective

Restructure `workflow.md` §5, §8, and §10's Validation/Review paragraphs so the
task-level and phase-level validation+completion-review pairs each read as one named
gate with two internal checks, while leaving `info.md`'s Policy keys, both skills'
own procedures, and every other section untouched.

### In scope

- §5's lifecycle diagram (the `Validate → Review` step).
- §5's gate bullet list (merge the `task-validation` + `task-completion-review`
  bullets into one; merge `phase-validation` + `phase-completion-review` into one).
- §5's Execution modes bullet list (the `assisted` bullet currently states
  `task-validation`/`phase-validation`/`context-update` default `agent`; restate this
  per merged gate: within `task-completion-review`/`phase-completion-review`, the
  mechanical check defaults `agent`, the judgment check defaults `human`).
- §5's "Completion-review gates ≠ plan-review gates" paragraph — update its wording
  if it still implies four separate always-two-of-them-together gates.
- §8, merged into one short paragraph (still under the `## 8.` heading — do not
  renumber or delete the section) describing the two checks as internal steps of one
  gate rather than two independent concerns.
- §10's `**Validation operation**` and `**Review operation**` paragraphs, merged into
  one `**Validation-review operation**` paragraph naming both skills.

### Out of scope

- `.ai/info.md` — its Policy YAML keys and structure are unchanged; this is a
  `workflow.md` documentation change only.
- `skills/validate-work-full/SKILL.md`, `skills/review-work-full/SKILL.md`, and their
  medium-profile equivalents — no behavior or wording change; they keep checking
  `task-validation`/`task-completion-review` (or the phase equivalents)
  independently, exactly as today.
- Any other §10 paragraph besides Validation/Review's.
- `P06-T03`'s ADR-timing edits to §7/§9 — separate decision, separate task.

### Files to modify

- `workflow.md` — §5, §8, §10 (Validation/Review paragraphs only).

### Steps

1. In §5's lifecycle diagram, merge the `Validate → Review` pair of arrows into a
   single labeled step, e.g. `Implement → Task Completion Review (validate, then
   review) → Context Evaluation → ...` (flexible: exact diagram wording — binding:
   the diagram must show one step covering both checks, not two separate arrows).
   Apply the same merge to the phase-level `Phase Validation → Phase Completion
   Review` pair later in the same diagram.
2. In §5's gate bullet list, replace the separate `task-validation` and
   `task-completion-review` bullets with one bullet under the `task-completion-review`
   name, describing both checks inline — e.g. "after implementation: first a
   mechanical check (does it meet the task's requirements?), then a judgment check
   (is it appropriate/coherent?). Unlocks marking the task complete." (flexible: exact
   prose — binding: both checks named, in order, under one bullet, unlock statement
   preserved from the original `task-completion-review` bullet). Do the same for
   `phase-validation` + `phase-completion-review` under `phase-completion-review`.
3. In §5's Execution modes list, rewrite the `assisted` bullet so it states the
   mechanical/judgment split per merged gate rather than per separate gate name —
   e.g. "within `task-completion-review`/`phase-completion-review`, the mechanical
   check defaults `agent`, the judgment check defaults `human`; `context-update`
   also defaults `agent`; rest `human`" (flexible: exact wording — binding: the
   auto-pass-mechanical/hold-for-human-judgment split must still be readable per
   gate, matching what `validate-work-full`/`review-work-full` actually do today).
   Check the `manual`/`delegated`/`autonomous` bullets too — update only if they
   reference the now-removed separate gate names; leave alone otherwise.
4. Update the "Completion-review gates ≠ plan-review gates" paragraph (and the
   "Task complete requires"/"Phase complete requires" bullets just above it) if their
   wording still lists `task-validation`/`task-completion-review` as two separate
   items rather than one gate's two checks — keep the actual completion requirements
   (implementation + both checks + context evaluated + table row marked + `info.md`
   cleared) unchanged, only the framing.
5. Rewrite §8 as one short paragraph: state that the merged gate's two checks are
   "does it satisfy requirements?" (mechanical) and "is it appropriate, coherent,
   consistent with direction?" (judgment) — keep both existing constraints (validation
   never edits to force a pass; review never silently fixes unless `info.md` grants
   implementation authority). Remove the `[HUMAN]` comment at the end of §8, since
   this step addresses it. Keep the `## 8.` heading and section itself — do not fold
   it into §5.
6. In §10, merge `**Validation operation** (\`validate-work-full\`)` and `**Review
   operation** (\`review-work-full\`)` into one paragraph, labeled
   `**Validation-review operation** (\`validate-work-full\`, \`review-work-full\`)`,
   preserving every existing Can/Must/Should-not bullet from both original paragraphs
   without dropping content (flexible: how the two skills' Can/Must/Should-not
   clauses are merged into one flowing list — binding: no clause from either original
   paragraph is lost).

### Dependencies

`P06-T01` (already complete — this task builds on its §10 paragraph structure and
operation-labeling convention).

### Expected result

`workflow.md` presents `task-completion-review` and `phase-completion-review` each as
one gate with two internal checks in §5's diagram, gate list, and execution-mode
defaults; §8 is one short paragraph instead of a bare bullet pair; §10 has one merged
Validation-review paragraph instead of two. `info.md` and both skills are untouched.

### Automatic validations

- `grep -n "task-validation.*gate\b" workflow.md` and
  `grep -n "phase-validation.*gate\b" workflow.md` — confirm neither is still
  presented as its own standalone gate bullet (a mention as the internal-check name
  inside the merged bullet is fine; a separate `- **\`task-validation\`**` /
  `- **\`phase-validation\`**` bullet is not).
- `grep -n "Validation operation\|Review operation" workflow.md` returns no matches
  in §10 (confirms the merge into `Validation-review operation`).
- `grep -c "\[HUMAN\]" workflow.md` — count drops by exactly 1 (§8's comment).
- `diff <(git show HEAD:.ai/info.md) .ai/info.md` — no output (confirms `info.md`
  untouched by this task; re-run right before commit to catch unrelated
  in-session pointer edits).
- `diff <(git show HEAD:skills/validate-work-full/SKILL.md) skills/validate-work-full/SKILL.md`
  and the same for `skills/review-work-full/SKILL.md` — no output.

### Manual validations

- Read §5's rewritten lifecycle diagram and gate bullets end-to-end: confirm a
  reader can tell, for both task and phase level, that one gate runs a mechanical
  check first and a judgment check second, without needing to already know the old
  four-gate structure.
- Confirm the `assisted`-mode bullet still lets a reader determine, per gate, that
  the mechanical check auto-passes while the judgment check waits for a human —
  the exact behavior `validate-work-full`/`review-work-full` already implement.
- Confirm §10's merged Validation-review paragraph reads as one coherent operation
  contract, not two paragraphs stapled together with a shared heading.
