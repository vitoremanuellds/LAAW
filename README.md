# LAAW — Local AI Agents Workflow

A file-based workflow for developing software with AI coding agents — one
modular design whose weight scales via **optional layers** rather than
separately-maintained variants.

Built around the hardest constraints — small context windows, weaker
instruction-following — so it holds up on local models (7B–35B,
48k–64k context); the same discipline pays off on frontier models too,
just with more slack to work with.

---

## The problem

Four things get worse as models get smaller or context gets tighter:

1. **Hallucination** — agents invent steps or context when they've lost track
2. **Wasted context** — reading everything "just in case" fills windows fast
3. **Loss of human control** — agents push past gates or make scope decisions
4. **Unsafe parallel work** — multiple agents overwrite each other's changes

## How it works

Two ideas do most of the work:

### 1. Persist knowledge, not reasoning

Project knowledge lives in small Markdown files, linked together like a
graph. An agent starts at the smallest file that defines its current task
and follows links only as far as it needs to — it never reads the whole
`.ai/` tree to do bounded work.

### 2. Separate *what* from *who decides*

`workflow.md` defines the process (constitution → phases → tasks →
validation → review) and **never changes per-project**. `info.md` holds
who's authorized for each gate and what mode is active — it changes as
you trust the agents more, without touching the process itself.

Everything else — skills, agent contracts, deviation rules, context
propagation, the full gate list — lives inside `workflow.md`,
self-contained. See [`workflow.md`](workflow.md) for all of it.

---

## One workflow, three axes

LAAW used to ship `medium`/`lite`/`minimal` profiles alongside `full`,
then dropped to `full`-only. Maintaining several variants meant every
workflow change had to be ported across all of them. ADR03 replaced that
with a **single modular workflow** built on three independent axes:

| Axis | What it controls | How it works |
|---|---|---|
| **Presence** | Which layers are active | Every layer but `tasks/` is optional — inferred from what exists on disk. No config file needed. |
| **Granularity** | Task vs. phase structure | A task opts into a phase parent or not, independently of whether the project uses phases at all. |
| **Locality** | Where files live | One `.ai/` tree, always in-repo. A consuming project gitignores whatever layers it doesn't want committed. |

`full` and `Light` collapse into presets of this one design rather than
separately-versioned document sets.

---

## The directory structure

```
.ai/
├── workflow/              ← this repo's content, installed by sync-workflow.sh
│   ├── workflow.md        ← the whole workflow, self-contained
│   ├── skills/            ← one SKILL.md per operation
│   ├── reference/         ← occasional-need detail, one file per concept
│   └── templates/         ← templates for first-run scaffolding
├── info.md                ← Policy only: gate authority; always present
├── constitution/             ← optional: mission.md, techstack.md
├── context/                  ← optional: context.md + architecture files
├── decisions/                ← optional: decisions.md + adr{NN}-{name}.md
├── phases/                   ← optional: phases.md + p{NN}-{name}.md
├── tasks/                    ← mandatory: tasks.md + p{NN}-t{NN}-*.md + t{NN}-*.md
└── workbench/                ← optional: freeform scratch space
```

**Presence is inferred from existence** — a missing directory means that
layer is off. `.ai/tasks/` is the only one every project has. How a
layer comes into existence on first use: see
[`reference/scaffold-on-first-use.md`](reference/scaffold-on-first-use.md).

`.ai/tasks/` holds two task-file shapes, distinguished by filename:
`p{NN}-t{NN}-{name}.md` (phase-linked) and
`t{NN}-{name}.md` (orphan — no phase parent). A phase-linked task is
indexed only in its phase file's task table; an orphan task is indexed
in `.ai/tasks/tasks.md` — never both, never neither.

---

## Lifecycle & gates

```
Constitution → Constitution Review → Phase → Phase Plan Review
  → Tasks → Task Plan Review → Implement
  → Task Completion Review (validate, then review)
  → Context Evaluation → Task Complete → (repeat)
  → Phase Completion Review (validate, then review)
  → Reconcile Phase/Project Context → Phase Complete
```

**Gates for missing layers are skipped.** The lifecycle above shows
the full set — a project never walks through every gate; it only
encounters gates for layers that exist. If `constitution/` doesn't
exist, `constitution-review` doesn't run. If `phases/` doesn't exist,
`phase-review` and `phase-completion-review` don't run. If `context/`
doesn't exist, `context-update` and `context-evaluation` don't run.

| Gate | Runs after | Unlocks |
|---|---|---|
| `constitution-review` | constitution draft | phase planning |
| `phase-review` | phase plan draft | task planning |
| `task-review` | task-batch draft | implementation |
| `task-completion-review` | implementation | task complete |
| `phase-completion-review` | all tasks done | phase complete |
| `context-update` | alongside completion | — |

Gates block *advancing past* a draft, never *producing* one.

**Modes** (`info.md`: `mode` + `overrides`):

| Mode | Plan-review | Completion: mech. | Completion: judgment | `context-update` |
|---|---|---|---|---|
| `manual` | human | human | human | human |
| `assisted` (default) | human | agent | human | agent |
| `autonomous` | agent | agent | agent | agent |
| `delegated` | — | — | — | — |

`delegated`: no defaults — every gate listed in `overrides`, else
`human`.

---

## This repo vs. your project

| This repo (`.ai/workflow/`, installed by `sync-workflow.sh`) | Your project (`.ai/`, edit freely) |
|---|---|
| `workflow.md` | `info.md` — bootstrapped from template, then yours |
| `skills/*` — one per operation | `constitution/*` — mission.md, techstack.md; optional |
| `reference/*` — occasional-need detail | `context/*` — optional |
| `templates/*` — first-run scaffolding | `phases/*` — optional |
| `sync-workflow.sh` | `tasks/*` — **mandatory layer** |
| `sync-skills.sh` (optional mirror) | `decisions/*` — optional |

A third category, technically outside both: `.agents/skills/`, if you
use `sync-skills.sh` — a generated copy, not source of truth. Same
status for `.ai/workflow-version`, written by `sync-workflow.sh` —
generated metadata, not hand-edited.

If you find yourself editing anything under `.ai/workflow/` per-project,
that's a signal the workflow itself needs a change — make it in this
repo instead.

---

## Bootstrap into a project

Clone this repo somewhere on disk, then run `sync-workflow.sh` against
your project. **No `git submodule` command is involved.**

```bash
git clone <this-repo-url> /path/to/LAAW
cd your-project
/path/to/LAAW/sync-workflow.sh
```

`sync-workflow.sh` takes two optional positional arguments —
`[source-dir] [target-root]` — each defaulting sensibly. Running it with
no arguments from inside your project is the normal case.

### 1. Wire up `AGENTS.md`

Paste this into your project's `AGENTS.md` (create the file or add as a
section):

```markdown
## Agent Workflow
This project uses a structured, modular agent workflow — one process,
with optional layers rather than a profile choice:
- `.ai/info.md` exists → open and read in full — not "recall it
  exists," actually read it —
  [.ai/workflow/workflow.md](.ai/workflow/workflow.md).
- `.ai/info.md` doesn't exist → unbootstrapped. Run
  `.ai/workflow/skills/create-constitution/SKILL.md` (or
  `.ai/workflow/skills/bootstrap/SKILL.md` to set up several
  layers at once) to bootstrap it before doing anything else.

Do this before acting, every session — not just once, and not from
memory of a previous read. Gate-skip and scope-overstep bugs have
consistently traced back to this step being skipped.
```

### 2. Bootstrap `info.md` and optional layers

Point an agent (or yourself) at:

- **`create-constitution`** — mission + techstack interview, plus
  `info.md`'s unconditional first-run bootstrap
- **`bootstrap`** — asks which of constitution/context/decisions/phases
  to set up now (each an empty scaffold; constitution gets the same
  interview)

Until one of these runs, `.ai/info.md` doesn't genuinely exist yet —
that's expected. Defaults are safe/conservative (`mode: assisted`); edit
the policy block afterward once you're ready to delegate gates.

### 3. Optional: sync skills to `.agents/skills/`

If your harness auto-discovers skills from `.agents/skills/` rather
than following `workflow.md`'s lookup table:

```bash
.ai/workflow/sync-skills.sh
```

Re-run it after every `sync-workflow.sh` re-sync. If you don't know
whether your harness needs this, you probably don't —
`workflow.md §2`'s own lookup table works without it.

---

## Updating the workflow

Re-running `sync-workflow.sh` re-syncs `.ai/workflow/` to the source
checkout's current `HEAD` — wholesale-replacing its content:

```bash
cd /path/to/LAAW && git pull
cd your-project
/path/to/LAAW/sync-workflow.sh
```

**Review what changed before adopting it.** This repo doesn't yet publish
tagged releases, so treat every commit as a potential breaking change:

```bash
git -C /path/to/LAAW log --oneline -5   # find a reviewed commit
git -C /path/to/LAAW checkout <sha>     # pin your clone there
```

Then point `sync-workflow.sh` at that pinned clone as its source
argument. Your project's own content (`info.md`, `constitution/`,
`context/`, `phases/`, `tasks/`, `decisions/`) is untouched.

---

## Best practices

**Reasoning effort should match the gate, not stay uniform.** If your
harness lets you set thinking/reasoning level per call:

- **High/medium** — `create-constitution`, `define-phase`,
  `define-task`, and any deviation/ADR work. Ambiguity is real here; a
  wrong call cascades.
- **Low** — `implement-task` and `validate-work`. Hard thinking happened
  at planning time; execution should be close to mechanical.

**Call the skill explicitly.** Say "use `define-task` to plan this"
rather than phrasing generically. This has been the single most common
failure point in testing.

**Name the task or phase you mean.** "Implement P02-T03" beats
"implement the next task," especially after replanning. Task IDs are
sequential and never reflect reordering.

**One thread per phase/task-batch.** Starting fresh threads for
subsequent phases keeps each one's context budget close to what it needs,
rather than accumulating full project history.

**Watch for skills reading one step ahead.** A model may read an adjacent
skill even when its prerequisites aren't met. Harmless if it just
previews, but worth tightening descriptions if an agent *acts* prematurely.

**A gate's authority can change mid-session.** Read `info.md` fresh at
every gate check, not from memory. This caused a real bug: a gate's
authority changed partway through a session, and a skill that had read
the old value earlier kept acting on stale information.

**Keep `.ai/workflow/` clean.** If a skill seems to want to edit
`workflow.md` mid-task, that's feedback for this repo — not a local
patch to apply. A local patch will be overwritten by the next
`sync-workflow.sh` and silently diverge.

---

## What's in this repo

```
README.md
workflow.md                    ← the whole workflow, self-contained
sync-workflow.sh               ← installs/re-syncs into a target's .ai/workflow/
sync-skills.sh                 ← optional: mirrors skills/ to .agents/skills/
reference/                       ← occasional-need detail
├── directory-and-links.md
├── reread-skill-discipline.md
├── scaffold-on-first-use.md
├── starting-without-a-plan.md
└── status-and-info.md
templates/
├── info-template.md
├── context-template.md
├── decisions-template.md
├── adr-template.md
└── workbench-readme-template.md
skills/
├── bootstrap/
├── create-constitution/
├── define-phase/
├── define-task/
├── implement-task/
├── validate-work/
├── review-work/
├── propagate-context/
└── build-context/
```

Once installed at `.ai/workflow/` in a project, alongside it (in the
project's own repo) you'll have, once each optional layer comes into
use:

```
.ai/
├── workflow/              ← this repo's content
├── workflow-version       ← generated: source, commit SHA, date
├── info.md                  ← policy only
├── constitution/             ← optional
├── context/                  ← optional
├── phases/                   ← optional
├── tasks/                    ← mandatory
└── decisions/                ← optional
```

Every link inside this repo is relative and none hardcode `.ai/`, so it
stays correct regardless of what your project names the mount point.
Full layout and link conventions: [`workflow.md §3`](workflow.md#3-directory-structure).
