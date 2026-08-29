# Directory structure & link conventions — detail

Referenced from [`../workflow.md §3`](../workflow.md#3-directory-structure).
The rules themselves are already fully stated there — read this only
for the reasoning behind them, which isn't needed on every operation.

## Why every path must be `.ai/`-prefixed, never bare or dot-relative

This document is a reference for understanding the rules, not a
literal sequence of write-tool calls. When a **skill** instructs an
actual write/read, it spells out the full `.ai/`-prefixed path
explicitly and states this same rule again at the point of use — treat
any bare mention of `info.md`, `roadmap.md`, `phases/`, `tasks/`,
`context/`, `decisions/`, or `constitution/` in `workflow.md` itself,
or in a skill's prose, as shorthand, never as a literal path to hand a
write tool without resolving it against the project root first.

This distinction is not academic: a bare or dot-relative path handed
directly to a write tool resolves against the agent's working
directory, not against where any instruction was read from — that
mismatch has already caused a phase file to be created outside `.ai/`
in practice. If you're about to call a write tool with an `.ai/`-family
path, resolve it against the project root explicitly, every time —
don't assume the ambient working directory already matches.

## Why cross-references are `.ai/workflow/`-anchored, not dot-relative

Every skill's cross-references to `workflow.md`, sibling skills, and
templates use `.ai/workflow/`-anchored paths, not dot-relative ones —
this is a deliberate change from an earlier, purely-relative
convention, made after a mirrored skill copy (see `sync-skills.sh`)
demonstrated that dot-relative links silently break once a file is
copied somewhere other than its designed location. `sync-skills.sh`
mirrors skill files to `.agents/skills/`, a different relative depth
than their canonical location under `skills/` — every dot-relative
cross-reference inside those skills was only correct at the canonical
depth; once mirrored, they silently resolved to the wrong files, which
is very likely what produced confused reasoning in an agent reading
the mirrored copy.

`.ai/workflow/` is the fixed, documented mount point every skill and
the `AGENTS.md` snippet assumes — not arbitrary. Per-project artifact
references follow the same rule: always `.ai/`-prefixed, never bare or
dot-relative, so a write/read target never depends on resolving
"relative to what." If you ever add another way for skill files to get
copied or cached elsewhere, re-verify this holds — it's the kind of
bug that produces no error, just quietly wrong behavior.

## Why `.ai/workbench/` isn't part of the permanent record

Referenced from
[`../workflow.md §3`](../workflow.md#3-directory-structure).

Every other `.ai/` subdirectory is schema- or Status-tracked:
`context/` via `context.md`'s table, `phases/`/`tasks/` via their
Status columns, `decisions/` via `decisions.md`'s table.
`.ai/workbench/` deliberately isn't — it's freeform scratch space for
the human and agent working together: planning notes, scratch
questions and answers, prompt drafts, anything disposable that would
otherwise have nowhere sanctioned to live.

It stays git-tracked (committed, not gitignored) — a file placed there
is meant to be visible to a teammate or a later session, not purely
local scratch. But "read only what the current task needs"
(`workflow.md` §1) never includes `.ai/workbench/` content as an
implicit input: no skill treats anything under it as something it
depends on, unless a human explicitly points an agent at one specific
file in it for that turn. A skill that grows its own ephemeral output
(the way `build-context-full`'s `context.temp.md`/`build-plan.md` do)
can write into `.ai/workbench/` directly — this is the general
convention, not a `build-context-full`-specific carve-out.
