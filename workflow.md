# Agent Workflow Protocol

This file is the source of truth for how work is organized and performed.

It defines **what must happen**. Skills define **how** an agent performs it.
Execution policy (`.ai/policy.md`) defines **who** is authorized to do it.

Do not duplicate this file's rules elsewhere. Reference it.

---

## 1. Principles

1. Agents do not reconstruct information that can be persisted cheaply.
2. Persist knowledge, not reasoning.
3. Read only what the current task needs. Never load the whole `.ai/` tree.

---

## 2. Artifact Hierarchy

```
Constitution (mission, techstack, roadmap)
  → Project Context (context, structure, modules/*)
  → Decisions (ADRs)
  → Phases (context, requirements, plan, validations)
      → Tasks (context, implementation)
```

See [Directory Structure](structure.md) for exact paths.

Target size: ~2048 tokens per artifact. Split artifacts that mix concerns
rather than letting them grow.

---

## 3. Context Rule

1. Read the artifact defining the current task.
2. Read its direct references (task → phase context → project context).
3. Follow further links only if the task cannot be completed without them.
4. Never explore unrelated project areas "just in case."

Links are pointers, not preloads.

---

## 4. Lifecycle

```
Constitution → Phase → Requirements → Plan → Validations → Tasks
  → Task Context → Task Implementation → Implement → Validate
  → Review → Context Evaluation → Task Complete
  → (repeat) → Phase Validation → Phase Review
  → Reconcile Phase Context → Reconcile Project Context → Phase Complete
```

Full diagram: [Lifecycle Diagram](lifecycle.md)

### Task completion requires

- Implementation done.
- Validation passed (or documented exception).
- Review passed per policy.
- Context evaluated (see §6).
- `.ai/state.md` updated.

### Phase completion requires

- All tasks complete.
- Phase requirements + validations satisfied.
- Phase review passed.
- Phase and project context reconciled.
- Required ADRs exist.

---

## 5. Deviations

A deviation = actual work materially differs from the approved plan.
Minor detail corrections (wrong file, small mismatch) are not deviations —
just fix and continue.

Record a deviation when: a planned approach fails, scope must change
materially, or an architectural assumption breaks.

Deviation lifecycle: `OPEN → ADDRESSED → INCORPORATED`, then delete the
deviation file — the fact must already live in the plan, implementation,
or an ADR. Git keeps the history.

Task-level deviation → replan task.
Phase-level deviation → replan phase.
Project-level deviation → replan project + write an ADR.

Full rules: [Deviations](deviations.md)

---

## 6. Context Propagation

```
Task done   → evaluate → update Phase Context if future tasks need it
Phase done  → reconcile Phase Context → promote persistent facts to
              Project Context
```

Propagate: architecture facts, invariants, module responsibilities,
dependencies, constraints, domain knowledge.

Never propagate: task history, temporary details, internal reasoning,
progress reports, anything already recorded elsewhere.

### Structure map is not judgment-based

`project-context/structure.md` is a mechanical map of the file tree, not
a knowledge-propagation decision. Any task that creates, deletes, or
moves a file or directory must update it as part of implementation
itself — not deferred to task-completion context evaluation. See
[Implementation Skill §3](skills/workflow-implementation/SKILL.md).

---

## 7. Decisions (ADRs)

Write an ADR when a decision is deliberate and future work needs to know
it — not every deviation produces one, and not every ADR comes from a
deviation. Format: [ADR Template](decisions/_template.md).

**Ownership:** whichever agent's scope produced the decision writes it —
Constitution Agent (project-level), Phase Planning Agent (phase-level),
Implementation Agent (decisions made or discovered during
implementation). No other agent writes an ADR; a Review Agent that spots
a missing one flags it back to the owning scope. See
[agents.md](agents.md).

Before writing a new ADR, check [decisions/index.md](decisions/index.md)
— a related decision may already exist. Whoever writes the ADR also adds
its entry to the index in the same step.

---

## 8. Validation vs Review

- **Validation** — does the implementation satisfy the requirements?
- **Review** — is the work appropriate, coherent, and consistent with the
  project's direction?

Both are required and distinct. A validation agent must not edit
implementation to force a pass — failures return to the implementation
loop. A review agent must not silently fix issues unless its policy
grants implementation authority.

---

## 9. Gates

A gate blocks *advancing past* a completed artifact until its condition
is met — it never blocks *producing* the artifact in the first place.
Drafting a phase plan, a task, or an implementation never requires prior
approval; only moving past that draft's review checkpoint does. If
you're unsure whether you're "allowed" to start drafting, the answer is
yes — check the relevant skill's procedure before making any judgment
about what a gate permits.

Standard gates:

```
constitution-review · phase-review · task-review
task-validation · phase-validation · context-update
```

Each gate's authority (`human` | `agent`) is set in `.ai/policy.md`.
Default authority is always human unless the policy explicitly delegates it.

---

## 10. Execution Modes

`manual` → `assisted` → `delegated` → `autonomous`

Mode changes only affect who satisfies gates in `.ai/policy.md`. This file
never changes as a result. See [Execution Policy](policy.md).

---

## 11. Agents

Each agent type has an explicit can/cannot contract. See
[Agent Contracts](agents.md). In short:

| Agent | Can | Cannot |
|---|---|---|
| Constitution | write mission/techstack/roadmap | touch project code |
| Phase Planning | write phase artifacts | implement code |
| Task Planning | write task context/implementation | implement code |
| Implementation | modify project files | change approved requirements/plan silently |
| Validation | run checks, report failures | edit code to force a pass |
| Context | update phase/project context | copy task history, record reasoning |

---

## 12. IDs

`P01`, `P01-T01`, ... — sequential, never reused, never renumbered on
deletion. Subtasks (`P01-T01-S01`) only if a task must be split.

---

## 13. Multi-Agent / Multi-Human

Independent tasks may run in parallel across agents/humans. Shared state
lives in Git and `.ai/state.md` — never invent a second synchronization
mechanism in Markdown. Avoid concurrent edits to the same task, files, or
workflow artifact.

---

## 14. Entry Point

Agents start at `AGENTS.md`, which points here. This file points to
skills, policy, and state — it does not re-explain them.
