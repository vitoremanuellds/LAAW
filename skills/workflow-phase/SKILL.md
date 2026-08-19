---
name: workflow-phase
description: Use this skill to define a new phase (context.md, requirements.md, plan.md, validations.md under .ai/phases/) or to replan an existing phase after a phase-level deviation. Trigger this whenever the user wants to break the roadmap into a concrete phase, define what must be true for a phase to be done, or plan the sequence of work for a phase. Requires the constitution (mission/techstack/roadmap) to already exist — use workflow-constitution first if it doesn't. Do not use this for individual task breakdown, task ID assignment, or tasks/index.md — even though plan.md's steps look task-like, task planning is a separate operation; see workflow-task for that, invoked only after this phase's plan is reviewed.
---

# Skill: workflow.phase

Operation for the **Phase Planning Agent**. Contract:
[../../agents.md#phase-planning-agent](../../agents.md#phase-planning-agent).

## When to use

Defining a new phase, or replanning one after a phase-level deviation
(see [../../deviations.md](../../deviations.md)).

## Inputs

- [../../constitution/roadmap/roadmap.md](../../constitution/roadmap/roadmap.md)
- Relevant [project-context](../../project-context/context.md) — only
  the modules this phase actually touches.
- If replanning: the deviation that triggered it, and completed tasks
  from the prior plan.

## Procedure

Steps 1–6 require no prior approval — draft the full set of phase
artifacts before stopping for anything. Only step 7 is gated.

1. Read the roadmap entry for this phase. Read only the project-context
   modules it names — do not read the whole project-context tree.
2. Write `context.md` — architecture, modules, domain concepts,
   constraints shared by this phase's tasks. Do not duplicate project
   context; link to it.
3. Write `requirements.md` — outcomes that must be true for the phase to
   be complete. Outcomes, not steps.
4. Write `plan.md` — the ordered sequence of work. This defines *what*
   must happen; task implementations later define *how*.
5. Write `validations.md` — automated/integration/manual validations,
   acceptance criteria, known edge cases.
6. If replanning: fold in what's already complete rather than discarding
   it; note the change in `plan.md` itself (Git carries the prior
   version).
7. Stop for phase review — see [../../policy.md](../../policy.md). Stop
   your turn here. Do not continue into task breakdown, task IDs, or
   `tasks/index.md` — that's a separate operation
   ([workflow-task](../workflow-task/SKILL.md)), invoked separately once
   this phase's plan is approved. Approval unlocks task *planning*, not
   implementation — `task-review` is a separate gate still to come after
   tasks exist.

## Output

Exactly these four files, nothing else:
`phases/p{NN}-{name}/{context,requirements,plan,validations}.md`
