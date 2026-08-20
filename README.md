# Agents With Local Models — Workflow

A structured protocol for developing software with AI agents — tuned
for local models (7B–35B, 48k–64k context) but not limited to them.

It exists to solve four problems that get worse as models get smaller
or context gets tighter: hallucination, wasted context, loss of human
control, and unsafe parallel work.

## How it works, briefly

Two ideas do most of the work:

1. **Don't make agents reconstruct what can be written down once.**
   Project knowledge lives in small Markdown files, linked together
   like a graph. An agent starts at the smallest file that defines its
   current task and follows links only as far as it needs to — it
   never reads the whole project to do bounded work.

2. **Separate *what* must happen from *who* is allowed to decide it.**
   `workflow/workflow.md` defines the process (constitution → phases →
   tasks → validation → review) and never changes. `policy.md` defines
   which gates a human must approve and which an agent may — and
   *that* can change freely as you trust the agents more, without
   touching the process itself.

Everything else — skills, agent contracts, deviation/decision rules,
context propagation — lives inside that one self-contained protocol
file. See [`workflow/workflow.md`](workflow/workflow.md) for all of it.
This repo's root is designed to *become* your project's `.ai/` folder
directly — see Bootstrapping below.

## Bootstrapping into a project

### Option A — copy the template

```bash
git clone <this-repo-url> .ai
rm -rf .ai/.git    # detach it from this repo's history
```

### Option B — git submodule (keeps the protocol updatable)

```bash
cd your-project
git submodule add <this-repo-url> .ai
```

One command — the submodule's name *is* `.ai`, so there's no extra copy
step. `git submodule update --remote .ai` later pulls protocol updates
into every project using it.

Either way, after this:

1. **Wire up `AGENTS.md`.** This repo does not ship its own — most
   projects already have one, or use it for other tools too. Paste this
   block into your project's `AGENTS.md` (create the file if it
   doesn't exist; add as a section if other instructions already live
   there):

   ```markdown
   ## Agent Workflow
   This project uses a structured agent workflow. Before planning,
   implementing, validating, reviewing, or maintaining context, read
   [.ai/workflow/workflow.md](.ai/workflow/workflow.md) and follow it.
   ```

   That single pointer is enough — everything else is discovered from
   there, including the skill lookup table.

2. **Fill the constitution.** Point an agent (or yourself) at
   `.ai/workflow/skills/workflow-constitution/SKILL.md` and write
   `mission.md`, `techstack.md`, and `roadmap.md` for your actual
   project. This is the only step that can't be skipped — everything
   downstream assumes it exists.

3. **Set your execution policy.** Open `.ai/policy.md`. If you don't
   trust agents yet, leave `mode: manual` and every gate on `human`.
   You can delegate gates later without touching anything else.

There's no state file to check or initialize — status lives in
`constitution/roadmap.md` (phase-level) and each phase's
`tasks/index.md` (task-level), both created as you go.

From there the normal loop is: plan a phase → get it reviewed → break
it into tasks → implement → validate → review → let context propagate
→ repeat. Full lifecycle: [`workflow/workflow.md §5`](workflow/workflow.md#5-lifecycle--gates).

## What you fill in vs. what's fixed

| Fixed (don't edit per-project) | Filled in per-project |
|---|---|
| `workflow/workflow.md`, `workflow/skills/*` | Your project's `AGENTS.md` |
| `workflow/decision-template.md` | `constitution/*` |
| | `project-context/*` |
| | `phases/*` |
| | `decisions/*` |
| | `policy.md` (adjusted as trust grows) |

If you find yourself editing `workflow/workflow.md` per-project, that's
a signal the protocol itself needs a change — make it here, in this
repo, so every project using it benefits.

## Repository structure

This repo's root is flat by design except for one level of nesting
around the protocol itself — everything that's genuinely per-project
config or content sits at the top level; everything that's fixed
protocol sits under `workflow/`:

```
README.md              ← this file — also readable as .ai/README.md once installed
policy.md                ← per-project config: who's authorized for each gate
workflow/
├── workflow.md            ← the whole protocol, self-contained
├── decision-template.md    ← ADR template, instantiated into decisions/
└── skills/
    ├── workflow-constitution/
    ├── workflow-phase/
    ├── workflow-task/
    ├── workflow-implementation/
    ├── workflow-validation/
    ├── workflow-review/
    └── workflow-context/
decisions/
└── index.md
```

Not shipped by the template — created as you use it:
`constitution/`, `project-context/`, `phases/`.

Every link between these files is relative and none hardcode `.ai/`,
so this whole tree is portable to any folder name or nesting depth
without touching a single link. Full layout and link conventions:
[`workflow/workflow.md §3`](workflow/workflow.md#3-directory-structure).

## Best Practices

Learned from actually running this against a local model — update this
section as more surfaces.

**Reasoning effort should match the gate, not stay uniform.** If your
harness lets you set a thinking/reasoning level per call (e.g. Ollama's
OpenAI-compatible endpoint), don't leave it at the same setting for
every skill:

- **High/medium** — `workflow-constitution`, `workflow-phase`, and any
  deviation or ADR decision. These are exactly the places ambiguity is
  real and a wrong call cascades into everything built on top. Spending
  reasoning budget here is the point of the workflow.
- **Low** — `workflow-implementation` and `workflow-validation`. The
  hard thinking already happened at planning time; execution should be
  close to mechanical (follow the steps, adjust minor mismatches,
  escalate real deviations rather than reasoning your way around them).
  This is also your most frequently invoked skill, so unnecessary
  reasoning tokens here compound fast across a phase.

Compare actual token usage and output quality before committing to a
split — it varies by model.

**Be explicit about which operation you want.** Constitution creation
in particular tends to prompt for confirmation before starting if asked
generically ("plan the app") rather than directly ("create the
constitution"). Neither is wrong, but if you want it to proceed without
asking, say so — this is a prompting choice, not a workflow gate (there
is deliberately no "may I start" gate in `policy.md`, only review gates
after a draft exists).

**One thread per phase/task-batch of work, not one long thread.** The
workflow assumes stateless agents — bootstrapping/constitution work is
naturally the most expensive single operation (one-time, front-loads
project understanding) and is worth spending a large chunk of context
on, since everything downstream reads the result rather than repeating
the work. Starting fresh threads for subsequent phases keeps each one's
context budget close to just what that phase/task needs, rather than
accumulating the full project history in one window.

**Watch for skills reading one step ahead of where they should.** A
model may read an adjacent skill (e.g. `workflow-phase` while still
doing constitution work) even when its own description says it requires
the prior step to exist first. Usually harmless — it doesn't act
prematurely, just previews — but if you see an agent *acting* on a
skill before its prerequisites are met, that's worth tightening the
skill descriptions to be more mutually exclusive.

**No state file means status must come from the indexes, every time.**
Since `state.md` was removed in favor of `roadmap.md` + `tasks/index.md`
carrying status directly, watch early on whether agents reliably check
those before assuming what's active — this replaced a real bug (a
never-updated `state.md`) but shifts the burden onto every skill
consistently writing to the right index at the right moment. Worth
extra scrutiny in the first few runs after this change.
