# Agent Workflow Protocol

Source of truth for how work is organized, performed, and by whom.
Procedural how-to lives in `skills/`. Gate *authority* (who) lives in
[`../info.md`](../info.md), not here. Do not duplicate this file's
rules elsewhere — reference it.

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
   gate as human-owned and run `workflow-constitution` first, which
   creates it from `templates/info-template.md`.
2. **Open and read the matching skill file below before acting** — not
   "recall it exists," actually read it, every operation, even if you
   think you know it. Gate-skip and scope-overstep bugs traced back to
   this step being skipped, every time.
3. Never bypass a gate unless `info.md`'s policy explicitly authorizes it.

| Operation | Skill |
|---|---|
| Define/update mission, techstack, roadmap | `skills/workflow-constitution/` |
| Define a phase (`phases/p{NN}-{name}.md`) | `skills/workflow-phase/` |
| Define a task (`tasks/p{NN}-t{NN}-{name}.md`) | `skills/workflow-task/` |
| Write/modify/delete code for an already-planned task | `skills/workflow-implementation/` |
| Run task or phase validation | `skills/workflow-validation/` |
| Review implementation, plan, or completed work | `skills/workflow-review/` |
| Evaluate/propagate context after task or phase completion | `skills/workflow-context/` |

Can't find the right skill? Re-read this table — don't guess paths.

---

## 3. Directory structure

```
.ai/
├── workflow/                 ◄── submodule boundary — never written to
│   ├── workflow.md
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

**Every bare mention below** of `info.md`, `roadmap.md`, `phases/`,
`tasks/`, `context/`, `decisions/`, or `constitution/` refers to that
file/folder under `.ai/` as shown above — this document is a reference
for understanding the rules, not a literal sequence of write-tool
calls. When a **skill** instructs an actual write/read, it spells out
the full `.ai/`-prefixed path explicitly and states this same rule
again at the point of use — treat any bare mention there, or here, as
shorthand, never as a literal path to hand a write tool without
resolving it against the project root first. This distinction is not
academic: a bare or dot-relative path handed directly to a write tool
resolves against the agent's working directory, not against where any
instruction was read from — that mismatch has already caused a phase
file to be created outside `.ai/` in practice.

**Link rule:** every skill's cross-references to `workflow.md`, sibling
skills, and templates use `.ai/workflow/`-anchored paths, not
dot-relative ones — this is a deliberate change from an earlier,
purely-relative convention, made after a mirrored skill copy (see
`sync-skills.sh`) demonstrated that dot-relative links silently break
once a file is copied somewhere other than its designed location.
`.ai/workflow/` is the fixed, documented mount point every skill and
the `AGENTS.md` snippet assumes — not arbitrary. Per-project artifact
references follow the same rule: always `.ai/`-prefixed, never bare or
dot-relative, so a write/read target never depends on resolving
"relative to what."

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

---

## 5. Lifecycle & gates

```
Constitution → Constitution Review → Phase → Phase Plan Review
  → Tasks → Task Plan Review → Implement → Validate → Review
  → Context Evaluation → Task Complete → (repeat) → Phase Validation
  → Phase Completion Review → Reconcile Phase/Project Context
  → Phase Complete
```

Diagram labels favor readability over `info.md`'s exact YAML keys:

| Diagram label | Gate key | Distinct from |
|---|---|---|
| Constitution Review | `constitution-review` | — |
| Phase Plan Review | `phase-review` | Phase Completion Review (below) |
| Task Plan Review | `task-review` | unqualified Review (below) |
| (unqualified) Review | `task-completion-review` | `task-review` above |
| Phase Completion Review | `phase-completion-review` | `phase-review` above |

Full gate list: `constitution-review` · `phase-review` · `task-review`
· `task-validation` · `phase-validation` · `task-completion-review` ·
`phase-completion-review` · `context-update`.

**Gates block *advancing past* a draft, never *producing* one.**
Drafting never needs prior approval; only passing review does. Unsure
if you're "allowed" to draft? Yes — check the skill.

**Each gate unlocks only the next operation, nothing further.**
`phase-review` → task planning, not implementation. `task-review` →
implementation of *that* task only. Completion-review gates unlock
marking complete, nothing retroactive.

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

## 8. Validation vs. Review

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
`roadmap.md`'s Status at transitions + refresh `info.md`'s Active
phase pointer (§11 — pointer only, never a status word). Cannot:
implement code; **assign task IDs or populate the task table beyond
stub titles** — the Plan section isn't a task list.

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
(§11 — no status word there). Must: read `info.md` fresh before
trusting a gate's authority — never a cached read. Should not: edit
implementation to force a pass.

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

| Value | Set by |
|---|---|
| `not-planned` | `workflow-constitution` (every phase, initially); `workflow-task` (every undrafted plan step, on first invocation per phase) |
| `awaiting-plan-review` | `workflow-phase`/`workflow-task`, end of drafting |
| `plan-approved` | Whichever skill's ending receives approval — see §5's unlocking-≠-starting rule |
| `in-progress` | `workflow-task` (phase, task planning begins) / `workflow-implementation` (task, implementation begins) |
| `validating` | `workflow-validation` |
| `reviewing` | `workflow-review` — a different check than plan-review, see below |
| `complete` | `workflow-context`, only after its completion-review is approved |
| `blocked` | any agent, from any active state |

`workflow-task`'s first invocation per phase stubs every remaining
plan step at `not-planned` at once (cheap — titles only), then fully
drafts whatever's actually in scope.

Plan-review (`awaiting-plan-review`/`plan-approved`) checks a *plan*
before work begins; `reviewing` checks the *result* after (§8). Same
word "review," different check, different point in the lifecycle —
don't conflate them.

**Task ID order ≠ execution order.** A replan can insert a task that
logically belongs earlier but still gets the next-highest ID. Resolve
"first/next task" against the phase file's Depends-on and Status
columns — no unmet dependencies, Status `awaiting-plan-review`/
`plan-approved` — not the lowest ID. Ask rather than guess if still
ambiguous.

---

## 12. Multi-agent / multi-human

Independent tasks may run in parallel. Shared state lives in Git,
`info.md`, and the permanent-record tables — never a second Markdown
sync mechanism. Avoid concurrent edits to the same artifact. `info.md`
tracks only one active phase/task by design — true parallel work needs
each agent tracking its own item some other way until this format
supports more than one.

---

## 13. Commit discipline

Commit a draft the moment it's written, before requesting review — the
review happens via `git diff`. Messages tied to IDs: `P01: phase
drafted`, `P01-T01: task planned`, `P01-T01: implementation complete`,
`P01: phase complete`. Commit again whenever `info.md`, `roadmap.md`,
or a phase file's task table changes.
