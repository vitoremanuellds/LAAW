# Agent Workflow

Source of truth for how work is organized, performed, and by whom —
don't duplicate its rules elsewhere, reference it. Occasional-need
rationale and detail lives in `reference/`, one file per concept,
linked where needed below.

---

## 1. Principles

1. Agents do not reconstruct information that can be persisted cheaply.
2. Persist knowledge, not reasoning.
3. Read only what the current task needs — never the whole `.ai/` tree.

---

## 2. Starting point for any agent

1. **Read `../info.md` fresh, every gate check.** Policy = gate
   authority; status lives elsewhere (§11). Missing → unbootstrapped:
   gates are human-owned; run `create-constitution` first — it always
   scaffolds `info.md`, even if you don't want its mission/techstack
   content.
2. **Read the matching skill file before acting, every time.** See
   [reference/reread-skill-discipline.md](reference/reread-skill-discipline.md).
3. Never bypass an unauthorized gate without confirming with the human
   first.

| Operation | Skill |
|---|---|
| Bootstrap several layers at once | `bootstrap` |
| Constitution | `create-constitution` |
| Phase planning | `define-phase` |
| Task planning | `define-task` |
| Implementation | `implement-task` |
| Validation | `validate-work` |
| Review | `review-work` |
| Context — propagate/finalize | `propagate-context` |
| Context — survey codebase | `build-context` |

---

## 3. Directory structure

```
.ai/workflow/       submodule, never written to — workflow.md, reference/, templates/, skills/
.ai/info.md         Policy only — gate authority; always present, not an optional layer
.ai/constitution/   mission.md, techstack.md — optional
.ai/context/        context.md + whatever fits — optional
.ai/decisions/      decisions.md + adr{NN}-{name}.md — optional
.ai/phases/         phases.md (index) + p{NN}-{name}.md, own Context + task table — optional
.ai/tasks/          tasks.md (orphan index) + p{NN}-t{NN}-{name}.md (phase-linked) + t{NN}-{name}.md (orphan) — the one mandatory layer
.ai/workbench/      freeform scratch — planning notes, Q&A, prompt drafts; disposable, not part of the permanent record — optional
```

Presence is inferred from existence — no directory means that layer is
off for this project; `.ai/tasks/` is the only one every project has.
How a layer comes into existence on first use: see
[reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)
(or run `bootstrap` to set up several at once).

`.ai/tasks/` holds two task-file shapes, distinguished by filename
alone, each its own ID sequence: `p{NN}-t{NN}-{name}.md` (linked to a
phase) and `t{NN}-{name}.md` (orphan — no phase, whether this project
has no `phases/` at all or this task just doesn't need one). A
phase-linked task is indexed only in its phase file's task table; an
orphan task is indexed in `.ai/tasks/tasks.md` — never both, never
neither.

Flat by design; paths always `.ai/`-prefixed off the project root,
never bare/dot-relative (why:
[reference/directory-and-links.md](reference/directory-and-links.md)).
IDs sequential, never reused. `.ai/workbench/` is the one exception to
"part of the permanent record" above — nothing in it is schema- or
Status-tracked, and no skill reads it as an input dependency (why:
[reference/directory-and-links.md](reference/directory-and-links.md)).

---

## 4. Artifact hierarchy & context rule

```
Constitution → Context → Decisions → Phases (own Context) → Tasks (own Context)
```

Each level links only to the one above it — no lateral shared-context
files; that belongs in `context/` (§1.3).

Every level except Tasks is optional (§3); a task can skip its phase
link (an orphan task) independently of whether the project uses phases
elsewhere.

**Phase** = feature-sized slice of work (*what*). **Task** = one
mechanical unit within a phase's Plan (*how*), drafted by
`define-task`. One or two steps is a task, not a phase.

---

## 5. Lifecycle & gates

```
Constitution → Constitution Review → Phase → Phase Plan Review
  → Tasks → Task Plan Review → Implement
  → Task Completion Review (validate, then review)
  → Context Evaluation → Task Complete → (repeat)
  → Phase Completion Review (validate, then review)
  → Reconcile Phase/Project Context → Phase Complete
```

| Gate | Runs after | Unlocks |
|---|---|---|
| `constitution-review` | constitution draft | phase planning |
| `phase-review` | phase plan draft | task planning |
| `task-review` | task-batch draft | implementation |
| `task-completion-review` | implementation (mech., then judgment) | task complete |
| `phase-completion-review` | all tasks done (mech., then judgment) | phase complete |
| `context-update` | alongside task/phase completion | — |

Gates block *advancing past* a draft, never *producing* one.
**Unlocking ≠ starting** — `manual`/`assisted` stops and asks before
the next step; `delegated`/`autonomous` chains through.

**Modes** (`info.md`: `mode` + `overrides`):

| Mode | Plan-review | Compl.: mech. | Compl.: judgment | `context-update` |
|---|---|---|---|---|
| `manual` | human | human | human | human |
| `assisted` (default) | human | agent | human | agent |
| `autonomous` | agent | agent | agent | agent |

`delegated`: no defaults — every gate listed in `overrides`, else
`human`.

**Task complete:**
- implementation + `task-completion-review` (both checks)
- context evaluated
- phase row complete

**Phase complete:**
- all tasks complete + `phase-completion-review` (both checks)
- context reconciled
- required ADRs exist
- `phases.md` row complete

Both leave `info.md` untouched — it holds no status to clear (§11).

Starting without every phase already planned is normal:
[reference/starting-without-a-plan.md](reference/starting-without-a-plan.md).

---

## 6. Deviations

Deviation = work materially differs from the approved plan; a mismatch
against a plan detail marked flexible isn't one, everything else is.
Recorded inline as a `## Deviations` subsection in the task file —
never separate; lifecycle `OPEN → ADDRESSED → INCORPORATED`, deleted
once the fact lives in the plan, implementation, or an ADR. Field
format: `define-task`'s task-file conventions. Pseudocode is
guidance, not contract — deviating from it isn't itself a deviation;
only the underlying *approach* being wrong is.

- **Task-level** → back to the implementation loop.
- **Phase-level** → replanned via `define-phase` (completed tasks
  carry over; ADR if architecturally significant).
- **Project-level** → replanned via `create-constitution`,
  always an ADR.

New, working-as-planned scope on approved work isn't a deviation — it
still needs its own `phase-review`/`task-review`.

---

## 7. Decisions (ADRs)

Write one when a decision is deliberate and future work needs to know
it — not every deviation produces one, not every ADR comes from one.

**Owner writes it, at the moment of the decision:**
- `create-constitution` — project-level
- `define-phase` — phase-level
- `implement-task` — during implementation

No other operation writes one — review flags a missing one back to
the owning scope. Promotion into `context/` follows §9; writing the
ADR itself doesn't wait. A superseding ADR updates both rows'
Relations, not a deletion — Git keeps history.

---

## 8. Validation vs Review

The completion-review gate's two checks, in order: **validation** —
does it satisfy requirements (mechanical)? — then **review** — is it
appropriate, coherent, consistent with direction (judgment)? Both
required, both distinct. Validation never edits to force a pass;
review never silently fixes unless `info.md` grants that authority.

---

## 9. Context propagation

```
Task done  → matters to other tasks this phase? → phase file's Context
Phase done → matters beyond this phase? → promote to context/
```

A task never writes to `context/` directly, even a project-wide-looking
fact — it routes through the phase file's Context first; promotion to
`context/` happens once, at phase completion.

**Propagate:** architecture facts, invariants, responsibilities,
dependencies, constraints, domain knowledge.
**Never:** task history, temporary details, reasoning, progress
reports, anything recorded elsewhere.

A fact belongs in the phase/task file, or gets promoted to `context/`
(no lateral files, §4). An ADR's relevance follows the same cadence —
writing it doesn't wait.

---

## 10. Operation contracts

No agent determines its own authority — it always comes from
`../info.md`. Each skill states its own Can/Must/Cannot contract right
after its frontmatter, in its own SKILL.md — read there, not here.

---

## 11. Status: the permanent record

Every status value lives in exactly one place — never `info.md`, which
holds Policy only (§2, §10): `phases.md`'s Status column (phase-level),
a phase file's own task table (phase-linked task), or `tasks.md`'s
Status column (orphan task). "What's active" is answered by reading
the relevant table directly — no separate pointer to keep in sync.

```
not-planned → awaiting-plan-review → plan-approved → in-progress
  → validating → reviewing → complete
(blocked applies from any active state)
```

Full detail (which skill sets which value, ID-order reasoning):
[reference/status-and-info.md](reference/status-and-info.md).

**ID order ≠ execution order** — a replan can insert a task/phase that
belongs earlier but still gets the next-highest ID. Resolve
"first/next" via Depends-on + Status, never the lowest ID; ask if
ambiguous.

---

## 12. Commit discipline

Commit each draft immediately, before requesting review — the review
happens via `git diff`. Applies only to non-gitignored files: locality
is a per-layer, per-project choice (§3), and a gitignored layer simply
has nothing to commit — not a violation of this discipline. Message
format and type selection are your project's own convention (see your
`AGENTS.md`); each skill's own commit step says what to stage.
