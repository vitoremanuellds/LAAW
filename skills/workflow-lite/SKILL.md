---
name: workflow-lite
description: Use this skill for the entire lifecycle of a lite-profile project — a single .ai/project.md holding mission, tech notes, a flat task table, inline per-task detail, and a decisions log. Covers bootstrap, planning a task, implementing it, validating it, and marking it complete. Not for medium or full profiles (see workflow-medium.md / workflow.md) — those use separate constitution/context/decisions/tasks files and more gates; lite is for prototypes, small tools, and single-session work where that structure isn't worth the overhead.
---

# Skill: workflow.lite

Self-contained — this one file is both the rules and the procedure for
the lite profile. It does not reference `workflow.md` or
`workflow-medium.md`, and they don't reference it — three independent
profiles, not variants of each other. See `../README.md` (or
`../../README.md` if reading this from `.ai/workflow/`) for how a
project picks a profile.

**All `.ai/`-prefixed paths below are relative to the project root, not
to this skill file — write the full `.ai/...` path, never a bare or
dot-relative one.**

## 1. Principles (same as every profile)

1. Don't reconstruct information that can be persisted cheaply.
2. Persist knowledge, not reasoning.
3. Read only what's needed — for lite that's simple: `project.md` is
   the whole project, read it whole, every time.
4. Use terminal tools (`tree`, `find`, `ls`, `grep`) to discover the
   actual project structure — no separate structure map.

## 2. The one file

```
.ai/
├── workflow/          ◄── submodule boundary — never written to
└── project.md            the entire project: policy, status, mission,
                            tech notes, task table, inline task detail,
                            decisions log — see
                            .ai/workflow/templates/lite-project-template.md
```

Nothing else. No `constitution/`, `context/`, `decisions/`, `phases/`,
or `tasks/` directories — everything lives in the sections of this one
file. If a project outgrows this (multiple contributors need to work
genuinely in parallel, or the decision/ADR history is getting long
enough to need its own index), that's a signal to graduate to the
medium or full profile, not to start bolting extra files onto lite.

**If `.ai/project.md` doesn't exist**, this is an unbootstrapped
lite-profile project: copy
[`.ai/workflow/templates/lite-project-template.md`](.ai/workflow/templates/lite-project-template.md)
there unedited, then continue with §4 below to fill in Mission/Tech
notes and draft the first task. Ask the user for anything required
that isn't stated or clearly implied — don't invent goals.

## 3. Gates

Three, not eight or four — one dial-derived triad for the one level
this profile has:

- **`plan-review`** — covers both "is the mission/tech-notes section
  clear" (only matters the first time) and "is this task's plan
  reasonable" (every time a task's detail is drafted). One gate type,
  reused per task.
- **`validation`** — does the implementation satisfy the task's
  Validation section?
- **`completion-review`** — is it appropriate, coherent, consistent
  with the rest of the project? Distinct from validation — validation
  never edits to force a pass (return to implementation instead);
  review never silently fixes issues unless the Policy block
  explicitly grants implementation authority.

**Gates block *advancing past* a draft, never *producing* one.**
Drafting a task's detail never needs prior approval; only passing
`plan-review` does. **Each gate unlocks only the next step** —
`plan-review` unlocks implementing *that* task, nothing else.
**Unlocking ≠ starting** — in `manual`/`assisted` mode, report a gate
passed and explicitly ask before the next step, even though the gate
technically authorizes it; don't chain into it in the same turn.

### Execution modes

Set in `project.md`'s Policy block (`mode` + optional `overrides`):

- **`manual`** — all gates default `human`.
- **`assisted`** (recommended default) — `validation` defaults
  `agent`; rest `human`.
- **`delegated`** — no default; every gate must be listed in
  `overrides`, unlisted falls back to `human`.
- **`autonomous`** — all gates default `agent`; list any you want held
  back at `human`.

## 4. Procedure

**Plan a task** (steps 1–4 need no prior approval; only step 5 is gated):

1. Read `.ai/project.md` in full — this is the only file, so this is
   always the entire read.
2. If Mission/Tech notes are still empty (first task ever), fill them
   in from the user's stated goals — don't invent requirements.
3. Add or update the task's row in the Tasks table (`not-planned` →
   `awaiting-plan-review` once drafted) and write its subsection under
   Task detail: Objective, Files, Steps (ordered, literal — no
   pseudocode section at this profile; if the logic is non-trivial
   enough to want pseudocode, write more literal steps instead), and
   Validation.
4. Update Status: `Active task` to this task's ID.
5. Commit (see §6). Stop for `plan-review` — read the Policy block
   fresh (not from earlier in the session) for who approves it. **When
   approval comes back, that's a separate turn:** set the task's
   Status to `plan-approved`, then explicitly ask (in `manual`/
   `assisted` mode) whether to implement now, rather than starting in
   the same response.

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
   incorporated into the Steps, delete the deviation note — the fix
   should live in the plan, not as a separate permanent record.
3. If you make a decision worth remembering (a library choice, a
   non-obvious tradeoff), append one bullet to the Decisions section —
   don't write a history of what you did, only what future work needs
   to know.
4. Set Status to `validating` (or `blocked` if stuck).
5. Commit (see §6). Stop for `validation` — read the Policy block
   fresh for whether that's yours to self-certify.

**Validate:**

1. Read the task's Validation section.
2. Execute it (automated tests, manual checks, whatever it specifies).
3. Report pass/fail. On failure, do **not** edit implementation to
   force a pass — set Status back to `in-progress` and return to
   Implement.

**Review and complete:**

1. Set Status to `reviewing`.
2. Confirm the change matches the task's stated scope and Files list —
   flag anything done that wasn't planned or something required that's
   missing.
3. Check for unnecessary complexity relative to the Objective.
4. Check the Decisions log actually captures anything genuinely
   decided along the way that isn't there yet.
5. Report findings — approve, or changes requested. **Clean findings
   are not themselves approval** — stop and wait for an explicit yes
   even if nothing's wrong. If changes are requested, return to
   Implement; nothing to stop for until it comes back.
6. **When approval comes back, that's a separate turn:** set the
   task's Status to `complete`, clear `Active task` in Status, commit
   (see §6).

## 5. Status enum

Exactly these eight values, shared vocabulary with the other profiles
even though lite tracks them in one table instead of a permanent
record spread across multiple files:

```
not-planned → awaiting-plan-review → plan-approved → in-progress
  → validating → reviewing → complete
(blocked applies from any active state)
```

If you find yourself wanting a status this list doesn't have, that's a
sign you've misread the situation, not a reason to invent one.

## 6. Commit discipline

Commit a draft the moment it's written, before requesting review — the
review happens via `git diff`. Messages tied to IDs: `T01: task
planned`, `T01: implementation complete`, `T01: task complete`. Commit
again whenever `project.md`'s Status or Tasks table changes.

## Output

`.ai/project.md` — the only file this skill ever writes to.
