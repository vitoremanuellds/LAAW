# Index

Navigation entry point for `.ai/`. Do not load everything linked here —
follow only the link your current operation needs.

## Before doing any work

This project uses a structured agent workflow. Before planning,
implementing, validating, reviewing, or maintaining context:

1. Read [state.md](state.md) — what phase/task is active right now.
2. Read [policy.md](policy.md) — who is authorized to do what.
3. Use the matching skill under `skills/` for the operation you're
   performing — see the lookup table below. Read [workflow.md](workflow.md)
   in full unless the skill you're using says otherwise for its own
   operation (currently only `workflow-implementation` does — it's
   invoked too often per phase to justify the reread every time).
4. Do not bypass a gate unless the policy explicitly authorizes you to.

Do not read the rest of `.ai/` speculatively. Start here, then follow
only the links your current task actually needs.

## Protocol

- [workflow.md](workflow.md) — the protocol itself
- [policy.md](policy.md) — who is authorized for each gate
- [state.md](state.md) — what is active right now
- [structure.md](structure.md) — directory layout and link rules
- [lifecycle.md](lifecycle.md) — full flow diagrams
- [deviations.md](deviations.md) — deviation rules
- [agents.md](agents.md) — agent contracts

## Constitution

- [mission.md](constitution/mission.md)
- [techstack.md](constitution/techstack.md)
- [roadmap.md](constitution/roadmap/roadmap.md)

## Project Context

- [context.md](project-context/context.md)
- [structure.md](project-context/structure.md) — project's own structure
  (not to be confused with `.ai/structure.md` above)
- [modules/](project-context/modules/)

## Decisions

- [decisions/index.md](decisions/index.md) — topic lookup before
  writing a new ADR
- [decisions/](decisions/) — the ADRs themselves

## Current Work

- Active phase and task: see [state.md](state.md)
- All phases: [phases/](phases/)
- Each phase's `tasks/index.md` lists its tasks, status, and
  dependencies — check it before opening individual task files.

## Skill Lookup

| Operation | Skill |
|---|---|
| Define/update mission, techstack, roadmap | `skills/workflow-constitution/` |
| Define a phase (context, requirements, plan, validations) | `skills/workflow-phase/` |
| Define a task (context, implementation) | `skills/workflow-task/` |
| Write/modify/delete project code for an already-planned task | `skills/workflow-implementation/` |
| Run task or phase validation | `skills/workflow-validation/` |
| Review implementation, plan, or completed work | `skills/workflow-review/` |
| Evaluate/propagate context after task or phase completion | `skills/workflow-context/` |

Each skill's `SKILL.md` follows [workflow.md](workflow.md) — it does not
redefine the protocol.
