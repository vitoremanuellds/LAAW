# Tech Stack

## Foundation

- **Content format**: Markdown with YAML front matter (skills only).
  No compiled artifacts, no build step. The entire product is text
  files read by AI agents and humans.
- **Distribution**: Git, via `git submodule` — this repo is mounted at
  `.ai/workflow/` inside consuming projects (including, reflexively,
  itself — see `mission.md`). Consumers pin to a specific commit/tag
  rather than floating on a branch, since this repo doesn't yet
  publish tagged releases.
- **Tooling**: One shell script, `sync-skills.sh`, which mirrors
  `skills/` to `.agents/skills/` for harnesses that auto-discover
  skills from that convention rather than following `workflow.md`'s
  explicit lookup table. No other scripts, no package manager, no
  dependency tree.
- **Runtime / consumers**: Any AI coding agent harness that can read
  files, follow a skill-lookup table, and (ideally) invoke skills by
  name — field-tested against Claude Code and local models served
  through an OpenAI-compatible endpoint (e.g. Ollama), including
  small quantized models in the 7B–35B range with 48k–64k context
  windows. That combination — small model, tight context, weak
  instruction-following — is the design's hard case; frontier models
  are expected to work at least as well with more slack.

## Constraints

- Everything must remain legible to a small local model reading it
  cold: no assumed shared context beyond what a linked file states,
  no jargon without definition, file sizes targeted around ~2048
  tokens (`workflow.md §3`).
- No lateral shared-context files between parallel artifacts (phases,
  tasks) — see `workflow.md §4`. Anything that feels lateral belongs
  in `context/` instead.
- The four profiles (full/medium/lite/minimal) must each stay a fully
  self-contained document/skill-set — no shared "core rules" file, no
  per-profile conditionals inside a shared file (see `mission.md`
  boundaries).
- Cross-references inside `skills/` and the root docs use
  `.ai/workflow/`-anchored paths, never dot-relative ones — a past
  bug showed dot-relative links silently break once a file is mirrored
  to a different relative depth (`sync-skills.sh`'s copy into
  `.agents/skills/`).

## "Testing"

There is no test suite in the traditional sense. Validation is
field-testing: running the workflow against real project work with a
real model (local or frontier) and recording what actually failed —
gate skips, wrong skill picked, ambiguous instructions — into
README's Best Practices section. That section is the closest thing
this repo has to a regression log, and changes that address a
documented failure mode should reference which one.
