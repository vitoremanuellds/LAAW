# Project: {name}

Copy this to `.ai/project.md` in your project and edit — this is the
**only** protocol file a lite-profile project has. Read it fresh at
the start of every operation; it can change between sessions and a
stale read is what causes a gate to get silently ignored. Full rules:
[`.ai/workflow/skills/workflow-lite/SKILL.md`](.ai/workflow/skills/workflow-lite/SKILL.md).

```yaml
profile: lite
mode: assisted   # manual | assisted | delegated | autonomous

overrides:
  # Only needed for exceptions to your mode's default — see
  # .ai/workflow/skills/workflow-lite/SKILL.md for what each mode
  # defaults to. In delegated mode this list *is* your actual policy.
```

## Status

```
Active task: —
Blocked: none
```

## Mission

<!-- 1-2 sentences: what this project is, who it's for. -->

## Tech notes

<!-- Brief: language/framework/runtime, only what actually constrains
     how tasks get implemented. -->

## Tasks

| ID | Title | Status |
|---|---|---|
<!-- T01 | Scaffold project | not-planned -->

Status enum: `not-planned → awaiting-plan-review → plan-approved →
in-progress → validating → reviewing → complete` (`blocked` from any
active state).

## Task detail

<!-- One subsection per task, written when that task is actually
     planned — not predrafted for the whole table above.

### T01 — {title}

**Objective:** one or two sentences.

**Files:** explicit paths, one line each, modify vs. create.

**Steps:** ordered, literal actions.

**Validation:** how to check this task actually works.

**Deviation (if any):** Expected / Discovered / Why it fails /
Proposed fix — delete once resolved, the fix already lives in the
steps above once incorporated.
-->

## Decisions

<!-- Short bullet log, newest last, for anything a later task genuinely
     needs to know about ("chose SQLite over Postgres: single-user,
     no need for a server"). Not a history of what happened — only
     decisions future work depends on. -->
