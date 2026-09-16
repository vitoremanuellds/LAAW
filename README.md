# LAAW — Local AI Agents Workflow

A file-based workflow for developing software with AI coding agents — one
modular design whose weight scales via **optional layers** rather than
separately-maintained variants.

Built around the hardest constraints — small context windows, weaker
instruction-following — so it holds up on local models (7B–35B,
48k–64k context); the same discipline pays off on frontier models too,
just with more slack to work with.

---



<!-- TOC -->
<details><summary>Table of Contents</summary>

  - [The problem](#the-problem)
  - [How it works](#how-it-works)
    - [1. Persist knowledge, not reasoning](#1-persist-knowledge-not-reasoning)
    - [2. Separate *what* from *who decides*](#2-separate-what-from-who-decides)
  - [One workflow, no profiles](#one-workflow-no-profiles)
  - [The directory structure](#the-directory-structure)
  - [Lifecycle & gates](#lifecycle-gates)
  - [Router skill](#router-skill)
  - [Bootstrap into a project](#bootstrap-into-a-project)
    - [1. Wire up `AGENTS.md`](#1-wire-up-agentsmd)
  - [Agent Workflow](#agent-workflow)
    - [2. Bootstrap `info.md` and optional layers](#2-bootstrap-infomd-and-optional-layers)
    - [3. Optional: sync skills to `.agents/skills/`](#3-optional-sync-skills-to-agentsskills)
  - [Updating the workflow](#updating-the-workflow)
  - [Best practices](#best-practices)
  - [What's in this repo](#whats-in-this-repo)

</details>


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

`workflow.md` defines the process (tasks → task-review → implementation
→ task-completion-review) and **never changes per-project**. `info.md`
holds who's authorized for each gate and what mode is active — it
changes as you trust the agents more, without touching the process
itself.

Everything else — skills, agent contracts, deviation rules, context
propagation, the full gate list — lives inside `workflow.md`,
self-contained. See [`workflow.md`](workflow.md) for all of it.

---

## One workflow, no profiles

LAAW ships a single workflow — no `medium`/`lite`/`minimal` profiles.
Optional layers are inferred from what exists on disk; no config file
declares which layers a project uses. `.ai/tasks/` is mandatory;
everything else is optional. How a layer comes into existence on first
use: see
[`reference/scaffold-on-first-use.md`](reference/scaffold-on-first-use.md).

---

## The directory structure

```
.ai/
├── workflow/              ← this repo's content, installed by sync-workflow.py
│   ├── workflow.md        ← the whole workflow, self-contained
│   ├── skills/            ← one SKILL.md per operation
│   │   ├── route/         ← router: plain-language → correct skill
│   │   ├── bootstrap/
│   │   ├── create-constitution/
│   │   ├── define-task/
│   │   ├── implement-task/
│   │   ├── validate-work/
│   │   ├── review-work/
│   │   ├── build-context/
│   │   └── propagate-context/
│   ├── reference/         ← occasional-need detail, one file per concept
│   ├── templates/         ← templates for first-run scaffolding
│   └── tools/             ← generate-id.py, sync-workflow.py, sync-skills.py, .epoch
├── info.md                ← Policy only: gate authority; always present
├── context/                  ← optional: context.md + c-{ID}-{name}.md
├── tasks/                    ← mandatory: tasks.md + t{ID}-{name}/task.md
└── workbench/                ← optional: freeform scratch space
```

**Presence is inferred from existence** — a missing directory means that
layer is off. `.ai/tasks/` is the only one every project has. How a
layer comes into existence on first use: see
[`reference/scaffold-on-first-use.md`](reference/scaffold-on-first-use.md).

`.ai/tasks/` holds two shapes, distinguished by path: a **leaf task**
(`t{ID}-{name}/task.md`) and a **task with subtasks**
(`t{ID}-{name}/` — a folder containing the parent file
`task.md` and subtask files below it). The same rule applies at
every nesting level: if a task has subtasks, it is a folder; if it does
not, it is a leaf file. IDs are sequential and never reused.

---

## Lifecycle & gates

```
Tasks → Task Plan Review → Implement
  → Task Completion Review (validate, then review)
  → Context Evaluation → Task Complete → (repeat)
```

**Gates for missing layers are skipped.** The lifecycle above shows
the full set — a project never walks through every gate; it only
encounters gates for layers that exist.

| Gate | Runs after | Unlocks |
|---|---|---|
| `task-review` | task-batch draft | implementation |
| `task-completion-review` | implementation (mech., then judgment) | task complete |

Gates block *advancing past* a draft, never *producing* one.

**Modes** (`info.md`: `mode` + `overrides`):

| Mode | Plan-review | Compl.: mech. | Compl.: judgment |
|---|---|---|---|
| `manual` | human | human | human |
| `assisted` (default) | human | agent | human |
| `autonomous` | agent | agent | agent |

**Task complete:** implementation + `task-completion-review` (both
checks) + context evaluated.

Starting without every task already planned is normal:
[`reference/starting-without-a-plan.md`](reference/starting-without-a-plan.md).

---

## Router skill

Users state what they want in plain terms — "plan a task", "implement
X", "build context" — and the router (`skills/route/SKILL.md`) points
the agent at the correct operation skill. You don't need to name skills
explicitly; the router handles the mapping. The router does no operation
work itself; it only reads the user's request and points at the right
skill file.

---

## Bootstrap into a project

Clone this repo somewhere on disk, then run `sync-workflow.py` against
your project. **No `git submodule` command is involved.**

```bash
git clone <this-repo-url> /path/to/LAAW
cd your-project
/path/to/LAAW/tools/sync-workflow.py
```

`sync-workflow.py` takes two optional positional arguments —
`[source_dir] [target_root]` — each defaulting sensibly. Running it
with no arguments from inside your project is the normal case.

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
  [.ai/workflow/skills/route/SKILL.md](.ai/workflow/skills/route/SKILL.md)
  and say "bootstrap" to set up several layers at once.

Do this before acting, every session — not just once, and not from
memory of a previous read. Gate-skip and scope-overstep bugs have
consistently traced back to this step being skipped.
```

### 2. Bootstrap `info.md` and optional layers

Point an agent (or yourself) at:

- **`create-constitution`** — mission + techstack interview, plus
  `info.md`'s unconditional first-run bootstrap
- **`bootstrap`** — asks which optional layers to set up now (each an
  empty scaffold; constitution gets the same interview)

Until one of these runs, `.ai/info.md` doesn't genuinely exist yet —
that's expected. Defaults are safe/conservative (`mode: assisted`);
edit the policy block afterward once you're ready to delegate gates.

### 3. Optional: sync skills to `.agents/skills/`

If your harness auto-discovers skills from `.agents/skills/` rather
than following `workflow.md`'s lookup table:

```bash
.ai/workflow/tools/sync-skills.py
```

Re-run it after every `sync-workflow.py` re-sync. If you don't know
whether your harness needs this, you probably don't —
`workflow.md §2`'s own lookup table works without it.

---

## Updating the workflow

Re-running `sync-workflow.py` re-syncs `.ai/workflow/` to the source
checkout's current `HEAD` — wholesale-replacing its content:

```bash
cd /path/to/LAAW && git pull
cd your-project
/path/to/LAAW/tools/sync-workflow.py
```

**Review what changed before adopting it.** This repo doesn't yet publish
tagged releases, so treat every commit as a potential breaking change:

```bash
git -C /path/to/LAAW log --oneline -5   # find a reviewed commit
git -C /path/to/LAAW checkout <sha>     # pin your clone there
```

Then point `sync-workflow.py` at that pinned clone as its source
argument. Your project's own content (`info.md`, `context/`, `tasks/`,
`workbench/`) is untouched.

---

## Best practices

**Reasoning effort should match the gate, not stay uniform.** If your
harness lets you set thinking/reasoning level per call:

- **High/medium** — `create-constitution`, `define-task`, and any
  deviation/decision work. Ambiguity is real here; a wrong call
  cascades.
- **Low** — `implement-task` and `validate-work`. Hard thinking happened
  at planning time; execution should be close to mechanical.

**State what you want in plain terms.** Say "plan a task for X" rather
than "use `define-task`." The router skill maps your request to the
correct skill automatically.

**Name the task you mean.** "Implement t{xxx-yyyy-zzzzz}" beats
"implement the next task," especially after replanning. Task IDs are
sequential and never reflect reordering.

**One thread per task-batch.** Starting fresh threads for subsequent
tasks keeps each one's context budget close to what it needs, rather
than accumulating full project history.

**Watch for skills reading one step ahead.** A model may read an
adjacent skill even when its prerequisites aren't met. Harmless if it
just previews, but worth tightening descriptions if an agent *acts*
prematurely.

**A gate's authority can change mid-session.** Read `info.md` fresh at
every gate check, not from memory. This caused a real bug: a gate's
authority changed partway through a session, and a skill that had read
the old value earlier kept acting on stale information.

**Keep `.ai/workflow/` clean.** If a skill seems to want to edit
`workflow.md` mid-task, that's feedback for this repo — not a local
patch to apply. A local patch will be overwritten by the next
`sync-workflow.py` and silently diverge.

---

## What's in this repo

```
README.md
workflow.md                    ← the whole workflow, self-contained
reference/                       ← occasional-need detail
├── directory-and-links.md
├── reread-skill-discipline.md
├── scaffold-on-first-use.md
├── starting-without-a-plan.md
└── status-and-info.md
templates/
├── task-template.md
├── context-item-template.md
├── context-template.md
├── info-template.md
├── workbench-readme-template.md
├── assumptions-template.md
└── context-build-plan-template.md
skills/
├── route/                     ← router
├── bootstrap/
├── create-constitution/
├── define-task/
├── implement-task/
├── validate-work/
├── review-work/
├── build-context/
└── propagate-context/
tools/
├── generate-id.py             ← mint t{xxx-yyyy-zzzzz} / c{xxx-yyyy-zzzzz}
├── sync-workflow.py           ← cross-platform workflow sync
├── sync-skills.py             ← cross-platform skills mirror
└── .epoch                     ← default epoch for ID generation
```

Once installed at `.ai/workflow/` in a project, alongside it (in the
project's own repo) you'll have, once each optional layer comes into
use:

```
.ai/
├── workflow/              ← this repo's content
├── workflow-version       ← generated: source, commit SHA, date
├── info.md                  ← policy only
├── context/                  ← optional
├── tasks/                    ← mandatory
└── workbench/                ← optional
```

Every link inside this repo is relative and none hardcode `.ai/`, so it
stays correct regardless of what your project names the mount point.
Full layout and link conventions: [`workflow.md §3`](workflow.md#3-directory-structure).
