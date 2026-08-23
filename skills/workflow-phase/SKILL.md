---
name: workflow-phase
description: Use this skill to define a new phase (phases/p{NN}-{name}.md — Context, Requirements, Plan, Validations, embedded task table) or replan one after a phase-level deviation. Requires the constitution to exist first. Not for task breakdown or task ID assignment, even though the Plan section looks task-like — see workflow-task, invoked only after this phase's plan is reviewed.
---

# Skill: workflow.phase

Operation for the **Phase Planning Agent**. Contract:
[.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts).

## When to use

Defining a new phase, or replanning one after a phase-level deviation
(see [.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations)).

## Inputs

- `.ai/constitution/roadmap.md`
- Relevant `.ai/context/context.md` and whatever files it points to —
  only what this phase actually touches.
- If replanning: the deviation that triggered it, and completed tasks
  from the prior plan.

## Procedure

**All paths below are `.ai/`-prefixed and relative to the project
root — not relative to this skill file.** This is the exact mistake
that has caused a phase file to be created outside `.ai/` before: a
bare or dot-relative path here gets resolved against your current
working directory by a write tool, not against where this skill file
lives. When in doubt, write the full `.ai/...` path. Status values you
set here (`awaiting-plan-review`, `plan-approved`) are two of exactly
eight in a closed enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)
for the full list; never invent one not on it.

Steps 1–6 require no prior approval — draft the whole file before
stopping for anything. Only step 7 is gated.

1. Read the roadmap entry for this phase. Don't touch its Status yet —
   whether this is a first draft (already `not-planned`, set by
   `workflow-constitution`) or a replan (already `in-progress`), leave
   it as-is until step 5. Read only the `.ai/context/` files relevant
   to this phase — do not read the whole `context/` tree.
2. Write `.ai/phases/p{NN}-{name}.md` in one file, with these sections:
   - **Context** — architecture, modules, domain concepts, constraints
     specific to *this* phase. Don't repeat `.ai/context/context.md` —
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
4. Update `.ai/info.md`'s Status section: set `Active phase` to this
   phase's ID (Status *values* live only in `.ai/constitution/roadmap.md`,
   not here — see
   [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)).
5. **Set the phase's Status to `awaiting-plan-review` in
   `.ai/constitution/roadmap.md` — unconditionally, including when
   replanning mid-phase with tasks actively `in-progress`.** This is
   not a contradiction: Status tracks whether *this plan* has been
   reviewed, not whether execution is happening. A replanned phase file
   is a fresh draft and needs its own review regardless of what
   unaffected tasks are doing. Do not reason "it's already in-progress,
   so nothing needs to change" — that conflates two different things
   this one field can't both represent, and the review requirement
   wins.
6. Commit the draft (see
   [.ai/workflow/workflow.md §13](.ai/workflow/workflow.md#13-commit-discipline)). Stop for
   phase plan review (`phase-review` gate) — see `.ai/info.md` (read
   fresh, not from memory). Stop your turn here. Do not continue into
   task breakdown or task IDs — that's a separate operation
   ([workflow-task](.ai/workflow/skills/workflow-task/SKILL.md)). Approval unlocks task
   *planning*, not implementation — `task-review` is a separate gate
   still to come after tasks exist. **When approval comes back, that's
   a separate turn:** set the phase's Status to `plan-approved` in
   `.ai/constitution/roadmap.md` — `workflow-task`'s own first step is
   what later moves it to `in-progress`, once task planning genuinely
   starts. In `manual`/`assisted` mode, report the approval and
   explicitly ask whether to proceed to task planning now, rather than
   starting it in the same response (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).

## Output

Exactly one file: `.ai/phases/p{NN}-{name}.md` — inside `.ai/`, never
at the project root — plus Status updates in `.ai/info.md` and
`.ai/constitution/roadmap.md`.
