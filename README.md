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
   phases → tasks → validation → review) and never changes. `info.md`
   (your project, not this repo — see below) holds who's authorized
   for each gate and what's currently active, and *that* can change
   freely as you trust the agents more, without touching the process
   itself.

Everything else — skills, agent contracts, deviation/decision rules,
context propagation, the full gate list and what each execution mode
defaults to — lives inside `workflow.md`, self-contained. See
[`workflow.md`](workflow.md) for all of it.

## This repo is only the fixed half

This repo contains **only** protocol content that never changes
per-project: `workflow.md`, `templates/`, `skills/`. It gets installed
as a git submodule mounted at `.ai/workflow/` inside your project — one
level *inside* your project's `.ai/` folder, not the whole thing.

That's deliberate, not incidental. `constitution/`, `context/`,
`phases/`, `tasks/`, `decisions/`, and `info.md` all get written to
constantly by agents — if the whole `.ai/` folder were the submodule,
every one of those writes would leave the submodule dirty. You'd
either be unable to commit that work at all, or committing your
project's actual constitution/phases/decisions into the shared
template's own history — neither is right. And `git submodule update
--remote` against a dirty submodule ranges from "refuses to run" to
"silently discards your uncommitted work," depending on your git
config. Scoping the submodule to just `.ai/workflow/` means nothing
ever writes inside it — updates stay clean *with respect to
agent-generated content*.

That doesn't make updates risk-free in general, though: this repo's
own internal structure can still change between versions (it has, more
than once) — files moving, renaming, or being merged. Floating on the
default branch means every one of those changes lands on you
immediately, and a structural change can leave an already-checked-out
submodule referencing paths that no longer exist. See **Updating the
protocol** below before you pull.

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
   there, including the skill lookup table. Because this gets read at
   the start of every session automatically, no skill needs to
   separately instruct a `workflow.md` reread mid-session — only
   `.ai/info.md` (below) genuinely needs rereading, since it's the one
   file that changes while a session is running.

2. **Run the constitution skill.** Point an agent (or yourself) at
   `.ai/workflow/skills/workflow-constitution/SKILL.md`. Until this
   runs, `.ai/info.md` genuinely doesn't exist yet — that's expected,
   not a sign anything's broken. On a brand-new project this single
   step writes `.ai/constitution/mission.md`, `techstack.md`,
   `roadmap.md` — *and* bootstraps `.ai/info.md`,
   `.ai/context/context.md`, and `.ai/decisions/decisions.md` from
   their templates automatically (safe conservative defaults; edit
   `info.md` afterward once you're ready to delegate any gates). This
   is the only step that can't be skipped — everything downstream
   assumes it exists.

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

`.ai/info.md`'s Status section is the fast answer to "what's happening
right now" — IDs only, no status values, updated by every skill as its
first and last action. `.ai/constitution/roadmap.md` (phase-level) and
each phase file's embedded task table (task-level) are the slower
permanent record of every actual status value, not just what's active
— see
[`workflow.md §11`](workflow.md#11-status-the-fast-pointer-and-the-permanent-record)
for how the two stay in sync.

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
project's own content (`info.md`, `constitution/`, `context/`,
`phases/`, `tasks/`, `decisions/`) is untouched either way — it was
never inside the submodule to begin with.

## What's in this repo vs. what's in your project

| This repo (`.ai/workflow/`, submodule, never edited per-project) | Your project (`.ai/`, regular files, edit freely) |
|---|---|
| `workflow.md` | `AGENTS.md` (has the snippet pasted in) |
| `templates/info-template.md`, `templates/context-template.md`, `templates/decisions-template.md`, `templates/adr-template.md` | `info.md` — bootstrapped from template, then yours |
| `skills/*` | `constitution/*`, `context/*` |
| `sync-skills.sh` | `phases/*` — one flat file per phase, own Context section embedded |
| | `tasks/*` — one flat file per task, own Context section embedded |
| | `decisions/*` — `decisions.md` bootstrapped from template, `adrNN-*.md` follow `templates/adr-template.md` |

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
├── info-template.md              ← copied to .ai/info.md on first run
├── context-template.md            ← copied to .ai/context/context.md on first run
├── decisions-template.md           ← copied to .ai/decisions/decisions.md on first run
└── adr-template.md                  ← ADR format, copied into your project's decisions/ per decision
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
├── info.md                  ← policy + status, merged: who's authorized, what's active
├── constitution/
├── context/
│   ├── context.md              ← entry point, table of everything else here
│   └── (however many files fit this project's actual architecture)
├── phases/
│   └── p01-name.md              ← one flat file per phase: own Context + Requirements + Plan + Validations + task table
├── tasks/
│   └── p01-t01-name.md            ← one flat file per task: own Context + Implementation, no per-phase subfolder
└── decisions/
    ├── decisions.md                ← index: ID, Name, Description, Status, Relations
    └── adr01-name.md
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

- **High/medium** — `workflow-constitution`, `workflow-phase`,
  `workflow-task` (it now writes fairly detailed task files — files to
  touch, ordered steps, sometimes pseudocode — and that detail is only
  useful if it's actually correct), and any deviation or ADR decision.
  These are exactly the places ambiguity is real and a wrong call
  cascades into everything built on top.
- **Low** — `workflow-implementation` and `workflow-validation`. The
  hard thinking already happened at planning time; execution should be
  close to mechanical (follow the steps, adjust minor mismatches,
  escalate real deviations rather than reasoning your way around them).
  This is also your most frequently invoked skill, so unnecessary
  reasoning tokens here compound fast across a phase.

Compare actual token usage and output quality before committing to a
split — it varies by model.

**Call the skill explicitly, don't rely on it self-navigating.** Even
though `workflow.md §2` names the skill-lookup table and instructs
opening the file, it's cheaper and more reliable to just say "use
workflow-task to plan this" than to phrase a request generically and
hope it finds the right skill on its own. This has been the single
most common failure point in testing (see below) — a five-word prompt
addition avoids it entirely.

**Name the task or phase you mean, don't rely on "the first one" or
"the next one."** Same logic as above, extended to *which* artifact:
"implement P02-T03" beats "implement the next task," especially after
any replanning has happened (task IDs don't reorder — see the note
further down). Being explicit costs nothing and removes an entire
category of ambiguity.

**Be explicit about which operation you want, more generally.**
Constitution creation in particular tends to prompt for confirmation
before starting if asked generically ("plan the app") rather than
directly ("create the constitution"). Neither is wrong, but if you
want it to proceed without asking, say so — this is a prompting
choice, not a workflow gate (there is deliberately no "may I start"
gate, only review gates after a draft exists).

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

**`info.md`'s Status section is a fast pointer, not the full
picture — and it can only track one active item.** It answers "what's
happening right now" in one read, which is the point, but by design it
holds no status values (those live in `roadmap.md`/the phase file) and
doesn't (yet) support more than one active phase/task at a time. If
you're running genuinely parallel work across multiple agents, watch
for it getting overwritten by whichever agent finishes its update last
— that's a real limitation of the current single-pointer format, not a
bug to route around by ignoring the file.

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
watch for it, especially on the first operation of a new session. This
is the same reason the "call the skill explicitly" best practice above
exists — it's the same failure, addressed as a habit rather than a
one-off fix.

**Say which task you mean, especially after a replan.** Task IDs are
sequential and never reflect a reordering — if a phase gets replanned
mid-execution and a new task is inserted that logically comes first,
its ID will still be the highest number, not the lowest. "Implement the
first task" is genuinely ambiguous in that situation even though it
reads as precise; naming the task by ID or title avoids an agent
guessing wrong and building on top of the wrong plan.

**A gate's authority can be changed mid-session — read `info.md`
fresh at the moment of every gate check, not from memory.** This
caused a real bug: a gate's authority was changed in `info.md`
partway through a session, and a skill that had already read the old
value earlier kept acting on stale information. Every skill's
gate-check step now says to reread `info.md` fresh rather than trust
an earlier read — if you see a gate's behavior not match what you just
changed in `info.md`, this is the first thing to check.
