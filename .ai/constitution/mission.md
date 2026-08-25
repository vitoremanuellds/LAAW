# Mission

## What

Local Model Agent Workflow is a file-based methodology for developing
software with AI coding agents. Project knowledge is persisted as
small, linked Markdown files (constitution → context → decisions →
phases → tasks) instead of being reconstructed in-context every
session. An agent starts at the smallest file that defines its current
task and follows links only as far as it needs to.

The methodology itself (`workflow.md`, `templates/`, `skills/`) is
distributed as a git submodule mounted at `.ai/workflow/` inside a
consuming project. Everything a project generates while using it
(`info.md`, `constitution/`, `context/`, `phases/`, `tasks/`,
`decisions/`) lives outside the submodule, in the consuming project's
own repo.

This project (`local-model-agent-workflow`) is that submodule's source
— and, reflexively, is now also bootstrapped with its own methodology
(this `.ai/` tree) to plan and track its own development, with
`.ai/workflow/` mounted as a self-referential submodule pinned to a
prior commit of this same repo.

## Why

Built around the hardest constraints — small context windows (48k–64k
tokens), weaker instruction-following — so it holds up on local models
(7B–35B parameters); the same discipline pays off on frontier models
too, just with more slack. It exists to solve four problems that get
worse as models get smaller or context gets tighter:

1. **Hallucination** — agents inventing state, requirements, or status
   values instead of reading the recorded ones.
2. **Wasted context** — agents reconstructing information every
   session that could have been written down once.
3. **Loss of human control** — agents advancing past points a human
   should have reviewed first.
4. **Unsafe parallel work** — multiple agents/humans stepping on the
   same artifact or losing track of what's actually in progress.

Two ideas do most of the work: (1) don't make agents reconstruct what
can be written down once — persist knowledge, not reasoning; (2)
separate *what* must happen (`workflow.md`, fixed, versioned) from
*who* is allowed to decide it (`info.md`, per-project, freely mutable)
— so trust in agents can grow without touching the process itself.

## Who

- **Vitor** (repo owner) — designs and maintains the methodology,
  field-tests it against local models, decides profile/process
  changes.
- **Consuming projects** — any project (human + AI agent team) that
  mounts this repo as `.ai/workflow/` and bootstraps one of the four
  profiles to manage its own development.
- **This repo itself** — now a consumer of its own methodology for its
  own development, via the self-referential submodule described above.

## Goals (current)

Driven by a stated need to make the workflow itself more efficient,
specifically:

- Reduce token/context overhead per skill invocation — every skill
  currently rereads `workflow.md` (or its profile's doc) in full on
  every operation; this was a deliberate fix for a past bug (a
  "compiled into this skill" summary silently omitted an edge case),
  but the full-reread cost is worth revisiting without reintroducing
  that failure mode.
- Reduce agent mistakes and retries — gate skips, wrong-skill
  invocations, invented status values — the failure modes already
  catalogued in README's Best Practices section.
- Make the bootstrap process and skill procedures more specific and
  less ambiguous.
- Be more specific about what each artifact (task file, phase file,
  ADR, etc.) must actually contain, so drafts need fewer correction
  rounds.

## Boundaries

- Never collapse the two-repo separation: fixed workflow content
  (this repo, mounted read-only at `.ai/workflow/`) vs. per-project
  generated content (everything else under `.ai/`). No agent writes
  inside `.ai/workflow/`.
- No shared "core rules" file across the four profiles — each
  profile's doc/skill-set stays self-contained. A prior attempt to
  thread profile conditionals through shared files was reverted
  (commits `72ad06c` / `4e00692`) specifically because it broke this.
- Any change to skill/file structure is a potential breaking change for
  every consuming project (this one included) — this repo doesn't yet
  publish tagged releases, so structural changes must be called out
  clearly enough that a pinned consumer can review them before moving
  its pin.
- Efficiency work must not sacrifice the correctness guarantees the
  current design paid for (e.g. the full-reread rule exists because a
  partial summary caused a real bug) — any reduction in what gets read
  needs to preserve completeness, not just cut length.
