# Agent Workflow Protocol

Source of truth for how work is organized, performed, and by whom.
Self-contained — everything an agent needs to understand the protocol
lives here. Procedural how-to lives in `skills/`, not here. Gate
*authority* (who) lives in [`../policy.md`](../policy.md), not here.

Do not duplicate this file's rules elsewhere. Reference it.

---

## 1. Principles

1. Agents do not reconstruct information that can be persisted cheaply.
2. Persist knowledge, not reasoning.
3. Read only what the current task needs. Never load the whole `.ai/`
   tree speculatively.
4. Use terminal tools (`tree`, `find`, `ls`, `grep`) to discover the
   actual project structure directly — no separate structure map to
   maintain or trust over the real filesystem.

---

## 2. Starting point for any agent

1. Check current status: which phases exist under `../phases/`, each
   phase's Status in `../constitution/roadmap.md`, and (if inside a
   phase) that phase's `tasks/index.md`. No separate state file — the
   folders and indexes *are* the state.
2. Read [`../policy.md`](../policy.md) — who is authorized for the
   gate you're about to hit.
3. Use the matching skill below for the operation you're performing.
   Read the rest of this file in full unless the skill says otherwise
   (currently only `workflow-implementation` skips the reread — it's
   invoked too often per phase to justify it every time).
4. Never bypass a gate unless policy explicitly authorizes you to.

| Operation | Skill |
|---|---|
| Define/update mission, techstack, roadmap | `skills/workflow-constitution/` |
| Define a phase (`context.md` + `phase.md`) | `skills/workflow-phase/` |
| Define a task (`task.md`) | `skills/workflow-task/` |
| Write/modify/delete code for an already-planned task | `skills/workflow-implementation/` |
| Run task or phase validation | `skills/workflow-validation/` |
| Review implementation, plan, or completed work | `skills/workflow-review/` |
| Evaluate/propagate context after task or phase completion | `skills/workflow-context/` |

If you can't find the right skill, re-read this table — don't guess
directory names or loop restating intent.

---

## 3. Directory structure

```
.ai/
├── README.md                 Bootstrap instructions + AGENTS.md snippet
├── policy.md                  Execution policy — gate authority (config, not protocol)
├── workflow/
│   ├── workflow.md              This file
│   ├── decision-template.md      ADR template (fixed — instantiated into decisions/)
│   └── skills/
│       ├── workflow-constitution/SKILL.md
│       ├── workflow-phase/SKILL.md
│       ├── workflow-task/SKILL.md
│       ├── workflow-implementation/SKILL.md
│       ├── workflow-validation/SKILL.md
│       ├── workflow-review/SKILL.md
│       └── workflow-context/SKILL.md
│
├── constitution/
│   ├── mission.md
│   ├── techstack.md
│   └── roadmap.md              Ordered phases + Status column — the phase index
│
├── project-context/
│   ├── context.md               Architecture, conventions, constraints, terminology
│   └── modules/
│       └── auth.md
│
├── decisions/
│   ├── index.md                  Topic lookup, one row per ADR
│   └── d01-decision-name.md
│
└── phases/
    └── p01-phase-name/
        ├── context.md              Shared background for this phase's tasks
        ├── phase.md                 Requirements + Plan + Validations, merged
        └── tasks/
            ├── index.md               ID / title / purpose / deps / status
            └── p01-t01-task-name/
                └── task.md              Context + Implementation, merged
```

**Link rule:** every link is relative to the file containing it, never
to `.ai/` root or repo root. This is what makes the whole tree portable
regardless of what folder it's nested under.

**Naming:** phase dirs `p{NN}-{kebab-name}/`; task dirs
`p{NN}-t{NN}-{kebab-name}/`; decisions `d{NN}-{kebab-name}.md`. IDs
(`P01`, `P01-T01`, ...) are sequential and never reused — deleting
`P01-T03` doesn't free the number; the next task is still `P01-T04`.

**Artifact size target:** ~2048 tokens per file. Split further only if
a file is mixing genuinely independent concerns.

---

## 4. Artifact hierarchy & context rule

```
Constitution (mission, techstack, roadmap)
  → Project Context (context, modules/*)
  → Decisions (ADRs)
  → Phases (context, phase)
      → Tasks (task)
```

An agent reads: the artifact defining its current work → its direct
references → further links only if the task can't be completed
without them. Never explores unrelated project areas "just in case."
A link is a pointer, not a preload.

---

## 5. Lifecycle & gates

```
Constitution → Phase (context + phase.md) → Tasks (task.md)
  → Task Review → Implement → Validate → Review → Context Evaluation
  → Task Complete → (repeat) → Phase Validation → Phase Review
  → Reconcile Phase Context → Reconcile Project Context → Phase Complete
```

**A gate blocks *advancing past* a completed draft — never blocks
*producing* the draft.** Drafting a phase, a task, or an implementation
never needs prior approval; only moving past its review checkpoint
does. If unsure whether you're "allowed" to start drafting, the answer
is yes — check the relevant skill before making any judgment about
what a gate permits.

**Each gate unlocks only the operation immediately following it —
never anything further down the chain.** Passing `phase-review`
unlocks task *planning*, not implementation. Passing `task-review`
unlocks *implementation* for that task, and only that task.

Standard gates: `constitution-review` · `phase-review` · `task-review`
· `task-validation` · `phase-validation` · `context-update`.

**Task completion requires:** implementation done; validation passed
(or documented exception); review passed; context evaluated; the
task's row in `tasks/index.md` marked complete.

**Phase completion requires:** all tasks complete; phase requirements
and validations satisfied; phase review passed; phase and project
context reconciled; required ADRs exist; the phase's row in
`roadmap.md` marked complete.

---

## 6. Deviations

A deviation = actual work materially differs from the approved plan.
Minor detail corrections (wrong file, small mismatch) are **not**
deviations — adjust and continue. Record one when a planned approach
fails, scope must change materially, or an architectural assumption
breaks:

```
Expected:     what the plan assumed
Discovered:   what is actually true
Why it fails: why the original plan can't proceed
Proposed fix: the new approach
Replan?       task / phase / project
```

File: `tasks/p01-t03-.../deviation.md`. Lifecycle:
`OPEN → ADDRESSED → INCORPORATED`, then delete — the fact must already
live in the plan, implementation, or an ADR by then. Git keeps the
history; don't let deviation files accumulate as a log.

- **Task-level** → returns to the implementation loop for that task.
- **Phase-level** → Phase Planning Agent replans (completed tasks are
  inputs, not discarded); writes an ADR if architecturally significant.
- **Project-level** → Constitution Agent replans and always writes an
  ADR — by definition, this changes what future work needs to know.

---

## 7. Decisions (ADRs)

Write an ADR when a decision is deliberate and future work needs to
know it. Not every deviation produces one; not every ADR comes from a
deviation.

**Ownership — whichever agent's scope produced the decision writes
it:** Constitution Agent (project-level) · Phase Planning Agent
(phase-level) · Implementation Agent (during implementation). No other
agent writes one — Review Agent flags a missing ADR back to the owning
scope instead.

Check `../decisions/index.md` before writing a new one. Whoever writes
the ADR copies [`decision-template.md`](decision-template.md) into
`../decisions/d{NN}-{name}.md` and fills it in, adding its index row in
the same step. Template fields: **Decision**, **Context** (link the
deviation if any), **Alternatives Considered**, **Consequences**.

---

## 8. Validation vs. Review

- **Validation** — does the implementation satisfy the requirements?
- **Review** — is the work appropriate, coherent, and consistent with
  the project's direction?

Both required, both distinct. Validation never edits implementation to
force a pass — failures return to the implementation loop. Review
never silently fixes issues unless policy grants implementation
authority.

---

## 9. Context propagation

```
Task done   → does this matter to other tasks this phase? → update phase context.md if yes
Phase done  → does this matter beyond this phase? → promote to project-context/ if yes
```

**Propagate:** architecture facts, invariants, module responsibilities,
dependencies, constraints, domain knowledge.
**Never propagate:** task history, temporary details, internal
reasoning, progress reports, anything already recorded elsewhere.

---

## 10. Agent contracts

No agent determines its own authority — it operates strictly within
its contract below. Gate authority comes from `../policy.md`.

**Constitution Agent** — Can: read project info, create/modify
constitution artifacts, ask for clarification. Must: write an ADR for
project-level decisions. Cannot: touch project code; invent
unsupported requirements.

**Phase Planning Agent** — Can: read constitution + relevant project
context, create phase `context.md` + `phase.md`. Must: write an ADR for
phase-level architectural decisions; update the phase's Status in
`roadmap.md` at each transition (see §11). Cannot: implement code;
**assign task IDs or create anything under `tasks/`** — `phase.md`'s
plan section looks like a task list but isn't one; task breakdown is a
separate, later operation.

**Task Planning Agent** — Can: read phase artifacts + relevant project
files, create `task.md`. Must: create/update `tasks/index.md` whenever
a task is added; update Status there at each transition (see §11).
Cannot: implement code; write an ADR — escalate an architectural
discovery as a phase-level deviation instead.

**Implementation Agent** — Can: read the task + referenced context,
inspect/modify project files, execute tools. Must: update the task's
`tasks/index.md` row (including Status, see §11) as it moves through
implementation; write an ADR for decisions made during implementation
(check the index first). Cannot: silently change approved
requirements or the phase plan.

**Validation Agent** — Can: inspect files, execute validation
commands, report failures; set the task's Status to `validating` in
`tasks/index.md` while running. Should not: modify implementation to
force a pass — return to the implementation loop instead.

**Review Agent** — Can: inspect requirements/plan/implementation/
changes/tests/context/ADRs; flag scope violations, requirement
mismatches, unnecessary complexity, architectural inconsistencies,
missing validation, context inconsistencies, undocumented decisions;
set Status to `reviewing` while running. Should not: silently fix
problems or write a missing ADR itself — flag back to the owning scope.

**Context Agent** — Can: inspect completed work, identify reusable
knowledge, update phase/project context; mark the task's row complete
in `tasks/index.md` and the phase's row complete in `roadmap.md` at
their respective completions. Should not: copy task history into
context; duplicate information already represented elsewhere; record
internal reasoning.

---

## 11. Status vocabulary (indexes, not a state file)

There is no `state.md`. "What's happening right now" is always
answered by reading `roadmap.md` (phase-level) and the relevant
`tasks/index.md` (task-level) — never a separate tracked file.

**`roadmap.md` Status column**, set by Phase Planning Agent /
Context Agent: `planned` · `awaiting-review` · `in-progress` ·
`phase-complete`.

**`tasks/index.md` Status column**, set by whichever agent is
currently acting on the task: `planned` · `awaiting-review` ·
`in-progress` · `validating` · `reviewing` · `complete` · `blocked`.

If you're unsure what's currently active and no index answers it,
check which `phases/`/`tasks/` directories exist — folder presence
itself is signal (a phase with no `phase.md` yet hasn't been planned;
a task directory with no `task.md` doesn't really exist yet).

---

## 12. Multi-agent / multi-human

Independent tasks may run in parallel across agents/humans. Shared
state lives in Git and the indexes above — never invent a second
synchronization mechanism in Markdown. Avoid concurrent edits to the
same task, files, or workflow artifact.

---

## 13. Commit discipline

Commit a draft the moment it's written, before requesting its review
gate — this lets the review happen via `git diff`. Message convention
tied to IDs: `P01: phase drafted`, `P01-T01: task planned`,
`P01-T01: implementation complete`, `P01: phase complete`. Commit again
whenever an index (`roadmap.md`, `tasks/index.md`) changes as part of a
transition.

---

## 14. Entry point

Projects using this workflow point agents here via a short snippet
pasted into their own `AGENTS.md` — see [`../README.md`](../README.md)
for exact bootstrap steps. This file and `skills/` never change per
project; `../policy.md`, `../constitution/`, `../project-context/`,
`../decisions/`, `../phases/` are all per-project content.
