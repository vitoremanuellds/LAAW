---
name: workflow-phase
description: Use this skill to define a new phase (context.md + phase.md under .ai/phases/) or to replan an existing phase after a phase-level deviation. Trigger this whenever the user wants to break the roadmap into a concrete phase, define what must be true for a phase to be done, or plan the sequence of work for a phase. Requires the constitution (mission/techstack/roadmap) to already exist — use workflow-constitution first if it doesn't. Do not use this for individual task breakdown, task ID assignment, or tasks/index.md — even though phase.md's plan section looks task-like, task planning is a separate operation; see workflow-task for that, invoked only after this phase's plan is reviewed.
---

# Skill: workflow.phase

Operation for the **Phase Planning Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

Defining a new phase, or replanning one after a phase-level deviation
(see [../../workflow.md §6](../../workflow.md#6-deviations)).

## Inputs

- [../../../constitution/roadmap.md](../../../constitution/roadmap.md)
- Relevant [project-context](../../../project-context/context.md) — only
  the modules this phase actually touches.
- If replanning: the deviation that triggered it, and completed tasks
  from the prior plan.

## Procedure

Steps 1–5 require no prior approval — draft the full set of phase
artifacts before stopping for anything. Only step 6 is gated.

1. Read the roadmap entry for this phase, and set its Status to
   `in-progress` in `../../../constitution/roadmap.md`. Read only the
   project-context modules it names — do not read the whole
   project-context tree.
2. Write `context.md` — architecture, modules, domain concepts,
   constraints shared by this phase's tasks. Do not duplicate project
   context; link to it.
3. Write `phase.md` with three sections:
   - **Requirements** — outcomes that must be true for the phase to be
     complete. Outcomes, not steps.
   - **Plan** — the ordered sequence of work. Defines *what* must
     happen; task implementations later define *how*.
   - **Validations** — automated/integration/manual validations,
     acceptance criteria, known edge cases.
4. If replanning: fold in what's already complete rather than
   discarding it; note the change in `phase.md` itself (Git carries
   the prior version).
5. Set the phase's Status to `awaiting-review` in
   `../../../constitution/roadmap.md`.
6. Commit the draft (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)). Stop for
   phase review — see [../../../policy.md](../../../policy.md). Stop your
   turn here. Do not continue into task breakdown, task IDs, or
   `tasks/index.md` — that's a separate operation
   ([workflow-task](../workflow-task/SKILL.md)), invoked separately
   once this phase's plan is approved. Approval unlocks task
   *planning*, not implementation — `task-review` is a separate gate
   still to come after tasks exist.

## Output

Exactly these two files, nothing else:
`phases/p{NN}-{name}/context.md`, `phases/p{NN}-{name}/phase.md` — plus
the Status update in `../../../constitution/roadmap.md`.
