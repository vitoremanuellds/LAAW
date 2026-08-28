# Agent Workflow

Source of truth for how work is organized, performed, and by whom. Do not
duplicate this file's rules elsewhere — reference it. Detailed rationale,
lookup tables, and historical context that's genuinely occasional-need
lives in `reference/`, one file per concept, linked from the specific place
below that needs it.

---

## 1. Principles

1. Agents do not reconstruct information that can be persisted cheaply.
2. Persist knowledge, not reasoning.
3. Read only what the current task needs. Never load the whole `.ai/` tree
   speculatively.

---

## 2. Starting point for any agent

1. **Read `../info.md` first, fresh, every time you check a gate** —
   even if read earlier this session; it can change mid-session, and a
   stale read is what causes a gate to get silently ignored. Status
   section = active phase/task. Policy section = gate authority. **If
   it doesn't exist, this is an unbootstrapped project** — treat every
   gate as human-owned and run `create-constitution-full` first, which
   creates it from `templates/info-template.md`. [HUMAN] Maybe replace the word status for something like info.
2. **Open and read the matching skill file below before acting** — not
   "recall it exists," actually read it, every operation, even if you
   think you know it. See
   [reference/reread-skill-discipline.md](reference/reread-skill-discipline.md)
   for why.
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
| Populate `.ai/context/` for a project with little context yet | `skills/build-context-full/` |

Can't find the right skill? Re-read this table — don't guess paths.

---

## 3. Directory structure

```
.ai/
├── workflow/                 ◄── submodule boundary — never written to
│   ├── workflow.md
│   ├── reference/              detail files, one per concept
│   ├── templates/            info, context, decisions, adr
│   └── skills/                8 skills, see table above
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
for why both rules exist.

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
pointer, not a preload. Resolve context by following the task or phase
file's own links first — don't search the rest of the codebase for context
documents it doesn't already point to; if the context you need isn't
linked from where you're working, that's a gap in the task/phase file,
not a cue to go looking elsewhere.

**What a phase is:** a group of high-level steps that are not tasks
themselves — work large enough and semantically-linked enough to read
as a feature, capability, or cohesive slice of the project. Its Plan
section describes *what* must happen at that level; task files, drafted
later by `define-task-full`, define *how*. If a candidate phase is
really just one or two mechanical steps, it's a task, not a phase —
don't create a phase to wrap a single unit of work, and don't let a
phase's Plan section read like a task list (the phase-planning
contract in §10 already forbids assigning task IDs there for the same
reason).

**Quick reference:** `phase` — a feature/capability-sized slice of work with its own Context and Plan; `task` — one mechanical, close-to-implementable unit of work within a phase's Plan.

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

Gates, in lifecycle order — the name in backticks is the exact
`info.md` Policy key:

- **`constitution-review`** — after the constitution draft (mission/
  techstack/roadmap, or a new phase row added to `roadmap.md`).
  Unlocks phase planning.
- **`phase-review`** — after a phase plan draft. Unlocks task planning
  for that phase only.
- **`task-review`** — after a task-batch plan draft. Unlocks
  implementation of those tasks only.
- **`task-completion-review`** — after implementation, one gate running
  two checks in order: first mechanical (does it meet the task's
  requirements?), then judgment (is it appropriate/coherent?). Unlocks
  marking the task complete.
- **`phase-completion-review`** — after every task in a phase is
  complete, the same two-check sequence, phase-wide: mechanical first,
  then judgment. Unlocks marking the phase complete.
- **`context-update`** — evaluating what to propagate; runs alongside
  task/phase completion, not a separate blocking step in the diagram
  above.

[HUMAN] Inside [feedback](feedback.md) I have written something about the simplifying the gates, lifecycle and status.

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
- **`assisted`** (recommended default) — within `task-completion-review`/
  `phase-completion-review`, the mechanical check defaults `agent` and
  the judgment check defaults `human`; `context-update` also defaults
  `agent`; rest `human`.
- **`delegated`** — no default; every gate must be listed in
  `overrides`, unlisted falls back to `human`.
- **`autonomous`** — all gates default `agent`; list any you want held
  back at `human`.

**Task complete requires:** implementation + `task-completion-review`
(both checks) + context evaluated + phase file's row marked complete +
`info.md` cleared.

**Phase complete requires:** all tasks complete +
`phase-completion-review` (both checks) + context reconciled +
required ADRs exist + `roadmap.md` row marked complete + `info.md`
cleared.

Completion-review gates ≠ plan-review gates — plan before
implementation, completion after. Within `assisted` mode, a
completion-review gate's judgment check defaults `human`
(coherence/judgment), same as every plan-review gate; its internal
mechanical check defaults `agent`, same as `context-update`.

### Starting without a plan

Not every project has a fully-formed roadmap up front, and it doesn't
need one to start. Planning one phase at a time — instead of the whole
project up front — is a normal, intentional way to work, not a
workaround: `create-constitution-full` appends a single title-only row
to `roadmap.md` for whatever's next, with no pre-existing Plan detail
required; `define-phase` then drafts that phase's full
Context/In-scope/Out-of-scope/Requirements/Plan/Validations straight
from the live conversation, not from anything already written down.
This repo's own `roadmap.md` is the worked example — P02 through P05
each started exactly this way: name the next phase, plan it, implement
it, then plan the next one.

---

## 6. Deviations

Deviation = work materially differs from the approved plan. A mismatch
against a detail the task file explicitly marked flexible is not
one — adjust and continue; everything else that doesn't match the
approved plan is, even something that would once have read as a
small, adjustable mismatch — see `define-task-full`'s task-file
conventions for how flexible details get marked. Record one when a
planned approach fails, scope changes materially, or an architectural
assumption breaks:

```
Expected / Discovered / Why it fails / Proposed fix / Replan? (task/phase/project)
```

Recorded inline, as a `## Deviations` subsection appended to the task
file itself — never a separate file. Lifecycle: `OPEN → ADDRESSED →
INCORPORATED`, then delete the entry — the fact must already live in
the plan, implementation, or an ADR. See `define-task-full`'s
task-file conventions for the exact subsection format.

A task file's optional pseudocode is guidance, not a contract —
implementing it differently isn't a deviation by itself; only the
underlying *approach* being wrong triggers one.

- **Task-level** → back to the implementation loop.
- **Phase-level** → replanned via `define-phase` (completed tasks
  carry over); ADR if architecturally significant.
- **Project-level** → replanned via `create-constitution-full`, always
  writes an ADR.

[HUMAN] Maybe we can remove this part from here, as it is kind of a rule that should live inside the skill.

Adding new, working-as-planned scope to already-approved work (a new
phase, or new tasks in an existing phase's Plan) is not a deviation —
it still needs its own `phase-review`/`task-review` for the new
material, drafted per `define-phase`/`define-task-full`.

---

## 7. Decisions (ADRs)

Write one when a decision is deliberate and future work needs to know
it. Not every deviation produces one; not every ADR comes from one.

**Ownership — whoever's scope produced the decision writes it:** the
constitution operation (`create-constitution-full`, project-level) ·
the phase-planning operation (`define-phase`, phase-level) · the
implementation operation (`implement-task-full`, during
implementation). No other operation writes one — review flags a
missing ADR back to the owning scope. Write it and reference it from
the owning phase/task file the moment the decision is made — never deferred to phase completion; only propagating its relevance into
`context/` follows §9's timing.

A superseding ADR updates both rows' Relations rather than deleting
the old one — Git keeps history; the table shows the current chain.

---

## 8. Validation vs Review

The completion-review gate's two internal checks, in order: **validation**
— does it satisfy requirements (mechanical)? — then **review** — is it
appropriate, coherent, consistent with direction (judgment)? Both
required, both distinct. Validation never edits to force a pass — return
to the implementation loop. Review never silently fixes unless `info.md`
grants implementation authority.

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
specific phase/task file, or gets promoted to `context/`. See
`skills/propagate-context/SKILL.md` for the exact procedure. An ADR's relevance to `context/` propagates on this same phase-completion cadence — writing the ADR itself never waits for it.

---

## 10. Operation contracts

No agent determines its own authority — gate authority comes from
`../info.md`.

**Constitution operation** (`create-constitution-full`) — Can:
constitution artifacts, ask clarification. Must: ADR for project-level
decisions; first run, bootstrap
`info.md`/`context/context.md`/`decisions/decisions.md` unedited,
never overwrite existing. Cannot: touch code; invent unsupported
requirements.

**Phase-planning operation** (`define-phase`) — Can: read constitution
+ `context/`, create the phase file (Context + Requirements + Plan +
Validations + empty task table). Must: ADR for phase-level decisions;
update `roadmap.md`'s Status at transitions + its Depends-on column
for this phase and any existing phase it now precedes (§11, §12) +
refresh `info.md`'s Active phase pointer (§11 — pointer only, never a
status word). Cannot: implement code; **assign task IDs or populate
the task table beyond stub titles** — the Plan section isn't a task
list.

**Task-planning operation** (`define-task-full`) — Can: read phase
file + `context/`, create the task file with enough detail (files,
ordered steps, optional pseudocode) that implementation is close to
mechanical. Must: update the phase file's task table at every status
change — status never lives in the task file itself, nor in
`info.md`; there, only refresh the Active task pointer (§11). Cannot:
implement code; write an ADR — escalate as a phase-level deviation.

**Implementation operation** (`implement-task-full`) — Can: read task
file + context, modify project files, run tools. Must: update the
phase file's task table (status) + refresh `info.md`'s pointer (§11)
as it progresses; ADR for decisions made along the way (check the
index first); treat pseudocode as guidance (§6). Cannot: silently
change approved requirements/plan.

**Validation-review operation** (`validate-work-full`,
`review-work-full`) — the completion-review gate's two internal checks
(§8): validation runs first, review second. Can: run validation, report
failures, set Status `validating` in the phase file; inspect everything,
flag scope/requirement/complexity/architecture/validation/context issues
and undocumented decisions, set Status `reviewing` in the phase file;
both refresh `info.md`'s pointer (§11). Must: read `info.md` fresh
before trusting a gate's authority — never a cached read; stop for
`task-completion-review`/`phase-completion-review` after reporting, even
clean findings — never treat "no problems" as approval itself. Should
not: edit implementation to force a pass; silently fix issues, or write
a missing ADR itself.

**Context operation** (`propagate-context`, `build-context-full`) —
Can: propagate reusable knowledge to a phase file's Context or
`context/`; mark rows complete in the phase file + `roadmap.md`; clear
`info.md`'s pointer (§11); also runs `build-context-full`'s
assumption/iteration process to populate `context/` by surveying an
existing codebase, a second operation distinct from propagation. Must:
verify the completion-review gate was actually approved before marking
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
status lives only in the permanent record below. The Active phase
pointer is set the moment phase planning starts (`define-phase`) and
cleared once the phase is marked complete (`propagate-context`);
Active task follows the same pattern one level down (`define-task-full`
sets it, `propagate-context` clears it). `info.md` tracks only one
active phase/task by design; genuinely parallel work needs each agent
tracking its own item some other way until this format supports more
than one.

[HUMAN] Lets get rid of the word status, as it may mislead the agent.

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

## 13. Commit discipline

Commit each draft immediately, before requesting review — the review
happens via `git diff`. Message format and type selection are your
project's own convention (see your `AGENTS.md`); each skill's own
commit step says what to stage.

# General comments

We need to prune this document, as it gets read every call, or at least it should. Lets move all the how to to skills and let only the descriptive things inside this file.

[HUMAN]
