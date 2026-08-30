# LAAW

**L**ocal **A**I **A**gents **W**orkflow.

A file-based workflow for developing software with AI coding agents.
Built around the hardest constraints — small context windows, weaker
instruction-following — so it holds up on local models (7B–35B,
48k–64k context); the same discipline pays off on frontier models too,
just with more slack to work with.

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

This repo contains **only** workflow content that never changes
per-project: `workflow.md`, `templates/`, `skills/`. It gets installed
into `.ai/workflow/` inside your project (via `sync-workflow.sh`, see
**Bootstrapping into a project** below) — one level *inside* your
project's `.ai/` folder, not the whole thing.

That's deliberate, not incidental. `constitution/`, `context/`,
`phases/`, `tasks/`, `decisions/`, and `info.md` all get written to
constantly by agents — if a re-sync's scope covered the whole `.ai/`
folder instead of just `.ai/workflow/`, there'd be no way to
distinguish "content that came from this repo and should be replaced
on update" from "content your own agents wrote and must never be
touched." Scoping installs to just `.ai/workflow/` means nothing an
agent writes ever lives where a re-sync could overwrite it — updates
stay clean *with respect to agent-generated content*, regardless of
which mechanism performs the install.

This repo's own internal structure can still change between versions
(it has, more than once) — files moving, renaming, or being merged.
`sync-workflow.sh`'s re-sync wholesale-replaces `.ai/workflow/`'s
content rather than patching it in place, so a structural change never
leaves an old, now-orphaned file sitting alongside the new layout —
but it also means there's no automatic "you're now on the latest
version" happening in the background; you only get a newer version by
explicitly re-running the script against a freshly pulled source. See
**Updating the workflow** below.

## Bootstrapping into a project

Clone this repo somewhere on disk, then run its `sync-workflow.sh`
against your project — this copies `workflow.md`, `skills/`,
`templates/`, `reference/`, and `README.md` into `.ai/workflow/`. No
`git submodule` command is involved.

```bash
git clone <this-repo-url> /path/to/LAAW
cd your-project
/path/to/LAAW/sync-workflow.sh
```

`sync-workflow.sh` takes two independent, optional positional
arguments — `[source-dir] [target-root]` — each defaulting sensibly:
source to the script's own checkout location, target to the current
directory. Running it with no arguments from inside your project, as
above, is the normal case. If you're not `cd`-ed into your project
first, pass both explicitly instead (there's no way to give just the
target and skip the source positionally):

```bash
/path/to/LAAW/sync-workflow.sh /path/to/LAAW /path/to/your-project
```

Then, as regular files tracked by *your project's own repo* (not this
one):

1. **Wire up `AGENTS.md`.** Most projects already have one, or use it
   for other tools too. Paste this block in (create the file if it
   doesn't exist; add as a section if other instructions already live
   there):

   ```markdown
   ## Agent Workflow
   This project uses a structured, modular agent workflow — one
   process, with optional layers rather than a profile choice:
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

   That's enough — everything else (the skill lookup table, gates,
   directory structure) is discovered from `workflow.md`. This gets
   read at the start of every session automatically, but every skill
   *also* instructs reading `workflow.md` in full as part of its own
   procedure — a single session-start read turned out not to be
   reliable enough in practice across a long session (see Best
   Practices below). `.ai/info.md` needs rereading even more
   aggressively, since unlike `workflow.md` it can change mid-session.

2. **Bootstrap `info.md`, and whichever layers you want now.** Point
   an agent (or yourself) at
   `.ai/workflow/skills/create-constitution/SKILL.md` (mission +
   techstack content, plus `info.md`'s unconditional first-run
   bootstrap) or `.ai/workflow/skills/bootstrap/SKILL.md` (asks which
   of constitution/context/decisions/phases/workbench to set up now,
   each an empty scaffold except constitution, which gets the same
   interview either way).

   Until one of these runs, `.ai/info.md` doesn't genuinely exist yet —
   that's expected, not a sign anything's broken. This is the only step
   that can't be skipped — everything downstream assumes `.ai/info.md`
   exists. Defaults are safe/conservative (`mode: assisted`); edit the
   policy block afterward once you're ready to delegate any gates.
   Every other layer is optional and comes into existence the first
   time its own owning skill is actually used — see
   [`workflow.md §3`](workflow.md#3-directory-structure) and
   [`reference/scaffold-on-first-use.md`](reference/scaffold-on-first-use.md).

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
   `sync-workflow.sh` re-sync, or the mirrored copy silently drifts out
   of sync with the real one in `.ai/workflow/`. If you don't know
   whether your harness needs this, you probably don't — `workflow.md
   §2`'s own lookup table works without it.

Every status value lives in exactly one place, never `.ai/info.md`
(which holds Policy only): `.ai/phases/phases.md`'s Status column
(phase-level), a phase file's own task table (a phase-linked task), or
`.ai/tasks/tasks.md`'s Status column (an orphan task — one with no
phase parent). See
[`workflow.md §11`](workflow.md#11-status-the-permanent-record).

From there the normal loop is: plan a phase → get it reviewed → break
it into tasks → implement → validate → review → let context propagate
→ repeat ([`workflow.md §5`](workflow.md#5-lifecycle--gates)) — or, for
a task with no phase, skip straight to drafting it and implementing it
([`workflow.md §3`](workflow.md#3-directory-structure)/§4).

A phase enters `phases.md` as a title-only row (via `define-phase`'s
own "stubbing only" mode) before it has any detail — its actual
Context, In/Out of scope, Requirements, Plan, and Automatic/Manual
validations get drafted separately, by a later `define-phase`
invocation, sometimes in a later session entirely. If you already know
what that phase should cover, say so when the row is added rather than
waiting for the planning step — a session that ends in between can
lose anything that was only ever stated in conversation, not yet
captured in a file. Planning one phase at a time like this, rather
than the whole project
up front, is itself an intentional supported mode, not a workaround —
see
[`workflow.md §5`, "Starting without a plan"](workflow.md#5-lifecycle--gates).

## Updating the workflow

Re-running the same `sync-workflow.sh` invocation against your project
re-syncs `.ai/workflow/` to the source checkout's current `HEAD` —
wholesale-replacing its content, since nothing in there is ever
supposed to be hand-edited (see **This repo is only the fixed half**
above):

```bash
cd /path/to/LAAW && git pull
cd your-project
/path/to/LAAW/sync-workflow.sh
```

**Review what changed before adopting it, don't blindly re-sync to
whatever `HEAD` currently is:** this repo doesn't yet publish tagged
releases, so treat every commit as a potential breaking change, the
same way you'd review any dependency upgrade.

```bash
git -C /path/to/LAAW log --oneline -5   # find a commit you've actually reviewed
git -C /path/to/LAAW checkout <sha>     # pin your own separate clone there
```

Then point `sync-workflow.sh` at that pinned clone as its source
argument, instead of one floating on the default branch:

```bash
/path/to/LAAW/sync-workflow.sh /path/to/LAAW /path/to/your-project
```

Your project's own content (`info.md`, `constitution/`, `context/`,
`phases/`, `tasks/`, `decisions/`) is untouched by any of this — the
script never writes anywhere under `.ai/` besides `.ai/workflow/`
itself and the `.ai/workflow-version` stamp file it writes beside it.

## What's in this repo vs. what's in your project

| This repo (`.ai/workflow/`, installed by `sync-workflow.sh`, never edited per-project) | Your project (`.ai/`, regular files, edit freely) |
|---|---|
| `workflow.md` | `AGENTS.md` (has the snippet pasted in) |
| `reference/*` — occasional-need detail behind `workflow.md`'s core, one file per concept | |
| `templates/info-template.md`, `templates/context-template.md`, `templates/decisions-template.md`, `templates/adr-template.md` | `info.md` — bootstrapped from template, then yours |
| `skills/*` — mostly named `<verb>-<noun>` | `constitution/*` — mission.md, techstack.md; optional |
| `sync-skills.sh` | `context/*` — optional |
| `sync-workflow.sh` — the install/re-sync script itself | `phases/*` — `phases.md` index + one flat file per phase, own Context section embedded; optional |
| | `tasks/*` — one flat file per task (phase-linked or orphan), own Context section embedded; `tasks.md` indexes orphan tasks only; the one mandatory layer |
| | `decisions/*` — `decisions.md` bootstrapped from template, `adrNN-*.md` follow `templates/adr-template.md`; optional |

A third category, technically outside both sides: `.agents/skills/`, if
you use `sync-skills.sh` — it's a generated copy of `skills/`, not
source of truth for either repo. Don't edit it directly and don't treat
it as authoritative; re-run the script instead. Same status for
`.ai/workflow-version`, written by `sync-workflow.sh` as a sibling of
`.ai/workflow/` on every install/re-sync — it records which commit of
this repo is currently installed (source, commit SHA, date); it's
generated metadata, not something to hand-edit.

If you find yourself editing anything under `.ai/workflow/` per-project,
that's a signal the workflow itself needs a change — make it in this
repo instead, so every project using it benefits, and so the next
`sync-workflow.sh` re-sync doesn't just overwrite your edit.

## This repo's own structure

```
README.md
workflow.md                    ← the whole workflow, self-contained
sync-workflow.sh                 ← installs/re-syncs this repo into a target's .ai/workflow/
sync-skills.sh                   ← optional: mirrors skills/ to .agents/skills/
reference/                       ← occasional-need detail, one file per
│                                    concept, linked from workflow.md
├── directory-and-links.md          ← §3 detail: path/link-rule incident history, optional-layer list
├── scaffold-on-first-use.md        ← §3 detail: how an optional layer comes into existence, who owns it
└── status-and-info.md              ← §11 detail: set-by table, ID-order reasoning
templates/
├── info-template.md              ← copied to .ai/info.md on first run
├── context-template.md            ← copied to .ai/context/context.md on first use
├── decisions-template.md           ← copied to .ai/decisions/decisions.md on first use
├── workbench-readme-template.md     ← copied to .ai/workbench/README.md on first use
├── context-temp-template.md          ← build-context.assess's temp output
├── context-build-plan-template.md     ← build-context.plan's temp output
└── adr-template.md                  ← ADR format, copied into decisions/ per decision
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
*project's* own repo, not this one) you'll have, once each optional
layer actually comes into use (see
[`workflow.md §3`](workflow.md#3-directory-structure)):

```
.ai/
├── workflow/              ← this repo's content, installed/re-synced by sync-workflow.sh
├── workflow-version         ← generated by sync-workflow.sh: source, commit SHA, date of what's installed
├── info.md                  ← policy only: who's authorized for each gate
├── constitution/             ← optional: mission.md, techstack.md
├── context/                  ← optional
│   ├── context.md              ← entry point, table of everything else here
│   └── (however many files fit this project's actual architecture)
├── phases/                   ← optional
│   ├── phases.md                ← index: ID, Title, Depends on, Status
│   └── p01-name.md              ← one flat file per phase: own Context + In/Out of scope + Requirements + Plan + Automatic/Manual validations + task table
├── tasks/                     ← the one mandatory layer
│   ├── tasks.md                  ← index for orphan tasks only: ID, Title, Purpose, Depends on, Status
│   ├── p01-t01-name.md            ← phase-linked task: own Context + Implementation
│   └── t01-name.md                ← orphan task (no phase parent): own Context + Implementation
└── decisions/                 ← optional
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
section as more surfaces. The underlying lessons (reread fresh, name
things explicitly, one thread per unit of work) generalize beyond this
specific setup.

**Reasoning effort should match the gate, not stay uniform.** If your
harness lets you set a thinking/reasoning level per call (e.g. Ollama's
OpenAI-compatible endpoint), don't leave it at the same setting for
every skill:

- **High/medium** — `create-constitution`, `define-phase`,
  `define-task` (it now writes fairly detailed task files — files
  to touch, ordered steps, sometimes pseudocode — and that detail is
  only useful if it's actually correct), and any deviation or ADR
  decision. These are exactly the places ambiguity is real and a wrong
  call cascades into everything built on top.
- **Low** — `implement-task` and `validate-work`. The
  hard thinking already happened at planning time; execution should be
  close to mechanical (follow the steps, adjust minor mismatches,
  escalate real deviations rather than reasoning your way around them).
  This is also your most frequently invoked skill, so unnecessary
  reasoning tokens here compound fast across a phase. Reading more
  content (see below — this skill now rereads `workflow.md` in full,
  same as every other skill) isn't the same as needing more reasoning
  effort to use it correctly; low effort is still appropriate as long
  as the correct information is actually present at decision time,
  which was the thing that was missing, not reasoning depth.

Compare actual token usage and output quality before committing to a
split — it varies by model.

**Call the skill explicitly, don't rely on it self-navigating.** Even
though `workflow.md §2` names the skill-lookup table and instructs
opening the file, it's cheaper and more reliable to just say "use
define-task to plan this" than to phrase a request generically and
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
accumulating the full project history in one window. This isn't an
absolute rule, though: if the thread is already long, start a new one;
but if the thread is still small and the model is capable, it's fine
to try staying in the same thread rather than splitting reflexively.

**Watch for skills reading one step ahead of where they should.** A
model may read an adjacent skill (e.g. `define-phase` while still
doing constitution work) even when its own description says it requires
the prior step to exist first. Usually harmless — it doesn't act
prematurely, just previews — but if you see an agent *acting* on a
skill before its prerequisites are met, that's worth tightening the
skill descriptions to be more mutually exclusive.

**`info.md` never holds a status value — every status lives directly
in the table that owns it.** `.ai/phases/phases.md` (phase-level), a
phase file's own task table (a phase-linked task), or
`.ai/tasks/tasks.md` (an orphan task) — never `info.md`, which holds
Policy only. "What's happening right now" is answered by reading the
relevant table directly, not a separate pointer file.

**Keep the `.ai/workflow/` boundary clean.** Never let an agent write
inside `.ai/workflow/` — if a skill ever seems to want to (e.g.
"fixing" a typo in `workflow.md` mid-task), that's a signal to raise it
as feedback for this repo, not to patch it locally; a local patch will
just be overwritten by the next `sync-workflow.sh` re-sync and silently
diverge from what the rest of your team is running.

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

**"Compiled into this skill" is a claim that needs to actually be
true, not just asserted.** `implement-task` used to skip
rereading `workflow.md`, on the assumption that its rules were fully
summarized locally. They weren't — the skill only mentioned the status
values *it* transitions through, never stated the enum was closed, and
an agent invented a status value outside it as a result. The carve-out
is gone; every skill now rereads `workflow.md` in full, every time.
If you reintroduce a similar shortcut anywhere, verify the "compiled"
version is actually complete for edge cases, not just the common path
— a partial summary is more dangerous than no summary, since it looks
authoritative while quietly omitting the constraint that mattered.

**A relative link's correctness depends on every file that references
it staying at the depth it was designed for — including copies.**
`sync-skills.sh` mirrors skill files to `.agents/skills/`, a different
relative depth than their canonical location. Every dot-relative
cross-reference inside those skills was only correct at the canonical
depth; once mirrored, they silently resolved to the wrong files, which
is very likely what produced confused reasoning in an agent reading
the mirrored copy. Every skill's cross-references now use
`.ai/workflow/`-anchored paths instead, making them correct regardless
of which copy gets read. If you ever add another way for these files
to get copied or cached elsewhere, re-verify this — it's the kind of
bug that produces no error, just quietly wrong behavior.
