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
[`.ai/workflow.md`](.ai/workflow.md) for the full protocol and
[`.ai/index.md`](.ai/index.md) to navigate the rest.

## Bootstrapping into a project

### Option A — copy the template

```bash
git clone <this-repo-url> agent-workflow-template
cp -r agent-workflow-template/.ai your-project/.ai
```

### Option B — git submodule (keeps the protocol updatable)

```bash
cd your-project
git submodule add <this-repo-url> .ai-workflow
cp -r .ai-workflow/.ai .
```

Either way, after copying:

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
→ repeat. Full lifecycle diagrams: [`.ai/lifecycle.md`](.ai/lifecycle.md).

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

```
agents-snippet.md   ← paste into your project's own AGENTS.md
.ai/
├── index.md · workflow.md · policy.md · state.md
├── structure.md · lifecycle.md · deviations.md · agents.md
├── skills/
│   ├── workflow-constitution/
│   ├── workflow-phase/
│   ├── workflow-task/
│   ├── workflow-validation/
│   ├── workflow-review/
│   └── workflow-context/
└── decisions/_template.md
```

Full layout and link conventions: [`.ai/structure.md`](.ai/structure.md).
