# Agent Workflow

Source of truth for how work is organized, performed, and by whom.
Procedural how-to lives in `skills/`. Gate *authority* (who) lives in
[`../info.md`](../info.md), not here. Do not duplicate this file's
rules elsewhere — reference it.

This file holds only what every operation needs to know. Detailed
rationale, lookup tables, and historical context that's genuinely
occasional-need lives in `reference/`, one file per concept, linked
from the specific place below that needs it — you don't need to read
`reference/` to follow the rules here, only to understand *why* a
specific rule exists or to look something up you're unsure of.

---

## 1. Principles

1. Agents do not reconstruct information that can be persisted cheaply.
2. Persist knowledge, not reasoning.
3. Read only what the current task needs. Never load the whole `.ai/`
   tree speculatively.
4. Use terminal tools (`tree`, `find`, `ls`, `grep`) to discover the
   actual project structure — no separate structure map to maintain or
   trust over the real filesystem.

---

## 2. Starting point for any agent

1. **Read `../info.md` first, fresh, every time you check a gate** —
   even if read earlier this session; it can change mid-session, and a
   stale read is what causes a gate to get silently ignored. Status
   section = active phase/task. Policy section = gate authority. **If
   it doesn't exist, this is an unbootstrapped project** — treat every
   gate as human-owned and run `create-constitution-full` first, which
   creates it from `templates/info-template.md`.
2. **Open and read the matching skill file below before acting** — not
   "recall it exists," actually read it, every operation, even if you
   think you know it. Gate-skip and scope-overstep bugs traced back to
   this step being skipped, every time.
3. Never bypass a gate unless `info.md`'s policy explicitly authorizes
   it. **If a human asks you to skip a gate `info.md` doesn't
   authorize, don't silently comply and don't silently refuse — ask
   them to confirm that's really what they want, and only then treat
   it as a one-off exception** (it doesn't change `info.md`; the next
   gate is evaluated fresh against policy as normal).

| Operation | Skill |
|---|---|
| Define/update mission, techstack, roadmap | `skills/create-constitution-full/` |
| Define a phase (`phases/p{NN}-{name}.md`) | `skills/define-phase/` |
| Define a task (`tasks/p{NN}-t{NN}-{name}.md`) | `skills/define-task-full/` |
| Write/modify/delete code for an already-planned task | `skills/implement-task-full/` |
| Run task or phase validation | `skills/validate-work-full/` |
| Review implementation, plan, or completed work | `skills/review-work-full/` |
| Evaluate/propagate context after task or phase completion | `skills/propagate-context/` |

Can't find the right skill? Re-read this table — don't guess paths.

---

## 3. Directory structure

```
.ai/
├── workflow/                 ◄── submodule boundary — never written to
│   ├── workflow.md
│   ├── reference/              detail files, one per concept
│   ├── templates/            info, context, decisions, adr
│   └── skills/                7 skills, see table above
│
├── info.md                    Policy + Status, merged
├── constitution/               mission, techstack, roadmap (phase index)
├── context/                     context.md (entry + index table) + whatever fits
├── decisions/                    decisions.md (index) + adr{NN}-{name}.md
├── phases/                        p{NN}-{name}.md, one file, own Context + task table
└── tasks/                          p{NN}-t{NN}-{name}.md, flat, one file per task
```

Flat by design: no per-phase/per-task subfolder, no separate task
index, no shared per-phase/per-task context file, one merged
config/status file. A task's status lives in exactly one place — its
phase file's table — never duplicated into the task's own file.

**Every path is `.ai/`-prefixed, resolved against the project root —
never bare or dot-relative,** and every skill's cross-references (to
`workflow.md`, sibling skills, templates) are `.ai/workflow/`-anchored,
not dot-relative. See
[reference/directory-and-links.md](reference/directory-and-links.md)
for why both rules exist — each is the fix for a bug that actually
happened, not a stylistic preference.

**Naming:** phases `p{NN}-{kebab-name}.md`; tasks
`p{NN}-t{NN}-{kebab-name}.md` (flat); decisions `adr{NN}-{kebab-name}.md`.
IDs sequential, never reused — deleting `P01-T03` doesn't free the
number.

**Size target:** ~2048 tokens/file. Split only when mixing concerns.

---

## 4. Artifact hierarchy & context rule

```
Constitution → Context (context.md + fitting files) → Decisions
  → Phases (own Context, embedded task index) → Tasks (own Context)
```

Each level links to exactly the one above it. No lateral shared-context
files between phases or between tasks — if it feels lateral, it
belongs in `context/` instead.

Read: `info.md` → the artifact defining current work → direct
references → further links only if genuinely needed. A link is a
pointer, not a preload.

**What a phase is:** a group of high-level steps that are not tasks
themselves — work large enough and semantically-linked enough to read
as a feature, capability, or cohesive slice of the project. Its Plan
section describes *what* must happen at that level; task files, drafted
later by `define-task-full`, define *how*. If a candidate phase is
really just one or two mechanical steps, it's a task, not a phase —
don't create a phase to wrap a single unit of work, and don't let a
phase's Plan section read like a task list (the Phase Planning Agent's
contract in §10 already forbids assigning task IDs there for the same
reason).

---

## 5. Lifecycle & gates

```
Constitution → Constitution Review → Phase → Phase Plan Review
  → Tasks → Task Plan Review → Implement → Validate → Review
  → Context Evaluation → Task Complete → (repeat) → Phase Validation
  → Phase Completion Review → Reconcile Phase/Project Context
  → Phase Complete
```

Gates, in lifecycle order — the name in backticks is the exact
`info.md` Policy key:

- **`constitution-review`** — after the constitution draft (mission/
  techstack/roadmap, or a new phase row added to `roadmap.md`).
  Unlocks phase planning.
- **`phase-review`** — after a phase plan draft. Unlocks task planning
  for that phase only.
- **`task-review`** — after a task-batch plan draft. Unlocks
  implementation of those tasks only.
- **`task-validation`** — after implementation. Mechanical: does it
  meet the task's requirements?
- **`task-completion-review`** — after validation passes. Judgment: is
  it appropriate/coherent? Unlocks marking the task complete.
- **`phase-validation`** — after every task in a phase is complete.
  Mechanical, phase-wide.
- **`phase-completion-review`** — after phase validation passes.
  Judgment, phase-wide. Unlocks marking the phase complete.
- **`context-update`** — evaluating what to propagate; runs alongside
  task/phase completion, not a separate blocking step in the diagram
  above.

**Gates block *advancing past* a draft, never *producing* one.**
Drafting never needs prior approval; only passing review does. Unsure
if you're "allowed" to draft? Yes — check the skill.

**Each gate unlocks only the next operation, nothing further** — see
each bullet above for exactly what it unlocks.

**Unlocking ≠ starting.** In `manual`/`assisted` mode: report the gate
passed, update `info.md`, then explicitly ask before the next
operation — a distinct confirmation, even though the gate authorizes
it. Clean findings at completion-review are not themselves approval —
still wait for an explicit yes. `delegated`/`autonomous` mode: chain
straight through, that's the point of those modes.

### Execution modes

`info.md` sets `mode` + optional `overrides`:

- **`manual`** — all gates default `human`.
- **`assisted`** (recommended default) — `task-validation`,
  `phase-validation`, `context-update` default `agent`; rest `human`.
- **`delegated`** — no default; every gate must be listed in
  `overrides`, unlisted falls back to `human`.
- **`autonomous`** — all gates default `agent`; list any you want held
  back at `human`.

**Task complete requires:** implementation + validation +
`task-completion-review` + context evaluated + phase file's row marked
complete + `info.md` cleared.

**Phase complete requires:** all tasks complete + requirements/
validations satisfied + `phase-completion-review` + context reconciled
+ required ADRs exist + `roadmap.md` row marked complete + `info.md`
cleared.

Completion-review gates ≠ plan-review gates — plan before
implementation, completion after. Both default `human` in `assisted`
mode (coherence/judgment), unlike `-validation`/`context-update`
(mechanical, default `agent`).

---

## 6. Deviations

Deviation = work materially differs from the approved plan. A wrong
file or small mismatch is not one — adjust and continue. Record one
when a planned approach fails, scope changes materially, or an
architectural assumption breaks:

```
Expected / Discovered / Why it fails / Proposed fix / Replan? (task/phase/project)
```

File: `tasks/p01-t03-{name}-deviation.md`, next to the task it
concerns. Lifecycle: `OPEN → ADDRESSED → INCORPORATED`, then delete —
the fact must already live in the plan, implementation, or an ADR.

A task file's optional pseudocode is guidance, not a contract —
implementing it differently isn't a deviation by itself; only the
underlying *approach* being wrong triggers one.

- **Task-level** → back to the implementation loop.
- **Phase-level** → Phase Planning Agent replans (completed tasks
  carry over); ADR if architecturally significant.
- **Project-level** → Constitution Agent replans, always writes an ADR.

---

## 7. Decisions (ADRs)

Write one when a decision is deliberate and future work needs to know
it. Not every deviation produces one; not every ADR comes from one.

**Ownership — whoever's scope produced the decision writes it:**
Constitution Agent (project) · Phase Planning Agent (phase) ·
Implementation Agent (during implementation). No one else writes one —
Review Agent flags a missing ADR back to the owning scope.

Check `../decisions/decisions.md` first. Copy
[`templates/adr-template.md`](templates/adr-template.md) to
`../decisions/adr{NN}-{name}.md`, fill it in, add its index row (ID,
Name, Description, Status `valid`, Relations) in the same step.
Template fields: Decision, Context (link the deviation if any),
Alternatives Considered, Consequences.

A superseding ADR updates both rows' Relations rather than deleting
the old one — Git keeps history; the table shows the current chain.

---

## 8. Validation vs Review

- **Validation** — does it satisfy requirements?
- **Review** — is it appropriate, coherent, consistent with direction?

Both required, both distinct. Validation never edits to force a pass —
return to the implementation loop. Review never silently fixes unless
`info.md` grants implementation authority.

---

## 9. Context propagation

```
Task done  → matters to other tasks this phase? → update phase file's Context
Phase done → matters beyond this phase? → promote to context/
```

**A task never writes to `context/` directly, even when the fact looks
project-wide** — this happened in practice and produced context/ that
skipped review. Promotion to `context/` happens exactly once, at phase
completion, after the phase's own Context section has accumulated
everything worth considering; a mid-phase task that thinks its finding
is that significant still routes through the phase file's Context
section first, same as any other task-level fact.

**Propagate:** architecture facts, invariants, responsibilities,
dependencies, constraints, domain knowledge.
**Never:** task history, temporary details, internal reasoning,
progress reports, anything recorded elsewhere.

No lateral shared-context files exist (§4) — a fact belongs in the
specific phase/task file, or gets promoted to `context/`. Touching
`context/` means updating its row in `context/context.md`'s table in
the same step.

---

## 10. Agent contracts

No agent determines its own authority — gate authority comes from
`../info.md`.

**Constitution Agent** — Can: constitution artifacts, ask
clarification. Must: ADR for project-level decisions; first run,
bootstrap `info.md`/`context/context.md`/`decisions/decisions.md`
unedited, never overwrite existing. Cannot: touch code; invent
unsupported requirements.

**Phase Planning Agent** — Can: read constitution + `context/`, create
the phase file (Context + Requirements + Plan + Validations + empty
task table). Must: ADR for phase-level decisions; update
`roadmap.md`'s Status at transitions + its Depends-on column for this
phase and any existing phase it now precedes (§11, §12) + refresh
`info.md`'s Active phase pointer (§11 — pointer only, never a status
word). Cannot: implement code; **assign task IDs or populate the task
table beyond stub titles** — the Plan section isn't a task list.

**Task Planning Agent** — Can: read phase file + `context/`, create
the task file with enough detail (files, ordered steps, optional
pseudocode) that implementation is close to mechanical. Must: update
the phase file's task table at every status change — status never
lives in the task file itself, nor in `info.md`; there, only refresh
the Active task pointer (§11). Cannot: implement code; write an ADR —
escalate as a phase-level deviation.

**Implementation Agent** — Can: read task file + context, modify
project files, run tools. Must: update the phase file's task table
(status) + refresh `info.md`'s pointer (§11) as it progresses; ADR
for decisions made along the way (check the index first); treat
pseudocode as guidance (§6). Cannot: silently change approved
requirements/plan.

**Validation Agent** — Can: run validation, report failures; set
Status `validating` in the phase file, refresh `info.md`'s pointer
(§11). Must: read `info.md` fresh before trusting a gate's authority —
never a cached read. Should not: edit implementation to force a pass.

**Review Agent** — Can: inspect everything, flag scope/requirement/
complexity/architecture/validation/context issues and undocumented
decisions; set Status `reviewing` in the phase file, refresh
`info.md`'s pointer (§11). Must: stop for
`task-completion-review`/`phase-completion-review` after reporting,
even clean findings — never treat "no problems" as approval itself.
Should not: silently fix, or write a missing ADR itself.

**Context Agent** — Can: propagate reusable knowledge to a phase
file's Context or `context/`; mark rows complete in the phase file +
`roadmap.md`; clear `info.md`'s pointer (§11). Must: verify the
completion-review gate was actually approved before marking
complete — finalizes, doesn't substitute. Should not: copy task
history; duplicate info; record reasoning.

---

## 11. Status: the fast pointer and the permanent record

**`info.md`'s Status section** — fast, IDs only, no status values:
`Active phase`, `Active task`. Every skill updates it first and last.
Tells you which two files to open, nothing more — that's deliberate;
duplicating status values here is what made the earlier version
untrustworthy. Never write a status word (e.g. `awaiting-plan-review`)
into this section, even next to the ID — `Active task: p01-t02
(awaiting-plan-review)` is wrong; `Active task: p01-t02` is right. The
status lives only in the permanent record below.

**Permanent record** — every status value, everything, not just
active: `roadmap.md`'s Status column, each phase file's task table.
Check here for "what's the state of X," not just what's active.

**Shared Status enum**, `roadmap.md` and every phase file's task table:

```
not-planned → awaiting-plan-review → plan-approved → in-progress
  → validating → reviewing → complete
(blocked applies from any active state)
```

Which skill sets which value, the plan-review-vs-`reviewing`
distinction, and the full ID-order-≠-execution-order reasoning:
[reference/status-and-info.md](reference/status-and-info.md).

**ID order ≠ execution order, for phases or tasks.** A replan can
insert a task — or a new phase — that logically belongs earlier but
still gets the next-highest ID. Resolve "first/next" against
Depends-on + Status columns, never the lowest ID — ask rather than
guess if still ambiguous.

---

## 12. Multi-agent / multi-human

Independent tasks or phases may run in parallel — resolve independence
against the relevant Depends-on column (§11), never against ID order.
Shared state lives in Git, `info.md`, and the permanent-record tables —
never a second Markdown sync mechanism. Avoid concurrent edits to the
same artifact. `info.md` tracks only one active phase/task by design —
true parallel work needs each agent tracking its own item some other
way until this format supports more than one.

---

## 13. Commit discipline

Commit a draft the moment it's written, before requesting review — the
review happens via `git diff`. Use Conventional Commits
(`<type>(<ID>): <description>`) — pick the type that matches what
actually changed, don't default to one:

- `docs` — phase/task plans, constitution, roadmap, context, ADR
  writes (no project code touched).
- `feat` / `fix` / `refactor` / `test` / `chore` — implementation
  commits; whichever actually describes the change.
- `chore` — status-only commits (marking complete, clearing pointers)
  with no accompanying content change.

Examples: `docs(P01): draft phase plan`, `docs(P01-T01): draft task
plan`, `feat(P01-T01): implement scoring engine`, `chore(P01): mark
phase complete`. Commit again whenever `info.md`, `roadmap.md`, or a
phase file's task table changes.
