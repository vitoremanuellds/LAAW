# Local Model Agent Workflow

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

## Choosing a profile

Four profiles, same underlying ideas, different amounts of ceremony —
pick one **before** bootstrapping, since it decides which files and
skills the project uses from that point on. Each profile is a fully
separate, self-contained document (and skill set) — not a flag that
changes behavior inside a shared one:

| | Full | Medium | Lite | Minimal |
|---|---|---|---|---|
| Doc | [`workflow.md`](workflow.md) | [`workflow-medium.md`](workflow-medium.md) | [`skills/workflow-lite/SKILL.md`](skills/workflow-lite/SKILL.md) | [`skills/workflow-minimal/SKILL.md`](skills/workflow-minimal/SKILL.md) |
| Hierarchy | Project → Phase → Task | Project → Task | one file | one file, no mission/tech-notes |
| Gates | 8 | 4 | 3 | 1 |
| Good for | multi-phase projects, multi-agent/multi-human coordination, full audit trail | one project of moderate size, one primary agent + human, still wants ADRs/context but no phase grouping | prototypes, small tools, single-session work | throwaway scripts, quick fixes, work too small or transient to justify even a Mission/Tech-notes section |

Gate count isn't picked per profile — it falls out of hierarchy depth.
Every non-top level always carries the same plan-review / validate /
completion-review triad; the top level carries one bootstrap gate.
Full has three levels, medium two, lite one (context propagation folds
into completion-review once there's no phase layer to promote
through). Minimal has no bootstrap gate at all (no constitution to
review) and collapses its one level's triad down to plan-review
alone — validation and completion-review are folded into finishing
implementation as a self-check, not separate stop-and-wait gates. If a
minimal, lite, or medium project outgrows its structure, that's a
signal to graduate profiles, not to bolt extra files onto the smaller
one.

There is deliberately no shared "core rules" file between the four —
that would mean an extra mandatory read on every single operation, for
every profile, forever, with no context-thrift benefit. Each profile's
doc is meant to be read on its own, start to finish.

## This repo is only the fixed half

This repo contains **only** workflow content that never changes
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
workflow** below before you pull.

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
   This project uses a structured agent workflow, one of four
   independent profiles depending on what's already bootstrapped:
   - `.ai/info.md` exists → read its `profile:` field, then open and
     read in full — not "recall it exists," actually read it —
     [.ai/workflow/workflow.md](.ai/workflow/workflow.md) (full) or
     [.ai/workflow/workflow-medium.md](.ai/workflow/workflow-medium.md) (medium).
   - `.ai/project.md` exists (no `info.md`) → open and read in full
     [.ai/workflow/skills/workflow-lite/SKILL.md](.ai/workflow/skills/workflow-lite/SKILL.md) (lite).
   - `.ai/tasks.md` exists (no `info.md`, no `project.md`) → open and
     read in full
     [.ai/workflow/skills/workflow-minimal/SKILL.md](.ai/workflow/skills/workflow-minimal/SKILL.md) (minimal).
   - None of the three exist → unbootstrapped. Ask which profile
     before doing anything else, then bootstrap accordingly (see this
     repo's README, "Choosing a profile").

   Do this before acting, every session — not just once, and not from
   memory of a previous read. Gate-skip and scope-overstep bugs have
   consistently traced back to this step being skipped.
   ```

   That's enough — everything else (the skill lookup table, gates,
   directory structure) is discovered from the matched profile's own
   doc. This gets read at the start of every session automatically,
   but every skill *also* instructs reading its profile's doc in full
   as part of its own procedure — a single session-start read turned
   out not to be reliable enough in practice across a long session
   (see Best Practices below). `.ai/info.md`/`.ai/project.md` need
   rereading even more aggressively, since unlike the workflow doc
   they can change mid-session.

2. **Bootstrap the chosen profile.** Point an agent (or yourself) at
   the matching skill:
   - **Full** — `.ai/workflow/skills/create-constitution-full/SKILL.md`.
     Writes `.ai/constitution/mission.md`, `techstack.md`,
     `roadmap.md`, and bootstraps `.ai/info.md`,
     `.ai/context/context.md`, `.ai/decisions/decisions.md`.
   - **Medium** — `.ai/workflow/skills/create-constitution-medium/SKILL.md`.
     Same idea, `roadmap.md` is a flat task index instead of a phase
     list, and `.ai/info.md` comes from `medium-info-template.md`.
   - **Lite** — `.ai/workflow/skills/workflow-lite/SKILL.md`. Writes
     one file, `.ai/project.md`, from
     `lite-project-template.md` — no `info.md` at this profile.
   - **Minimal** — `.ai/workflow/skills/workflow-minimal/SKILL.md`.
     Writes one file, `.ai/tasks.md`, from
     `minimal-tasks-template.md` — no `info.md`, no mission/tech
     notes, at this profile.

   Until this runs, none of `.ai/info.md`, `.ai/project.md`, or
   `.ai/tasks.md` genuinely exists yet — that's expected, not a sign
   anything's broken. This is the only step that can't be skipped —
   everything downstream assumes the chosen profile's bootstrap file
   exists. Defaults are safe/conservative (`mode: assisted`); edit the
   policy block afterward once you're ready to delegate any gates.

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
   sync with the real one in `.ai/workflow/`. It mirrors every skill
   directory generically, so lite/medium skills come along
   automatically — nothing profile-specific to configure. If you don't
   know whether your harness needs this, you probably don't — each
   profile's own §2 lookup table works without it.

Below, "the fast pointer" refers to `.ai/info.md`'s Status section
(full/medium), `.ai/project.md`'s Status block (lite), or
`.ai/tasks.md`'s Status block (minimal) — IDs only, no status values,
updated by every skill as its first and last action. The permanent
record — every actual status value, not just what's active — lives in
`.ai/constitution/roadmap.md` (full: phase-level; medium: flat
task-level) or, for lite/minimal, the Tasks table in
`.ai/project.md`/`.ai/tasks.md` itself. See each profile's own doc
(full/medium §11) or skill file (lite/minimal) for how the two stay in
sync.

From there the normal loop is, for full: plan a phase → get it
reviewed → break it into tasks → implement → validate → review → let
context propagate → repeat
([`workflow.md §5`](workflow.md#5-lifecycle--gates)); for medium: plan
a task → implement → validate → review (context propagates in the same
step) → repeat
([`workflow-medium.md §5`](workflow-medium.md#5-lifecycle--gates)); for
lite, the same shape collapsed into one file
([`skills/workflow-lite/SKILL.md §4`](skills/workflow-lite/SKILL.md));
for minimal, plan a task → get it reviewed → implement it, running its
Validation section as a self-check while finishing rather than a
separate gate, then mark complete directly — no validate or
completion-review stop at all
([`skills/workflow-minimal/SKILL.md §4`](skills/workflow-minimal/SKILL.md)).

## Updating the workflow

**Pin to a commit or tag, don't float on the branch head:**

```bash
cd .ai/workflow
git log --oneline -5        # find a commit you've actually reviewed
cd ../..
git -C .ai/workflow checkout <sha-or-tag>
git add .ai/workflow
git commit -m "Pin workflow to <sha-or-tag>"
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
| `workflow.md` (full) · `workflow-medium.md` (medium) — lite and minimal have no separate root doc, see below | `AGENTS.md` (has the snippet pasted in) |
| `templates/info-template.md`, `templates/context-template.md`, `templates/decisions-template.md`, `templates/adr-template.md` (full) | `info.md` — bootstrapped from template, then yours (full/medium only) |
| `templates/medium-info-template.md` (medium) | `constitution/*`, `context/*` (full/medium) |
| `templates/lite-project-template.md` (lite) | `phases/*` — full only, one flat file per phase, own Context section embedded |
| `templates/minimal-tasks-template.md` (minimal) | `tasks/*` — full/medium, one flat file per task, own Context section embedded |
| `skills/*` — full/medium skills named `<verb>-<noun>` with a `-full`/`-medium` suffix only where a name collides across the two, `workflow-lite` (lite, the whole profile in one skill), `workflow-minimal` (minimal, the whole profile in one skill) | `decisions/*` — full/medium, `decisions.md` bootstrapped from template, `adrNN-*.md` follow `templates/adr-template.md` |
| `sync-skills.sh` | `project.md` — lite only, the entire project in one file |
| | `tasks.md` — minimal only, the entire process state in one file, no mission/tech-notes/decisions |

A third category, technically outside both sides: `.agents/skills/`, if
you use `sync-skills.sh` — it's a generated copy of `skills/`, not
source of truth for either repo. Don't edit it directly and don't treat
it as authoritative; re-run the script instead.

If you find yourself editing anything under `.ai/workflow/` per-project,
that's a signal the workflow itself needs a change — make it in this
repo instead, so every project using it benefits, and so
`git submodule update` doesn't just overwrite your edit next time.

## This repo's own structure

```
README.md
workflow.md                    ← full profile: the whole workflow, self-contained
workflow-medium.md               ← medium profile: same role, independent document
sync-skills.sh                   ← optional: mirrors skills/ to .agents/skills/
templates/
├── info-template.md              ← full: copied to .ai/info.md on first run
├── context-template.md            ← full/medium: copied to .ai/context/context.md on first run
├── decisions-template.md           ← full/medium: copied to .ai/decisions/decisions.md on first run
├── adr-template.md                  ← full/medium: ADR format, copied into decisions/ per decision
├── medium-info-template.md           ← medium: copied to .ai/info.md on first run
├── lite-project-template.md           ← lite: copied to .ai/project.md on first run
└── minimal-tasks-template.md           ← minimal: copied to .ai/tasks.md on first run
skills/
├── create-constitution-full/    ┐
├── define-phase/                │
├── define-task-full/            │  full
├── implement-task-full/         │
├── validate-work-full/          │
├── review-work-full/            │
├── propagate-context/           ┘
├── create-constitution-medium/  ┐
├── define-task-medium/          │
├── implement-task-medium/       │  medium
├── validate-work-medium/        │
├── review-work-medium/          ┘
├── workflow-lite/                  lite — the whole profile, one skill
└── workflow-minimal/               minimal — the whole profile, one skill
```

Once mounted at `.ai/workflow/` in a project, alongside it (in the
*project's* own repo, not this one) you'll have one of these three,
depending on the profile chosen at bootstrap — never a mix:

**Full:**
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

**Medium:**
```
.ai/
├── workflow/              ← this repo, as a submodule
├── info.md                  ← policy + status
├── constitution/               mission.md, techstack.md, roadmap.md (flat task index, no phases)
├── context/context.md            single file — no proliferation of context/*.md
├── decisions/
│   ├── decisions.md                index
│   └── adr01-name.md
└── tasks/
    └── t01-name.md                  flat, no phase prefix — own Context + Implementation, no pseudocode
```

**Lite:**
```
.ai/
├── workflow/              ← this repo, as a submodule
└── project.md                ← the entire project: policy, status, mission, tasks, decisions log
```

**Minimal:**
```
.ai/
├── workflow/              ← this repo, as a submodule
└── tasks.md                  ← the entire process state: policy, status,
                                 flat task table, inline per-task detail —
                                 no mission, tech notes, or decisions log
```

Every link inside this repo is relative and none hardcode `.ai/`, so it
stays correct regardless of what your project names the mount point —
though `.ai/workflow/` is the convention every skill and the `AGENTS.md`
snippet assumes. Full layout and link conventions, per profile:
[`workflow.md §3`](workflow.md#3-directory-structure) ·
[`workflow-medium.md §3`](workflow-medium.md#3-directory-structure) ·
[`skills/workflow-lite/SKILL.md §2`](skills/workflow-lite/SKILL.md) ·
[`skills/workflow-minimal/SKILL.md §2`](skills/workflow-minimal/SKILL.md).

## Best Practices

Learned from actually running this against a local model — update this
section as more surfaces. Written against the full profile, since
that's what's been field-tested — the underlying lessons (reread
fresh, name things explicitly, one thread per unit of work) apply the
same way to medium/lite/minimal's analogous skills, just with fewer of
them.

**Reasoning effort should match the gate, not stay uniform.** If your
harness lets you set a thinking/reasoning level per call (e.g. Ollama's
OpenAI-compatible endpoint), don't leave it at the same setting for
every skill:

- **High/medium** — `create-constitution-full`, `define-phase`,
  `define-task-full` (it now writes fairly detailed task files — files
  to touch, ordered steps, sometimes pseudocode — and that detail is
  only useful if it's actually correct), and any deviation or ADR
  decision. These are exactly the places ambiguity is real and a wrong
  call cascades into everything built on top.
- **Low** — `implement-task-full` and `validate-work-full`. The
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
define-task-full to plan this" than to phrase a request generically and
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
model may read an adjacent skill (e.g. `define-phase` while still
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

**"Compiled into this skill" is a claim that needs to actually be
true, not just asserted.** `implement-task-full` used to skip
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
