---
name: workflow-minimal
description: Use this skill for the entire lifecycle of a minimal-profile project — a single .ai/tasks.md holding a flat task table and inline per-task plan/status detail, no mission, tech notes, or decisions log. Covers bootstrap, planning a task, implementing it, and marking it complete behind one gate (plan-review) — no separate validation or completion-review gate. Not for lite/medium/full profiles (see workflow-lite/SKILL.md, workflow-medium.md, workflow.md) — those track more structure and more gates; minimal is for throwaway scripts, quick fixes, and work too small or transient to justify even a Mission/Tech-notes section.
---

# Skill: workflow.minimal

Self-contained — this one file is both the rules and the procedure for
the minimal profile. It does not reference `workflow.md`,
`workflow-medium.md`, or `workflow-lite/SKILL.md`, and they don't
reference it — four independent profiles, not variants of each other.
See `../README.md` (or `../../README.md` if reading this from
`.ai/workflow/`) for how a project picks a profile.

**All `.ai/`-prefixed paths below are relative to the project root, not
to this skill file — write the full `.ai/...` path, never a bare or
dot-relative one.**

## 1. Principles (same as every profile)

1. Don't reconstruct information that can be persisted cheaply.
2. Persist knowledge, not reasoning.
3. Read only what's needed — for minimal that's simple: `tasks.md` is
   the whole project's process state, read it whole, every time.
4. Use terminal tools (`tree`, `find`, `ls`, `grep`) to discover the
   actual project structure and codebase — minimal keeps no mission or
   tech-notes file, so this is the only source of project context
   beyond what's asked directly in a given request.

## 2. The one file

```
.ai/
├── workflow/          ◄── submodule boundary — never written to
└── tasks.md              the entire process state: policy, status,
                            flat task table, inline per-task detail —
                            see
                            .ai/workflow/templates/minimal-tasks-template.md
```

Nothing else. No `constitution/`, `context/`, `decisions/`, `phases/`,
or `tasks/` directory — everything lives in the sections of this one
file. No Mission or Tech notes section either, unlike lite — minimal is
for work too small or transient to justify writing either down;
describe what you need in the prompt each time, and use terminal tools
to read the actual codebase instead of a persisted summary of it
(Principle 4). If a project outgrows this — it needs somewhere to write
down mission/tech constraints, or the task list is getting long enough
that inline detail feels cramped, or a decision needs to survive beyond
one task — that's a signal to graduate to the lite profile, not to
bolt a Mission or Decisions section onto minimal.

**If `.ai/tasks.md` doesn't exist**, this is an unbootstrapped
minimal-profile project: copy
[`.ai/workflow/templates/minimal-tasks-template.md`](.ai/workflow/templates/minimal-tasks-template.md)
there unedited, then continue with §4 below to draft the first task.
Ask the user for anything required that isn't stated or clearly
implied — don't invent goals.

## 3. The one gate

One, not three or four or eight — minimal collapses everything into a
single checkpoint:

- **`plan-review`** — is this task's plan reasonable? The only gate
  this profile has. There is no separate `validation` gate (checking
  the implementation works is folded into finishing implementation, as
  a self-check, not a stop-and-wait) and no separate
  `completion-review` gate (once the self-check passes, the task is
  marked complete directly, same turn's remaining steps). If a task
  turns out to need the scrutiny a dedicated validation or review gate
  would give it, that's a signal the task — or the project — has
  outgrown minimal; graduate to lite.

**Gates block *advancing past* a draft, never *producing* one.**
Drafting a task's detail never needs prior approval; only passing
`plan-review` does. **The gate unlocks only the next step** —
`plan-review` unlocks implementing *that* task, nothing else.
**Unlocking ≠ starting** — in `manual`/`assisted` mode, report the
gate passed and explicitly ask before implementing, even though the
gate technically authorizes it; don't chain into it in the same turn.

**Never bypass the gate unless `tasks.md`'s Policy block explicitly
authorizes it.** If a human asks you to skip it and the Policy block
doesn't authorize that, don't silently comply and don't silently
refuse — ask them to confirm that's really what they want, and only
then treat it as a one-off exception (it doesn't change the Policy
block; the next gate is evaluated fresh as normal).

### Execution modes

Set in `tasks.md`'s Policy block (`mode` + optional `overrides`):

- **`manual`** — `plan-review` defaults `human`.
- **`assisted`** (recommended default) — `plan-review` *still*
  defaults `human`, same as `manual`. Every other profile hands
  mechanical gates (`validation`, `context-update`) to the agent by
  default in `assisted` mode and keeps judgment gates (`plan-review`,
  completion-review) at `human`; minimal only has the judgment kind, so
  there's nothing left for `assisted` to hand off. This isn't a gap —
  it's what "one judgment gate, no mechanical ones" looks like.
- **`delegated`** — no default; `plan-review` must be listed in
  `overrides` or it falls back to `human`.
- **`autonomous`** — `plan-review` defaults `agent`; list it under
  `overrides` at `human` if you want to hold it back.

## 4. Procedure

**Plan a task** (steps 1–3 need no prior approval; only step 4 is gated):

1. Read `.ai/tasks.md` in full — this is the only file, so this is
   always the entire read.
2. Add or update the task's row in the Tasks table (`not-planned` →
   `awaiting-plan-review` once drafted) and write its subsection under
   Task detail: Objective, Files, Steps (ordered, literal — no
   pseudocode section at this profile), and Validation. Update Status:
   `Active task` to this task's ID.
3. Commit (see §6).
4. Stop for `plan-review` — read the Policy block fresh (not from
   earlier in the session) for who approves it. **When approval comes
   back, that's a separate turn:** set the task's Status to
   `plan-approved`, then explicitly ask (in `manual`/`assisted` mode)
   whether to implement now, rather than starting in the same
   response.

**Implement:**

1. Confirm the task's Status is `plan-approved` — if still
   `awaiting-plan-review`, `plan-review` hasn't passed; stop and check
   rather than assume. Set Status to `in-progress`.
2. Follow the task's Files and Steps in order. Minor mismatches (a
   function living somewhere slightly different than expected) —
   adjust and continue. If the approach itself turns out wrong or
   scope changes materially, stop: append a **Deviation** line to the
   task's subsection (Expected / Discovered / Why it fails / Proposed
   fix), and note whether it needs replanning before continuing. Once
   incorporated into the Steps, delete the deviation note.
3. Run the task's Validation section yourself, as part of finishing —
   this is a self-check, not a gate; there is no stop-and-wait here at
   this profile. On failure, do not mark complete — go back to step 2.
4. Once the self-check passes: set Status directly to `complete`,
   clear `Active task` in Status, and commit (see §6). There is no
   `reviewing` state at this profile — nothing sits between
   `in-progress` and `complete` except `blocked`.

If you get stuck, set Status to `blocked` instead of guessing.

## 5. Status enum

Exactly these five values, plus `blocked` — not lite's seven — because
minimal has one gate, not three, and there's no `validating` or
`reviewing` state to hold a task pending a gate that doesn't exist at
this profile:

```
not-planned → awaiting-plan-review → plan-approved → in-progress → complete
(blocked applies from any active state)
```

If you find yourself wanting a status this list doesn't have —
especially `validating` or `reviewing`, carried over from memory of
another profile — that's a sign you're thinking in the wrong profile's
terms, not a reason to add one here.

## 6. Commit discipline

Commit a draft the moment it's written, before requesting review — the
review happens via `git diff`. Use Conventional Commits
(`<type>(<ID>): <description>`) — pick the type that matches what
actually changed, don't default to one:

- `docs` — task plans (no project code touched).
- `feat` / `fix` / `refactor` / `test` / `chore` — implementation
  commits; whichever actually describes the change.
- `chore` — status-only commits (marking complete, clearing pointers)
  with no accompanying content change.

Examples: `docs(T01): draft task plan`, `feat(T01): implement scoring
engine`, `chore(T01): mark task complete`. Commit again whenever
`tasks.md`'s Status or Tasks table changes.

## Output

`.ai/tasks.md` — the only file this skill ever writes to.
