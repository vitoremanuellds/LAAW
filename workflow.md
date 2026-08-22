# Agent Workflow Protocol

Source of truth for how work is organized, performed, and by whom.
Self-contained — everything an agent needs to understand the protocol
lives here. Procedural how-to lives in `skills/`, not here. Gate
*authority* (who) lives in [`../info.md`](../info.md), not here.

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

1. **Read `../info.md` first — one file, always.** Its Status section
   tells you the active phase and task; its Policy section tells you
   who's authorized for the gate you're about to hit. Read it fresh
   every time you're about to check a gate, even if you already read
   it earlier this session — it can change mid-session, and relying on
   a cached read of it is exactly what causes a gate to get silently
   ignored. **If it doesn't exist yet, this is a brand-new project
   that hasn't been bootstrapped.** Treat every gate as human-owned
   (the same as the default for any unlisted gate) and go run
   `workflow-constitution` first if you aren't already — its first-run
   procedure is what creates `info.md` from
   `templates/info-template.md`. Don't invent gate authority in its
   absence.
2. **Open and actually read the matching skill file below before doing
   anything else for that operation.** Not "recall that it exists" —
   use your file-read tool on it now, every time you start a new
   operation type in a session, even if you believe you already know
   what it says. The rules that stop you from skipping a gate, from
   overstepping into another agent's scope, and from mismarking status
   live in the skill file's procedure, not in your general
   understanding of this table. Skipping this step is the single most
   common failure mode observed in practice — constitution review
   getting skipped, phases getting created without a plan, status
   fields left wrong — and every instance traced back to the skill
   never actually being opened.
3. Never bypass a gate unless `info.md`'s policy explicitly
   authorizes you to.

| Operation | Skill |
|---|---|
| Define/update mission, techstack, roadmap | `skills/workflow-constitution/` |
| Define a phase (`phases/p{NN}-{name}.md`) | `skills/workflow-phase/` |
| Define a task (`tasks/p{NN}-t{NN}-{name}.md`) | `skills/workflow-task/` |
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
├── workflow/                 ◄── git submodule boundary — never written to
│   ├── README.md               Install instructions, this repo's own docs
│   ├── workflow.md              This file
│   ├── templates/
│   │   ├── info-template.md          Copied to ../../info.md on first run
│   │   ├── context-template.md        Copied to ../../context/context.md on first run
│   │   ├── decisions-template.md       Copied to ../../decisions/decisions.md on first run
│   │   └── adr-template.md              ADR format (copied into ../../decisions/ per decision)
│   └── skills/
│       ├── workflow-constitution/SKILL.md
│       ├── workflow-phase/SKILL.md
│       ├── workflow-task/SKILL.md
│       ├── workflow-implementation/SKILL.md
│       ├── workflow-validation/SKILL.md
│       ├── workflow-review/SKILL.md
│       └── workflow-context/SKILL.md
│
├── info.md                    Policy + Status, merged — your project's own file
│
├── constitution/
│   ├── mission.md
│   ├── techstack.md
│   └── roadmap.md              Ordered phases + Status column — the phase index (permanent record)
│
├── context/                     About the codebase — architecture, conventions, terminology
│   ├── context.md                 Entry point + Status/Relations table of context files
│   ├── auth-module.md              Example — any name/structure fits, see context.md
│   └── score-engine.md
│
├── decisions/
│   ├── decisions.md              Topic lookup, one row per ADR
│   └── adr01-decision-name.md
│
├── phases/
│   └── p01-phase-name.md          Context + Requirements + Plan + Validations + embedded task table, one file per phase
│
└── tasks/                       Flat — every task from every phase, no per-phase subfolders
    ├── p01-t01-task-name.md        Context + Implementation, one file per task
    └── p01-t02-task-name.md
```

Everything under `workflow/` ships from a separate repo (submodule) and
is never written to by any agent — see that repo's own README for why.
Everything else is a regular file in your project's own git history.

**Why this is flat:** no per-phase subfolder, no per-task subfolder,
no separate task index file, no separate per-phase or per-task shared
context file, one merged config/status file instead of two. A task's
*status* lives in exactly one place — its phase file's embedded table —
never duplicated into the task's own file.

**Link rule:** every link is relative to the file containing it, never
to `.ai/` root or repo root. This is what makes the whole tree portable
regardless of what folder it's nested under.

**Naming:** phase files `p{NN}-{kebab-name}.md`; task files
`p{NN}-t{NN}-{kebab-name}.md` (flat under `tasks/`, phase ID is just
part of the filename, not a directory); decisions
`adr{NN}-{kebab-name}.md`. IDs (`P01`, `P01-T01`, `ADR01`, ...) are
sequential and never reused — deleting `P01-T03` doesn't free the
number; the next task is still `P01-T04`.

**Artifact size target:** ~2048 tokens per file. Split further only if
a file is mixing genuinely independent concerns.

---

## 4. Artifact hierarchy & context rule

```
Constitution (mission, techstack, roadmap)
  → Context (context.md + whatever files fit this project)
  → Decisions (ADRs)
  → Phases (one file, own Context section, embedded task index)
      → Tasks (one file, own Context section)
```

Each level links to exactly the one level above it for context — a
task's Context section points at its phase file; a phase file's
Context section points at `context/`. No lateral shared-context files
between phases or between tasks; if something feels like it belongs at
that lateral tier, it usually belongs in `context/` instead, one level
up.

An agent reads: `info.md` first → the artifact defining its current
work → its direct references → further links only if the task can't
be completed without them. Never explores unrelated project areas
"just in case." A link is a pointer, not a preload.

---

## 5. Lifecycle & gates

```
Constitution → Constitution Review → Phase (p{NN}-{name}.md)
  → Phase Plan Review → Tasks (p{NN}-t{NN}-{name}.md) → Task Plan Review
  → Implement → Validate → Review → Context Evaluation → Task Complete
  → (repeat) → Phase Validation → Phase Completion Review
  → Reconcile Phase Context → Reconcile Project Context → Phase Complete
```

Diagram labels favor readability over matching `info.md`'s YAML gate
keys exactly — don't assume identical spelling. Mapping:

| Diagram label | Gate key | Notes |
|---|---|---|
| Constitution Review | `constitution-review` | |
| Phase Plan Review | `phase-review` | Approves the phase file's Requirements/Plan/Validations — not the same as Phase Completion Review below |
| Task Plan Review | `task-review` | Approves a task file — not the same as the unqualified Review step below |
| (unqualified) Review | `task-completion-review` | Post-implementation coherence check, one per task — distinct from `task-review` above despite both being "reviews" |
| Phase Completion Review | `phase-completion-review` | Post-implementation coherence check, one per phase — distinct from `phase-review` above |

Full gate list: `constitution-review` · `phase-review` · `task-review`
· `task-validation` · `phase-validation` · `task-completion-review` ·
`phase-completion-review` · `context-update`.

**A gate blocks *advancing past* a completed draft — never blocks
*producing* the draft.** Drafting a phase, a task, or an implementation
never needs prior approval; only moving past its review checkpoint
does. If unsure whether you're "allowed" to start drafting, the answer
is yes — check the relevant skill before making any judgment about
what a gate permits.

**Each gate unlocks only the operation immediately following it —
never anything further down the chain.** Passing `phase-review`
unlocks task *planning*, not implementation. Passing `task-review`
unlocks *implementation* for that task, and only that task. Passing
`task-completion-review`/`phase-completion-review` unlocks marking the
task/phase complete — it does not retroactively bless anything about
the plan or the implementation beyond what was actually checked.

**Unlocking the next operation is not the same as starting it.** In
`manual` and `assisted` mode, report that the gate passed, update
`info.md`'s Status section, and explicitly ask before beginning the
next operation — wait for a distinct confirmation, even though the
gate technically authorizes it. Don't fold "your plan is approved" and
"I'll now implement it" into the same uninterrupted turn. This applies
at completion-review too: finding no problems is not itself approval —
report clean findings and still wait for an explicit yes before
marking anything complete. In `delegated`/`autonomous` mode this
separation is unnecessary — chaining straight into the next operation
once a gate passes is the point of those modes.

### Execution modes and their defaults

`info.md`'s Policy section sets `mode` and, optionally, `overrides` for
individual gates. Each mode has a real default so most projects need
few or no overrides:

- **`manual`** — every gate defaults to `human`. No overrides needed
  for the common case.
- **`assisted`** — `task-validation`, `phase-validation`, and
  `context-update` default to `agent`; every other gate defaults to
  `human`. This is the recommended starting mode.
- **`delegated`** — **no default exists.** Every gate must be listed
  explicitly in `overrides`; an unlisted gate falls back to `human`,
  same as the global rule for any gate policy doesn't mention. This
  mode's `overrides` list *is* the actual policy, not an exception to
  one.
- **`autonomous`** — every gate defaults to `agent`. Still list any
  gate you want to deliberately hold back at `human` (e.g. keeping
  `constitution-review` human even in an otherwise autonomous setup).

**Task completion requires:** implementation done; validation passed
(or documented exception); `task-completion-review` passed; context
evaluated; the task's row in its phase file's task table marked
complete; `info.md`'s Status section cleared of it as the active task.

**Phase completion requires:** all tasks complete; phase requirements
and validations satisfied; `phase-completion-review` passed; phase and
project context reconciled; required ADRs exist; the phase's row in
`roadmap.md` marked complete; `info.md`'s Status section cleared of it
as the active phase.

Neither completion-review gate is the same check as `task-review`/
`phase-review` — those approve a *plan*, before implementation exists;
these approve the *result*, after it's done. Both default to `human`
authority in `assisted` mode, matching the other `-review` gates
rather than the agent-default `-validation`/`context-update` gates —
coherence/judgment calls default to human, mechanical correctness
checks default to agent.

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

File: `tasks/p01-t03-{name}-deviation.md`, next to the task file it
concerns (flat, same as everything under `tasks/`). Lifecycle:
`OPEN → ADDRESSED → INCORPORATED`, then delete — the fact must already
live in the plan, implementation, or an ADR by then. Git keeps the
history; don't let deviation files accumulate as a log.

**A task file's optional pseudocode (see `workflow-task`) is guidance,
not a contract.** Implementing something differently than the
pseudocode sketched is not, by itself, a deviation — only escalate if
the *approach* itself turns out wrong, same threshold as always. Don't
let a detailed task file turn "I did it slightly differently" into
deviation-spam.

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

Check `../decisions/decisions.md` before writing a new one. Whoever
writes the ADR copies
[`templates/adr-template.md`](templates/adr-template.md) into
`../decisions/adr{NN}-{name}.md` and fills it in, adding its index row
(ID, Name, Description, Status `valid`, Relations) in the same step.
Template fields: **Decision**, **Context** (link the deviation if
any), **Alternatives Considered**, **Consequences**.

When a later ADR supersedes an earlier one, update both rows' Relations
column rather than deleting the old row — Git keeps history either
way, but the table should show the current chain without opening every
file.

---

## 8. Validation vs. Review

- **Validation** — does the implementation satisfy the requirements?
- **Review** — is the work appropriate, coherent, and consistent with
  the project's direction?

Both required, both distinct. Validation never edits implementation to
force a pass — failures return to the implementation loop. Review
never silently fixes issues unless `info.md`'s policy grants
implementation authority.

---

## 9. Context propagation

```
Task done   → does this matter to other tasks in this phase? → update the phase file's own Context section if yes
Phase done  → does this matter beyond this phase? → promote to context/ if yes
```

**Propagate:** architecture facts, invariants, module responsibilities,
dependencies, constraints, domain knowledge.
**Never propagate:** task history, temporary details, internal
reasoning, progress reports, anything already recorded elsewhere.

No lateral shared-context files exist between phases or between tasks
(see §4) — a fact either belongs in the specific phase/task file it
concerns, or it's general enough to promote straight to `context/`.
When you add or update a file under `context/`, update its row in
`context/context.md`'s table (Description, Status, Relations) in the
same step — same discipline as the decisions index.

---

## 10. Agent contracts

No agent determines its own authority — it operates strictly within
its contract below. Gate authority comes from `../info.md`.

**Constitution Agent** — Can: read project info, create/modify
constitution artifacts, ask for clarification. Must: write an ADR for
project-level decisions; on first run, bootstrap `../info.md`,
`../context/context.md`, and `../decisions/decisions.md` from their
templates, unedited, never overwriting any that already exist. Cannot:
touch project code; invent unsupported requirements.

**Phase Planning Agent** — Can: read constitution + relevant
`context/`, create `phases/p{NN}-{name}.md` (own Context section +
Requirements + Plan + Validations + an initially-empty task table).
Must: write an ADR for phase-level architectural decisions; update
`info.md`'s Status section and the phase's Status in `roadmap.md` at
each transition (see §11). Cannot: implement code; **assign task IDs
or populate the task table with anything beyond stub titles** — the
Plan section looks like a task list but isn't one; task breakdown is a
separate, later operation.

**Task Planning Agent** — Can: read the phase file + relevant
`context/` files, create `tasks/p{NN}-t{NN}-{name}.md` with enough
detail (files to touch, ordered steps, optional pseudocode) that
implementation can be close to mechanical. Must: update the owning
phase file's embedded task table whenever a task is added or changes
status (see §11) — this is the only place task status lives, task
files themselves don't track it; update `info.md`'s Status section.
Cannot: implement code; write an ADR — escalate an architectural
discovery as a phase-level deviation instead.

**Implementation Agent** — Can: read the task file + referenced
context, inspect/modify project files, execute tools. Must: update the
task's row in its phase file's task table (including Status, see §11)
as it moves through implementation; update `info.md`'s Status section;
write an ADR for decisions made during implementation (check the index
first); treat a task file's pseudocode as guidance, not a literal
script (see §6). Cannot: silently change approved requirements or the
phase plan.

**Validation Agent** — Can: inspect files, execute validation
commands, report failures; set the task's Status to `validating` in
its phase file's task table, and update `info.md`, while running.
Must: read `info.md`'s policy fresh before deciding whether a gate is
self-certifiable — never rely on a cached read from earlier in the
session. Should not: modify implementation to force a pass — return to
the implementation loop instead.

**Review Agent** — Can: inspect requirements/plan/implementation/
changes/tests/context/ADRs; flag scope violations, requirement
mismatches, unnecessary complexity, architectural inconsistencies,
missing validation, context inconsistencies, undocumented decisions;
set Status to `reviewing` in the relevant table and update `info.md`
while running. Must: stop for `task-completion-review`/
`phase-completion-review` after reporting findings, even clean ones —
never treat "no problems found" as approval in its own right. Should
not: silently fix problems or write a missing ADR itself — flag back
to the owning scope.

**Context Agent** — Can: inspect completed work, identify reusable
knowledge, update a phase file's own Context section or `context/`;
mark the task's row complete in its phase file's task table and the
phase's row complete in `roadmap.md` at their respective completions;
clear the completed item from `info.md`'s Status section. Must: verify
the relevant completion-review gate has actually been approved before
marking anything complete — this agent finalizes an approved review,
it doesn't substitute for one. Should not: copy task history into
context; duplicate information already represented elsewhere; record
internal reasoning.

---

## 11. Status: the fast pointer and the permanent record

Two tiers, not one — this is deliberate, not redundancy for its own
sake:

**`info.md`'s Status section — fast, always current, IDs only, no
status values.** Just `Active phase` and `Active task`. Every skill
updates it first (claim what you're about to do) and last (reflect the
outcome), before touching anything else. Reading it tells you which
two files to open next without scanning or listing anything — it
deliberately does not duplicate their actual status values, which is
what kept the earlier, fuller version of this file from staying
trustworthy.

**Permanent record — tracks every status value, for everything, not
just what's active.** `roadmap.md`'s Status column (every phase,
always) and each phase file's embedded task table (every task in that
phase, always). This is what you check for "what's the state of
everything" or "what's this specific phase/task's actual status" —
`info.md` only tells you *which one* is active, not what state it's in.

**One shared Status enum, used by `roadmap.md` and every phase file's
task table:**

```
not-planned → awaiting-plan-review → plan-approved → in-progress
  → validating → reviewing → complete
(blocked can apply from any of the active states)
```

| Value | Meaning | Set by |
|---|---|---|
| `not-planned` | Entry exists, no draft yet | `workflow-constitution`, for every phase, initially — and `workflow-task`, for every remaining plan step it hasn't been asked to draft yet, on its first invocation for a phase |
| `awaiting-plan-review` | A draft (phase file / task file) exists, committed, waiting on its plan-review gate | `workflow-phase` / `workflow-task`, at the end of drafting |
| `plan-approved` | The plan-review gate passed; work hasn't necessarily started yet | Whichever skill's ending receives the approval — see §5's two-step rule. This is the value that makes that rule concrete: don't leave Status stuck at `awaiting-plan-review` once approved, and don't jump straight to `in-progress` either. |
| `in-progress` | Real work is actively happening | `workflow-task` (phase-level, when task planning begins) / `workflow-implementation` (task-level, when implementation begins) |
| `validating` | Correctness check running | `workflow-validation`, task- or phase-level |
| `reviewing` | Coherence/quality check running — **this is a different check from plan-review above; see the note below** | `workflow-review`, task- or phase-level |
| `complete` | Done — only after `task-completion-review`/`phase-completion-review` is approved | `workflow-context`, task-level (task) or project-level (phase) |
| `blocked` | Stuck, needs attention | Any agent, from any active state |

On its first invocation for a given phase, `workflow-task` stubs a row
at `not-planned` in the phase file's task table for *every* remaining
plan step at once — cheap, since it's just a title, not a full draft —
then fully drafts only whatever was actually asked for that
invocation, moving those rows to `awaiting-plan-review`.

**Naming note — plan-review vs. review are not the same check.**
`awaiting-plan-review`/`plan-approved` are about a *plan document*
before work begins. `reviewing` is about the *implementation* after
it's done — code coherence, scope, architecture consistency (§8).
Don't conflate the two just because both involve a human or agent
"reviewing" something; they check entirely different things at
entirely different points in the lifecycle.

**Task ID order is not execution order.** IDs are assigned sequentially
as tasks are created (§3), but a replan can insert a task that
logically belongs earlier — e.g. a foundational setup step added after
`P01-T01`–`P01-T04` already exist still gets `P01-T05`. If a person
says "implement the first task" or "the next task," resolve it against
the phase file's task table — **Depends on** and **Status** columns —
the task with no unmet dependencies and Status `awaiting-plan-review`
or `plan-approved` that nothing else depends on ahead of it — not the
lowest ID number. If it's still ambiguous which task is meant, ask
rather than guess; picking the wrong task silently is worse than one
clarifying question.

---

## 12. Multi-agent / multi-human

Independent tasks may run in parallel across agents/humans. Shared
state lives in Git, `info.md`'s Status section, and the permanent-record
tables above — never invent a second synchronization mechanism in
Markdown. Avoid concurrent edits to the same task, files, or workflow
artifact. Note: the Status section only tracks a *single* active
phase/task by design — true parallel multi-agent work needs each agent
tracking its own item some other way (e.g. in its own commit messages)
until this format is extended to support more than one active item at
a time.

---

## 13. Commit discipline

Commit a draft the moment it's written, before requesting its review
gate — this lets the review happen via `git diff`. Message convention
tied to IDs: `P01: phase drafted`, `P01-T01: task planned`,
`P01-T01: implementation complete`, `P01: phase complete`. Commit again
whenever `info.md`, `roadmap.md`, or a phase file's task table changes
as part of a transition.
