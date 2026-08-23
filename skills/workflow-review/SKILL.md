---
name: workflow-review
description: Use this skill to review a task or phase's implementation and validation results for scope, complexity, architecture, missing validation, or context issues — at task-completion-review/phase-completion-review, after validation passes. Distinct from task-review/phase-review (plan approval) and from workflow-validation (correctness). Never silently fix issues — report and stop for the gate.
---

# Skill: workflow.review

Operation for the **Review Agent**. Contract:
[.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts).

**All `.ai/`-artifact paths below are relative to the project root,
not to this skill file — write the full `.ai/...` path.** Status
values you set here (`reviewing`, `complete`) are two of exactly eight
in a closed enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)
for the full list; never invent one not on it.

## When to use

After validation passes, before a task or phase is marked complete —
this is the "Review" step in the lifecycle
(`Implement → Validate → Review → Context Evaluation → Complete`), a
different moment from the `task-review`/`phase-review` gates (which
approve the *plan*, before any implementation happens — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)'s
naming note). Don't confuse the two just because both are called
"review." Distinct from validation too: see
[.ai/workflow/workflow.md §8](.ai/workflow/workflow.md#8-validation-vs-review).

## Inputs

- The task's detail (its own file at `full`; the inline block under
  its table row at `medium`/`lite`) or the phase file (`full`/`medium`
  only — no phase layer at `lite`, §14), and the actual changes made.
- Tests and validation results (the task's Status in its owning Tasks
  table; the phase file's Validations section at `full`/`medium`).
- Relevant context (`.ai/context/` at `full`; `techstack.md`'s or
  `project.md`'s `## Context` subsection at `medium`/`lite`) and ADRs.

## Procedure

1. Read `.ai/info.md` fresh — confirms gate authority (§14 for which
   gate applies at your profile); don't rely on a read from earlier in
   the session. Set Status to `reviewing` — in the task's row in its
   owning Tasks table (the phase file's at `full`/`medium`,
   `.ai/project.md`'s Roadmap table at `lite`) for a task-level review,
   or the phase's row in `.ai/constitution/roadmap.md` for a
   phase-level review (`full`/`medium` only — no phase layer at
   `lite`). Update `.ai/info.md`'s Status section to match.
2. Confirm the change matches its stated scope — flag anything done
   that wasn't in the plan (scope violation) or required but missing
   (requirement mismatch).
3. Check for unnecessary complexity relative to the stated objective.
4. Check consistency with existing architecture and any relevant ADRs
   in `.ai/decisions/`.
5. Check that validation coverage actually matches what the
   requirements call for — flag missing validation.
6. Check that context still accurately describes the result — flag
   inconsistencies for the context skill to fix. At `full`:
   `.ai/context/context.md` and its listed files, plus the phase
   file's own Context section. At `medium`: `techstack.md`'s
   `## Context` subsection, plus the phase file's own Context section.
   At `lite`: `project.md`'s Techstack `## Context` subsection (no
   phase-level Context section exists).
7. Check for undocumented decisions — an architectural choice with no
   corresponding ADR. Flag it back to the agent whose scope produced
   it (see [.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts)) —
   do not write the ADR yourself.
8. Report findings — approve, or changes requested. Do not silently
   fix issues yourself unless your entry in `.ai/info.md` explicitly
   grants implementation authority.
9. Commit if you made any changes to context/ADR files as part of
   flagging (see
   [.ai/workflow/workflow.md §13](.ai/workflow/workflow.md#13-commit-discipline)).
   At `full`/`medium`: stop for `task-completion-review` (task-level)
   or `phase-completion-review` (phase-level) — see `.ai/info.md`.
   **Clean findings are not themselves approval** — even if you found
   nothing wrong, stop and wait for an explicit yes before anything
   gets marked complete; don't treat "I approve of what I found" as
   the same thing as the human's sign-off (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)). If
   changes were requested instead, return to the implementation loop —
   there's nothing to stop for until it comes back for review again.
   **At `lite`, don't stop here at all** — these findings aren't
   themselves the gate; carry them straight into `workflow-context`'s
   task-completion sub-operation, which presents validation + review +
   context findings together and is where the single `task-completion`
   gate actually stops (§14).
10. **At `full`/`medium`, when approval comes back, that's a separate
    turn:** in `manual`/`assisted` mode, report the approval and
    explicitly ask whether to run `workflow-context` now to finalize
    completion, rather than starting it in the same response. **At
    `lite`**, there's no separate approval to wait for here (step 9) —
    proceed directly into `workflow-context`'s task-completion
    sub-operation in the same turn; that operation is itself where the
    turn stops for the single `task-completion` gate.

## Output

A review verdict (approve / changes requested) with findings listed
against the checks above. At `full`/`medium`, if approved: the
task/phase left at Status `reviewing` in the relevant table and
`.ai/info.md`, ready for `workflow-context` to mark it `complete` —
review itself never sets Status to `complete`. At `lite`: findings
handed directly to `workflow-context`, which presents them at the
combined `task-completion` gate.
