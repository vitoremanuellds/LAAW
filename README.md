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
   `workflow.md` (this repo) defines the process (constitution →
   phases → tasks → validation → review) and never changes.
   `policy.md` (your project, not this repo — see below) defines which
   gates a human must approve and which an agent may, and *that* can
   change freely as you trust the agents more, without touching the
   process itself.

Everything else — skills, agent contracts, deviation/decision rules,
context propagation — lives inside `workflow.md`, self-contained. See
[`workflow.md`](workflow.md) for all of it.

## This repo is only the fixed half

This repo contains **only** protocol content that never changes
per-project: `workflow.md`, `templates/decision-template.md`, `skills/`. It gets
installed as a git submodule mounted at `.ai/workflow/` inside your
project — one level *inside* your project's `.ai/` folder, not the
whole thing.

That's deliberate, not incidental. `constitution/`, `project-context/`,
`phases/`, `decisions/`, and `policy.md` all get written to constantly
by agents — if the whole `.ai/` folder were the submodule, every one of
those writes would leave the submodule dirty. You'd either be unable to
commit that work at all, or committing your project's actual
constitution/phases/decisions into the shared template's own history —
neither is right. And `git submodule update --remote` against a dirty
submodule ranges from "refuses to run" to "silently discards your
uncommitted work," depending on your git config. Scoping the submodule
to just `.ai/workflow/` means nothing ever writes inside it — updates
stay clean *with respect to agent-generated content*.

That doesn't make updates risk-free in general, though: this repo's
own internal structure can still change between versions (it has,
more than once, early on) — files moving, renaming, or being merged.
Floating on the default branch means every one of those changes lands
on you immediately, and a structural change can leave an
already-checked-out submodule referencing paths that no longer exist.
See **Updating the protocol** below before you pull.

## Bootstrapping into a project

```bash
cd your-project
git submodule add <this-repo-url> .ai/workflow
```

Then, as regular files tracked by *your project's own repo* (not this
one):

1. **Wire up `AGENTS.md`.** Most projects already have one, or use it
   for other tools too. Paste this block in (create the file if it
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

2. **Run the constitution skill.** Point an agent (or yourself) at
   `.ai/workflow/skills/workflow-constitution/SKILL.md`. Until this
   runs, `.ai/policy.md` genuinely doesn't exist yet — that's expected,
   not a sign anything's broken. On a brand-new project this single
   step writes `.ai/constitution/mission.md`, `techstack.md`,
   `roadmap.md` — *and* bootstraps `.ai/policy.md` and
   `.ai/decisions/index.md` from their templates automatically (safe
   conservative defaults; edit `policy.md` afterward once you're ready
   to delegate any gates). This is the only step that can't be
   skipped — everything downstream assumes it exists.

3. **Optional: sync skills to `.agents/skills/`.** If your harness
   auto-discovers skills from `.agents/skills/` rather than following
   `workflow.md`'s explicit lookup table, run:

   ```bash
   .ai/workflow/sync-skills.sh
   ```

   from your project root (if you get "permission denied," run
   `chmod +x .ai/workflow/sync-skills.sh` once — file permissions
   sometimes don't survive a download or the first checkout). This
   copies (not links) the skills there — re-run it after every
   `git submodule update`, or the mirrored copy silently drifts out of
   sync with the real one in `.ai/workflow/`. If you don't know
   whether your harness needs this, you probably don't —
   `workflow.md §2`'s lookup table works without it.

There's no state file to check or initialize — status lives in
`.ai/constitution/roadmap.md` (phase-level) and each phase's
`tasks/index.md` (task-level), both created as you go.

From there the normal loop is: plan a phase → get it reviewed → break
it into tasks → implement → validate → review → let context propagate
→ repeat. Full lifecycle: [`workflow.md §5`](workflow.md#5-lifecycle--gates).

## Updating the protocol

**Pin to a commit or tag, don't float on the branch head:**

```bash
cd .ai/workflow
git log --oneline -5        # find a commit you've actually reviewed
cd ../..
git -C .ai/workflow checkout <sha-or-tag>
git add .ai/workflow
git commit -m "Pin workflow protocol to <sha-or-tag>"
```

Review what changed before moving the pin — `git -C .ai/workflow log
<old-sha>..<new-sha>` — the same way you'd review any dependency
upgrade. This repo doesn't yet publish tagged releases; until it does,
treat every commit as a potential breaking change and pin explicitly
rather than trusting `--remote` to only ever pull safe updates.

**If a submodule update leaves things broken** (paths that used to
resolve don't anymore, `git status` shows the submodule in a strange
state): don't try to patch it in place.

```bash
git submodule deinit -f .ai/workflow
rm -rf .git/modules/.ai/workflow
git submodule add <this-repo-url> .ai/workflow
```

This re-adds it clean at whatever commit you point it to. Your
project's own content (`policy.md`, `constitution/`, `phases/`,
`decisions/`, `project-context/`) is untouched either way — it was
never inside the submodule to begin with.

## What's in this repo vs. what's in your project

| This repo (`.ai/workflow/`, submodule, never edited per-project) | Your project (`.ai/`, regular files, edit freely) |
|---|---|
| `workflow.md` | `AGENTS.md` (has the snippet pasted in) |
| `templates/decision-template.md`, `templates/policy-template.md`, `templates/decisions-index-template.md` | `policy.md` — bootstrapped from template, then yours |
| `skills/*` | `constitution/*`, `project-context/*`, `phases/*` |
| `sync-skills.sh` | `decisions/*` — `index.md` bootstrapped from template, `dNN-*.md` follow `templates/decision-template.md` |

A third category, technically outside both sides: `.agents/skills/`, if
you use `sync-skills.sh` — it's a generated copy of `skills/`, not
source of truth for either repo. Don't edit it directly and don't treat
it as authoritative; re-run the script instead.

If you find yourself editing anything under `.ai/workflow/` per-project,
that's a signal the protocol itself needs a change — make it in this
repo instead, so every project using it benefits, and so
`git submodule update` doesn't just overwrite your edit next time.

## This repo's own structure

```
README.md
workflow.md                    ← the whole protocol, self-contained
sync-skills.sh                   ← optional: mirrors skills/ to .agents/skills/
templates/
├── decision-template.md          ← ADR template, copied into your project's decisions/
├── policy-template.md             ← copied to .ai/policy.md on first run
└── decisions-index-template.md     ← copied to .ai/decisions/index.md on first run
skills/
├── workflow-constitution/
├── workflow-phase/
├── workflow-task/
├── workflow-implementation/
├── workflow-validation/
├── workflow-review/
└── workflow-context/
```

Once mounted at `.ai/workflow/` in a project, alongside it (in the
*project's* own repo, not this one) you'll have:

```
.ai/
├── workflow/              ← this repo, as a submodule
├── policy.md
├── constitution/
├── project-context/
├── phases/
└── decisions/
```

Every link inside this repo is relative and none hardcode `.ai/`, so it
stays correct regardless of what your project names the mount point —
though `.ai/workflow/` is the convention every skill and the `AGENTS.md`
snippet assumes. Full layout and link conventions:
[`workflow.md §3`](workflow.md#3-directory-structure).

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

**Keep the submodule boundary clean.** Never let an agent write inside
`.ai/workflow/` — if a skill ever seems to want to (e.g. "fixing" a typo
in `workflow.md` mid-task), that's a signal to raise it as feedback for
this repo, not to patch it locally; a local patch will just be
overwritten by the next `git submodule update` and silently diverge
from what the rest of your team is running.

**Smaller/weaker local models may need to be pointed at skill files
explicitly, every time, especially early in a session.** In testing
with a 9B-class quantized model, the single most common failure was the
model never actually opening the relevant `SKILL.md` at all — skipping
straight past a review gate, creating files a skill explicitly
forbids it from creating — while a larger model in the same setup
self-navigated the lookup table reliably. `workflow.md §2` now says
this as forcefully as prose can, but if you see a gate skipped or an
agent inventing its own procedure, the fastest fix is still just
telling it to open the specific skill file by path. Don't assume a
strengthened instruction alone has fully solved this for small models —
watch for it, especially on the first operation of a new session.

**Say which task you mean, especially after a replan.** Task IDs are
sequential and never reflect a reordering — if a phase gets replanned
mid-execution and a new task is inserted that logically comes first,
its ID will still be the highest number, not the lowest. "Implement the
first task" is genuinely ambiguous in that situation even though it
reads as precise; naming the task by ID or title avoids an agent
guessing wrong and building on top of the wrong plan.
