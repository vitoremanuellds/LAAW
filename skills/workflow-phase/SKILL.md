---
name: workflow-phase
description: Use this skill to define a new phase (phases/p{NN}-{name}.md, a single file with Context, Requirements, Plan, Validations, and an embedded task table) or to replan an existing phase after a phase-level deviation. Trigger this whenever the user wants to break the roadmap into a concrete phase, define what must be true for a phase to be done, or plan the sequence of work for a phase. Requires the constitution (mission/techstack/roadmap) to already exist — use workflow-constitution first if it doesn't. Do not use this for individual task breakdown, task ID assignment, or populating the task table with anything beyond stub titles — even though the Plan section looks task-like, task planning is a separate operation; see workflow-task for that, invoked only after this phase's plan is reviewed.
---

# Skill: workflow.phase

Operation for the **Phase Planning Agent**. Contract:
[../../workflow.md §10](../../workflow.md#10-agent-contracts).

## When to use

Defining a new phase, or replanning one after a phase-level deviation
(see [../../workflow.md §6](../../workflow.md#6-deviations)).

## Inputs

- [../../../constitution/roadmap.md](../../../constitution/roadmap.md)
- Relevant [context/context.md](../../../context/context.md) and whatever
  files it points to — only what this phase actually touches.
- If replanning: the deviation that triggered it, and completed tasks
  from the prior plan.

## Procedure

Steps 1–6 require no prior approval — draft the whole file before
stopping for anything. Only step 7 is gated.

1. Read the roadmap entry for this phase. Don't touch its Status yet —
   whether this is a first draft (already `not-planned`, set by
   `workflow-constitution`) or a replan (already `in-progress`), leave
   it as-is until step 5. Read only the `context/` files relevant to
   this phase — do not read the whole `context/` tree.
2. Write `phases/p{NN}-{name}.md` in one file, with these sections:
   - **Context** — architecture, modules, domain concepts, constraints
     specific to *this* phase. Don't repeat `context/context.md` —
     link to the specific files there instead.
   - **Requirements** — outcomes that must be true for the phase to be
     complete. Outcomes, not steps.
   - **Plan** — the ordered sequence of work. Defines *what* must
     happen; task files later define *how*.
   - **Validations** — automated/integration/manual validations,
     acceptance criteria, known edge cases.
   - **Tasks** — a table, initially with **no rows** (or, if
     replanning, only the rows that already existed): `| ID | Title |
     Purpose | Depends on | Status |`. Leave it empty/unchanged here —
     `workflow-task` populates it, not you.
3. If replanning: fold in what's already complete rather than
   discarding it; note the change in the file itself (Git carries the
   prior version). The existing Tasks table rows carry over unchanged —
   replanning the phase doesn't touch task rows.
4. Update `info.md`'s Status section: set `Active phase` to this
   phase's ID (Status *values* live only in `roadmap.md`, not here —
   see [../../workflow.md §11](../../workflow.md#11-status-the-fast-pointer-and-the-permanent-record)).
5. **Set the phase's Status to `awaiting-plan-review` in
   `../../../constitution/roadmap.md` — unconditionally, including when
   replanning mid-phase with tasks actively `in-progress`.** This is
   not a contradiction: Status tracks whether *this plan* has been
   reviewed, not whether execution is happening. A replanned phase file
   is a fresh draft and needs its own review regardless of what
   unaffected tasks are doing. Do not reason "it's already in-progress,
   so nothing needs to change" — that conflates two different things
   this one field can't both represent, and the review requirement
   wins.
6. Commit the draft (see
   [../../workflow.md §13](../../workflow.md#13-commit-discipline)). Stop for
   phase plan review (`phase-review` gate) — see
   [../../../info.md](../../../info.md) (read fresh, not from memory).
   Stop your turn here. Do not continue into task breakdown or task
   IDs — that's a separate operation
   ([workflow-task](../workflow-task/SKILL.md)). Approval unlocks task
   *planning*, not implementation — `task-review` is a separate gate
   still to come after tasks exist. **When approval comes back, that's
   a separate turn:** set the phase's Status to `plan-approved` in
   `roadmap.md` — `workflow-task`'s own first step is what later moves
   it to `in-progress`, once task planning genuinely starts. In
   `manual`/`assisted` mode, report the approval and explicitly ask
   whether to proceed to task planning now, rather than starting it in
   the same response (see
   [../../workflow.md §5](../../workflow.md#5-lifecycle--gates)).

## Output

Exactly one file: `phases/p{NN}-{name}.md`, plus Status updates in
`info.md` and `constitution/roadmap.md`.
