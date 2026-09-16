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
| Route to correct operation | `route` |
| Bootstrap several layers at once | `bootstrap` |
| Constitution / context setup | `create-constitution` |
| Task planning | `define-task` |
| Implementation | `implement-task` |
| Validation | `validate-work` |
| Review | `review-work` |
| Context — fill items | `build-context` |
| Context — propagate/finalize | `propagate-context` |

---

## 3. Directory structure

```
.ai/workflow/       plain copy, managed by sync-workflow.py (P02), never written to — workflow.md, reference/, templates/, skills/, tools/
.ai/info.md         Policy only — gate authority; always present, not an optional layer
.ai/context/        THE one context layer (merged): context.md + c-{ID}-{name}.md + optional index-*.md — effectively mandatory (one small file suffices)
.ai/tasks/          Mandatory: tasks.md + t{ID}-{name}.md (leaf) + t{ID}-{name}/ (has-subtasks folder, per the recursive rule below)
.ai/workbench/      freeform scratch — planning notes, Q&A, prompt drafts; disposable, not part of the permanent record — optional
```

Presence is inferred from existence — no directory means that layer is
off for this project; `tasks/` is mandatory; `context/` is effectively
mandatory (one small file suffices); `workbench/` is optional. No
five-axis matrix.
How a layer comes into existence on first use: see
[reference/scaffold-on-first-use.md](reference/scaffold-on-first-use.md)
(or run `bootstrap` to set up several at once).

`.ai/tasks/` holds two shapes, distinguished by path: a **leaf task**
(`t{ID}-{name}.md`) and a **task with subtasks** (`t{ID}-{name}/` — a
folder containing the parent file `t{ID}-{name}.md` and subtask files
below it). The same rule applies at every nesting level: if a task has
subtasks, it is a folder; if it does not, it is a leaf file. IDs are
sequential and never reused.

`tasks.md` and `workbench/` are exempt from the id system:
`tasks.md` is the root index (it exists before any task is minted),
and `workbench/` is scratch, not part of the permanent record (why:
[reference/directory-and-links.md](reference/directory-and-links.md)).

Flat by design; paths always `.ai/`-prefixed off the project root,
never bare/dot-relative (why:
[reference/directory-and-links.md](reference/directory-and-links.md)).

---

## 4. Artifact hierarchy & context rule

```
Context → Tasks (own Context)
```

One optional layer (`context/`) feeding into the mandatory `tasks/`
layer. All context is in `context/`. A task can have subtasks (itself a folder) or be a leaf.

**Context** = mission + techstack core + architecture facts, invariants,
responsibilities, dependencies, constraints, domain knowledge.
**Task** = one mechanical unit of work (*how*), drafted by
`define-task`. A task lives in `tasks/` as a leaf file or a folder
with subtasks.

---

## 5. Lifecycle & gates

```
Tasks → Task Plan Review → Implement
  → Task Completion Review (validate, then review)
  → Context Evaluation → Task Complete → (repeat)
```

**Gates for missing layers are skipped.** The lifecycle above shows
the full set — a project never walks through every gate; it only
encounters gates for layers that exist. If `context/` doesn't
exist, `context-evaluation` doesn't run.

| Gate | Runs after | Unlocks |
|---|---|---|
| `task-review` | task-batch draft | implementation |
| `task-completion-review` | implementation (mech., then judgment) | task complete |

Gates block *advancing past* a draft, never *producing* one.
**Unlocking ≠ starting** — `manual`/`assisted` stops and asks before
the next step; `delegated`/`autonomous` chains through.

**Modes** (`info.md`: `mode` + `overrides`):

| Mode | Plan-review | Compl.: mech. | Compl.: judgment |
|---|---|---|---|
| `manual` | human | human | human |
| `assisted` (default) | human | agent | human |
| `autonomous` | agent | agent | agent |

**Task complete:** implementation + `task-completion-review` (both
checks) + context evaluated.

Starting without every task already planned is normal:
[reference/starting-without-a-plan.md](reference/starting-without-a-plan.md).

---

## 6. Deviations

Deviation = work materially differs from the approved plan; a mismatch
against a plan detail marked flexible isn't one.
Recorded inline as a `## Deviations` subsection in the task file —
never separate; lifecycle `OPEN → ADDRESSED → INCORPORATED`, deleted
once the fact lives in the plan, implementation, or a context decision
row. Field format: `define-task`'s task-file conventions. Pseudocode is
guidance, not contract — deviating from it isn't itself a deviation;
only the underlying *approach* being wrong is.

- **Task-level** → back to the implementation loop.
- **Project-level** → replanned via `create-constitution`, always a
  context decision row.

New, working-as-planned scope on approved work isn't a deviation — it
still needs its own `task-review`.

---

## 7. Decisions

Decisions are **context rows** (`c-{ID}-{name}.md`), not standalone
files. Every decision has: id, name, relation, superseded-by columns
(same shape as the `context.md` index).

**Owner writes it, at the moment of the decision:**
- `create-constitution` — project-level.
- `implement-task` — during implementation.

No other operation writes one — review flags a missing one back to
the owning scope. A superseding decision updates both rows' Relations,
not a deletion — Git keeps history.

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
Task done  → matters beyond this task? → promote to context/
```

A task writes directly to `context/`.

**Propagate:** architecture facts, invariants, responsibilities,
dependencies, constraints, domain knowledge.
**Never:** task history, temporary details, reasoning, progress
reports, anything recorded elsewhere.

A fact belongs in the task file, or gets promoted to `context/`.
A context decision's relevance follows the same cadence — writing it
doesn't wait.

---

## 10. Operation contracts

No agent determines its own authority — it always comes from
`../info.md`. Each skill states its own Can/Must/Cannot contract right
after its frontmatter, in its own SKILL.md — read there, not here.

---

## 11. Status: the permanent record

Every status value lives in exactly one place — never `info.md`, which
holds Policy only (§2, §10): task rows in `tasks.md`, subtask rows in
the parent task file. "What's active" is answered by reading the
relevant table directly — no separate pointer to keep in sync.

``` 
not-started → planned → in-progress → done
(blocked from any active state)
```

`planned` = draft exists, `task-review` gate pending/passed.
`in-progress` = approved, implementation underway.
`done` = implementation complete + `task-completion-review` passed.

The two gates are transitions, not states.

Full detail (which skill sets which value, ID-order reasoning):
[reference/status-and-info.md](reference/status-and-info.md).

**ID order ≠ execution order** — a replan can insert a task that
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

**NEVER commit files that `.gitignore` excludes.** Before every commit,
run `git diff --cached` and verify no `.gitignore`d files appear in
the staged list. This is not optional — committing ignored files is a
violation of this discipline.

---

## 13. Teams (many developers)

**The file-overlap rule is the coordination unit:** work on the same
file set should not overlap across two `in-progress` tasks — the "touches
these files" spec line makes conflicts visible before they happen.

**Parallelism comes from subtasks:** a task can be approved as a whole
while subtasks are picked up by different people/agents.

**Git is the sync layer:** commit each draft/step; review happens via
diff. No locks beyond file overlap.

**Context (Before/After) matters more in a team:** it is what the next
person reads before touching the task — and where a deviation gets
recorded if it isn't a full replan.

---

## 14. What each principle buys

| Concern | Mechanism |
|---|---|
| Limited context window | small files + index `context.md` + links + "read only this file" rule; Context Before/After instead of session history |
| Hallucination | narrow task specs (files, done-when, out-of-scope); ask-don't-invent rule |
| Teams | file-overlap visibility, subtask parallelism, git diff review |
| Not source of truth | task files are guidance; acceptance is checked against the code/behavior, not the doc |
| Not PM tool | no roadmap, no progress metrics, no dependency graph — only what an agent needs to do its assigned task |
| Compressed info | everything small by design; anything long gets split + linked |
| Lazy reading | index files (`context.md`, `tasks.md`) hold only pointers + status |
