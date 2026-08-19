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
   current task and follows links only as far as it needs to —  it
   never reads the whole project to do bounded work.

2. **Separate *what* must happen from *who* is allowed to decide it.**
   `workflow.md` defines the process (constitution → phases → tasks →
   validation → review) and never changes. `policy.md` defines which
   gates a human must approve and which an agent may — and *that* can
   change freely as you trust the agents more, without touching the
   process itself.

Everything else — skills, agent contracts, deviation/decision rules,
context propagation — supports those two ideas. See
[`workflow.md`](workflow.md) for the full protocol and
[`index.md`](index.md) to navigate the rest. This repo's root is
designed to *become* your project's `.ai/` folder directly — see
Bootstrapping below.

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
   projects already have one, or use it for other tools too. Instead,
   paste [`agents-snippet.md`](agents-snippet.md) into your project's
   `AGENTS.md` (create the file if it doesn't exist). The snippet is a
   single pointer to `.ai/index.md` — everything else is discovered
   from there.

2. **Fill the constitution.** Point an agent (or yourself) at
   `.ai/skills/workflow-constitution/SKILL.md` and write
   `mission.md`, `techstack.md`, and `roadmap.md` for your actual
   project. This is the only step that can't be skipped — everything
   downstream assumes it exists.

3. **Set your execution policy.** Open `.ai/policy.md`. If you don't
   trust agents yet, leave `mode: manual` and every gate on `human`.
   You can delegate gates later without touching anything else.

4. **Check `.ai/state.md`** — it should read "not started." An agent
   or human updates it as the first phase begins.

From there the normal loop is: plan a phase → get it reviewed → break
it into tasks → implement → validate → review → let context propagate
→ repeat. Full lifecycle diagrams: [`.ai/lifecycle.md`](lifecycle.md).

## What you fill in vs. what's fixed

| Fixed (don't edit per-project) | Filled in per-project |
|---|---|
| `agents-snippet.md` (pasted once, then fixed) | Your project's `AGENTS.md` |
| `.ai/index.md`, `workflow.md` | `.ai/constitution/*` |
| `.ai/structure.md`, `lifecycle.md` | `.ai/project-context/*` |
| `.ai/deviations.md`, `agents.md` | `.ai/phases/*` |
| `.ai/skills/*` | `.ai/decisions/*` |
| | `.ai/state.md` (updated, not rewritten) |
| | `.ai/policy.md` (adjusted as trust grows) |

If you find yourself editing `workflow.md` per-project, that's a signal
the protocol itself needs a change — make it here, in this repo, so
every project using it benefits.

## Repository structure

This repo's root is flat by design — no `.ai/` wrapper inside it.
Whatever you name the folder when you clone or submodule it (`.ai` is
the convention this workflow expects) becomes the prefix for every path
below:

```
README.md            ← this file — also readable as .ai/README.md once installed
agents-snippet.md     ← paste into your project's own AGENTS.md
index.md · workflow.md · policy.md · state.md
structure.md · lifecycle.md · deviations.md · agents.md
skills/
├── workflow-constitution/
├── workflow-phase/
├── workflow-task/
├── workflow-implementation/
├── workflow-validation/
├── workflow-review/
└── workflow-context/
decisions/
├── _template.md
└── index.md
project-context/
└── structure.md   ← starter; filled in per-project, kept live by agents
```

Every link between these files is relative (`workflow.md`,
`../../agents.md`, etc.) — none of them hardcode `.ai/`, so this whole
tree is portable to any folder name or nesting depth without touching a
single link. Full layout and link conventions: [`structure.md`](structure.md).

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
workflow assumes stateless agents (§2) — bootstrapping/constitution work
is naturally the most expensive single operation (one-time, front-loads
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
