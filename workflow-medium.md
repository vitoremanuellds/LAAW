# Agent Workflow Protocol — Medium Profile

Source of truth for the **medium** profile: a project of moderate size,
one flat task list under a constitution, no phase layer. Self-contained
— everything an agent needs for medium-profile work lives in this one
file plus whichever single `skills/medium-*/SKILL.md` matches the
current operation. It does not reference `workflow.md` (the full
profile) and `workflow.md` does not reference this file — the two
profiles are independent documents by design, not variants of each
other. See `../README.md` for how a project picks a profile.

Gate *authority* (who) lives in `../info.md`, not here. Do not
duplicate this file's rules elsewhere — reference it.

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
   section = active task. Policy section = gate authority. **If it
   doesn't exist, this is an unbootstrapped project** — treat every
   gate as human-owned and run `medium-constitution` first, which
   creates it from `templates/medium-info-template.md`.
2. **Open and read the matching skill file below before acting** — not
   "recall it exists," actually read it, every operation, even if you
   think you know it.
3. Never bypass a gate unless `info.md`'s policy explicitly authorizes it.

| Operation | Skill |
|---|---|
| Define/update mission, techstack, roadmap (flat task index) | `skills/medium-constitution/` |
| Define a task (`tasks/t{NN}-{name}.md`) | `skills/medium-task/` |
| Write/modify/delete code for an already-planned task | `skills/medium-implementation/` |
| Run task validation | `skills/medium-validation/` |
| Review implementation and validation, propagate context, mark complete | `skills/medium-review/` |

Can't find the right skill? Re-read this table — don't guess paths.

---

## 3. Directory structure

```
.ai/
├── workflow/                 ◄── submodule boundary — never written to
├── info.md                    Policy + Status, merged
├── constitution/               mission.md, techstack.md, roadmap.md (flat task index)
├── context/context.md            single file — no proliferation of context/*.md at this scale
├── decisions/                     decisions.md (index) + adr{NN}-{name}.md
└── tasks/                          t{NN}-{name}.md, flat, own Context + Implementation
```

No phase layer — `roadmap.md`'s rows *are* the task index directly
(`ID | Title | Purpose | Depends on | Status`), not a phase list. Task
IDs are `T{NN}` (no `p{NN}-` prefix — there's nothing to prefix them
against). A task file's optional pseudocode section from the full
profile is dropped here — steps must stand on their own.

**Every bare mention below** of `info.md`, `roadmap.md`, `tasks/`,
`context/`, or `decisions/` refers to that file/folder under `.ai/` as
shown above. When a **skill** instructs an actual write/read, it
spells out the full `.ai/`-prefixed path explicitly — a bare or
dot-relative path handed to a write tool resolves against the agent's
working directory, not against where any instruction was read from.

**Link rule:** cross-references use `.ai/workflow/`-anchored paths, not
dot-relative ones, for the same reason the full profile does — so a
mirrored skill copy (`sync-skills.sh`) doesn't silently break.

**Naming:** tasks `t{NN}-{kebab-name}.md` (flat); decisions
`adr{NN}-{kebab-name}.md`. IDs sequential, never reused.

**Size target:** ~2048 tokens/file. Split only when mixing concerns.

---

## 4. Artifact hierarchy & context rule

```
Constitution → Context (context.md) → Decisions → Tasks (own Context)
```

Each level links to exactly the one above it. Read: `info.md` → the
artifact defining current work → direct references → further links
only if genuinely needed. A link is a pointer, not a preload.

---

## 5. Lifecycle & gates

```
Constitution → Constitution Review → Task Plan → Task Plan Review
  → Implement → Validate → Review (incl. context propagation)
  → Task Complete → (repeat)
```

One fewer hierarchy level than full means one fewer independent
gate-worthy transition: there's no phase-review/phase-validation/
phase-completion-review triad, and context propagation is a step
inside `task-completion-review` rather than its own `context-update`
gate — a task's context either matters to the project (goes to
`context.md` right then) or it doesn't; there's no intermediate phase
Context to promote through.

**Full gate list:** `constitution-review` · `task-review` ·
`task-validation` · `task-completion-review`. Four, not eight.

**Gates block *advancing past* a draft, never *producing* one.**
Drafting never needs prior approval; only passing review does.

**Each gate unlocks only the next operation, nothing further.**
`task-review` → implementation of *that* task only.
`task-completion-review` unlocks marking complete, nothing retroactive.

**Unlocking ≠ starting.** In `manual`/`assisted` mode: report the gate
passed, update `info.md`, then explicitly ask before the next
operation — a distinct confirmation, even though the gate authorizes
it. `delegated`/`autonomous` mode: chain straight through.

### Execution modes

`info.md` sets `mode` + optional `overrides`:

- **`manual`** — all gates default `human`.
- **`assisted`** (recommended default) — `task-validation` defaults
  `agent`; rest `human`.
- **`delegated`** — no default; every gate must be listed in
  `overrides`, unlisted falls back to `human`.
- **`autonomous`** — all gates default `agent`; list any you want held
  back at `human`.

**Task complete requires:** implementation + validation +
`task-completion-review` + context propagated (as part of that same
review) + roadmap.md's row marked complete + `info.md` cleared.

Completion-review (`task-completion-review`) ≠ plan-review
(`task-review`) — plan before implementation, completion after. Both
default `human` in `assisted` mode (coherence/judgment), unlike
`task-validation` (mechanical, defaults `agent`).

---

## 6. Deviations

Deviation = work materially differs from the approved plan. A wrong
file or small mismatch is not one — adjust and continue. Record one
when a planned approach fails, scope changes materially, or an
assumption breaks:

```
Expected / Discovered / Why it fails / Proposed fix / Replan? (task/project)
```

File: `tasks/t03-{name}-deviation.md`, next to the task it concerns.
Lifecycle: `OPEN → ADDRESSED → INCORPORATED`, then delete — the fact
must already live in the plan, implementation, or an ADR.

- **Task-level** → back to the implementation loop.
- **Project-level** → Constitution Agent replans, always writes an ADR.

There is no phase-level tier here — a deviation too big for the task
loop escalates straight to the project level, since there's no phase
in between to absorb it.

---

## 7. Decisions (ADRs)

Write one when a decision is deliberate and future work needs to know
it. Not every deviation produces one; not every ADR comes from one.

**Ownership — whoever's scope produced the decision writes it:**
Constitution Agent (project) · Implementation Agent (during
implementation). No one else writes one — Review Agent flags a missing
ADR back to the owning scope. Task Planning Agent cannot write one —
a decision surfacing during task planning escalates as a project-level
deviation to the Constitution Agent, since there's no phase level to
absorb it first.

Check `../decisions/decisions.md` first. Copy
[`templates/adr-template.md`](templates/adr-template.md) to
`../decisions/adr{NN}-{name}.md`, fill it in, add its index row (ID,
Name, Description, Status `valid`, Relations) in the same step.

A superseding ADR updates both rows' Relations rather than deleting
the old one.

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
Task done → matters to future tasks or the project as a whole?
  → update context/context.md
```

One step, not two — there's no phase layer to promote *through*, so a
fact either belongs in `context.md` or it doesn't need to be recorded
at all.

**Propagate:** architecture facts, invariants, responsibilities,
dependencies, constraints, domain knowledge.
**Never:** task history, temporary details, internal reasoning,
progress reports, anything recorded elsewhere.

Touching `context/context.md` means updating its own entry-table row
in the same step, same as the full profile.

---

## 10. Agent contracts

No agent determines its own authority — gate authority comes from
`../info.md`.

**Constitution Agent** — Can: constitution artifacts, ask
clarification. Must: ADR for project-level decisions; first run,
bootstrap `info.md`/`context/context.md`/`decisions/decisions.md`
unedited, never overwrite existing. Cannot: touch code; invent
unsupported requirements.

**Task Planning Agent** — Can: read constitution + `context/`, create
the task file with enough detail (files, ordered steps — no
pseudocode at this profile) that implementation is close to
mechanical. Must: update `roadmap.md`'s row at every status change —
status never lives in the task file itself, nor in `info.md`; there,
only refresh the Active task pointer (§11). Cannot: implement code;
write an ADR — escalate as a project-level deviation (§6, §7).

**Implementation Agent** — Can: read task file + context, modify
project files, run tools. Must: update `roadmap.md`'s row (status) +
refresh `info.md`'s pointer (§11) as it progresses; ADR for decisions
made along the way (check the index first); treat deviations per §6.
Cannot: silently change approved requirements/plan.

**Validation Agent** — Can: run validation, report failures; set
Status `validating` in `roadmap.md`, refresh `info.md`'s pointer.
Must: read `info.md` fresh before trusting a gate's authority — never
a cached read. Should not: edit implementation to force a pass.

**Review Agent** — Can: inspect everything, flag scope/requirement/
complexity/architecture/validation/context issues and undocumented
decisions; set Status `reviewing` in `roadmap.md`, refresh `info.md`'s
pointer; once `task-completion-review` is approved, propagate context
(§9), set Status `complete` in `roadmap.md`, clear `info.md`'s
pointer. Must: stop for `task-completion-review` after reporting, even
clean findings — never treat "no problems" as approval itself. Should
not: silently fix, or write a missing ADR itself, or mark complete
before approval is actually confirmed.

---

## 11. Status: the fast pointer and the permanent record

**`info.md`'s Status section** — fast, ID only, no status values:
`Active task`. Updated first and last by every skill. Tells you which
file to open, nothing more.

**Permanent record** — every status value, everything, not just
active: `roadmap.md`'s Status column, one row per task. Check here for
"what's the state of X," not just what's active.

**Shared Status enum**, `roadmap.md`:

```
not-planned → awaiting-plan-review → plan-approved → in-progress
  → validating → reviewing → complete
(blocked applies from any active state)
```

| Value | Set by |
|---|---|
| `not-planned` | `medium-constitution` (every task stub, initially) |
| `awaiting-plan-review` | `medium-task`, end of drafting |
| `plan-approved` | Whichever skill's ending receives approval |
| `in-progress` | `medium-implementation`, implementation begins |
| `validating` | `medium-validation` |
| `reviewing` | `medium-review` — a different check than plan-review |
| `complete` | `medium-review`, only after `task-completion-review` is approved |
| `blocked` | any agent, from any active state |

**Task ID order ≠ execution order.** A replan can insert a task that
logically belongs earlier but still gets the next-highest ID. Resolve
"first/next task" against `roadmap.md`'s Depends-on and Status
columns — no unmet dependencies, Status `awaiting-plan-review`/
`plan-approved` — not the lowest ID. Ask rather than guess if still
ambiguous.

---

## 12. Multi-agent / multi-human

Independent tasks may run in parallel. Shared state lives in Git,
`info.md`, and `roadmap.md` — never a second Markdown sync mechanism.
Avoid concurrent edits to the same artifact. `info.md` tracks only one
active task by design — true parallel work needs each agent tracking
its own item some other way until this format supports more than one.

---

## 13. Commit discipline

Commit a draft the moment it's written, before requesting review — the
review happens via `git diff`. Messages tied to IDs: `T01: task
planned`, `T01: implementation complete`, `T01: task complete`. Commit
again whenever `info.md` or `roadmap.md` changes.
