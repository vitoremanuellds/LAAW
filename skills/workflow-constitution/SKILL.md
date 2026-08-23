---
name: workflow-constitution
description: Use this skill to create or update a project's constitution (mission.md, techstack.md, roadmap.md — or a single project.md at profile lite) — the first operation on a new project; also bootstraps info.md, context/decisions on first run, and detects/inspects an existing codebase for brownfield onboarding. Not for phase or task planning — see workflow-phase/workflow-task.
---

# Skill: workflow.constitution

Operation for the **Constitution Agent**. Contract:
[.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts).

## When to use

Creating or updating the constitution — `.ai/constitution/mission.md`,
`techstack.md`, and `roadmap.md` at `profile: full`/`medium`, or the
single `.ai/project.md` at `lite` (see
[.ai/workflow/workflow.md §14](.ai/workflow/workflow.md#14-profiles)).
On a brand-new project, this is also what bootstraps `.ai/info.md`,
`.ai/decisions/decisions.md`, and (at `full` only) `.ai/context/context.md`,
plus inspects an existing codebase if one is already there (step 3).

## Inputs

- User-provided project information (interview, existing docs, stated
  goals) and, if the project already has code, the codebase itself
  (step 3).
- Existing constitution files, if updating.
- [`.ai/workflow/templates/info-template.md`](.ai/workflow/templates/info-template.md)
  and
  [`.ai/workflow/templates/decisions-template.md`](.ai/workflow/templates/decisions-template.md) — only
  read/used if the destinations don't exist yet. Also
  [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md)
  at `profile: full` only.

## Procedure

All paths below are `.ai/`-prefixed and relative to the project root —
not relative to this skill file. Steps 1–7 require no prior approval —
draft everything before stopping for anything. Only step 8 is gated.

1. Read existing constitution files if present — do not overwrite blind.
2. **First run only:** if `.ai/info.md` doesn't exist, ask the user
   which profile to bootstrap at (`lite`/`medium`/`full` — default
   `full` if they don't state one; see
   [.ai/workflow/workflow.md §14](.ai/workflow/workflow.md#14-profiles)
   for what each cuts) and copy
   [`.ai/workflow/templates/info-template.md`](.ai/workflow/templates/info-template.md)
   there, editing only the `profile:` line if it's not `full` — leave
   `mode:` at its template default (`assisted`); the human adjusts
   that later, not you. If `.ai/decisions/decisions.md` doesn't exist,
   copy [`.ai/workflow/templates/decisions-template.md`](.ai/workflow/templates/decisions-template.md) there
   unedited (every profile keeps Decisions/ADRs unchanged — §14). At
   `profile: full` only: if `.ai/context/context.md` doesn't exist,
   also copy
   [`.ai/workflow/templates/context-template.md`](.ai/workflow/templates/context-template.md)
   there unedited — at `medium`/`lite` this file is never created; §14's
   Context cut means cross-phase facts live inside `techstack.md` (or
   `project.md` at `lite`) instead, written in step 6 below. Never
   overwrite any of these if they already exist — a second
   constitution run (updating an existing project) skips this step
   entirely.
3. **Detect an existing codebase before asking the user anything else.**
   List the project root, ignoring `.ai/`, `.git/`, and trivial
   scaffolding (a short README, LICENSE, `.gitignore`). If you find a
   manifest file (`package.json`, `pyproject.toml`, `Cargo.toml`,
   `go.mod`, `pom.xml`, `requirements.txt`, `Gemfile`, `composer.json`,
   `*.csproj`, or equivalent), a source directory (`src/`, `lib/`,
   `app/`, `cmd/`, or similar), or any other tracked, non-trivial file
   outside `.ai/`, treat this as an existing ("brownfield") project. An
   empty/new project skips straight to step 4.

   If brownfield, inspect before interviewing:
   - Read manifest/dependency files for language(s), frameworks,
     runtime versions.
   - Use `tree`/`find`/`ls`/`grep` to map the real directory structure
     and locate entrypoints — enough to describe the foundation
     accurately, not an exhaustive read.
   - Read the existing `README.md` and any top-level docs for stated
     purpose or architecture.
   - Note existing infra/config (`Dockerfile`, CI configs,
     `.env.example`, IaC) relevant to `techstack.md`'s scope.

   This narrows step 4's interview — confirm what you found ("this
   looks like a Django + Postgres service — confirm?") rather than
   asking from scratch; still ask about anything inspection can't
   determine (mission, goals, boundaries, planned work). Inspection
   supplements the interview, it never replaces it. What you find here
   feeds a `## Current Architecture (snapshot)` subsection written in
   step 6 — **not** a synthetic roadmap history; see step 7's roadmap
   rule.
4. Ask the user for anything missing that's required to write mission,
   tech stack, or roadmap. Do not invent goals or constraints the user
   hasn't stated or clearly implied.
5. Write mission content: what/why/who/goals/boundaries. Keep it
   stable — it should rarely need to change. At `full`/`medium`: its
   own file, `.ai/constitution/mission.md`. At `lite`: the `## Mission`
   section of `.ai/project.md`.
6. Write tech-stack content: languages, frameworks, runtime, infra,
   constraints — the foundation, not per-task implementation choices.
   At `full`/`medium`: `.ai/constitution/techstack.md`. At `lite`: the
   `## Techstack` section of `.ai/project.md`. At `medium`/`lite`, this
   is also where the merged Context subsection lives — add a
   `## Context` subsection (under `techstack.md` at `medium`, nested
   under `project.md`'s Techstack section at `lite`) for any
   brownfield snapshot from step 3, and later for whatever
   `workflow-context` promotes there instead of a separate
   `context/` file (§14). At `full`, the brownfield snapshot instead
   goes to a new `.ai/context/architecture-snapshot.md`, indexed in
   `context/context.md` as `active`.
7. Write roadmap content — ordered work, one-line description each,
   and a **Status** column (this is the permanent record; see
   [.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)).
   At `full`/`medium`: `.ai/constitution/roadmap.md`, rows are
   **phases**, all `not-planned` initially — no per-phase files here,
   phase detail lives in each phase's own `.ai/phases/p{NN}-{name}.md`
   once planned. At `lite`: the `## Roadmap` section of `.ai/project.md`,
   rows are **tasks** directly (flat `T{NN}` IDs, no phase grouping —
   §14) — `workflow-task` fills in each row's inline detail later, this
   step only stubs titles.

   **Roadmap rule, every profile, no exceptions:** regardless of how
   much existing code was found in step 3, the roadmap starts with
   zero entries documenting past or already-built work. Never invent
   synthetic "already complete" phases or tasks to retroactively cover
   history this protocol never tracked. It contains only work that is
   future or genuinely in-flight from this point forward, each at its
   real current Status — `not-planned` for anything not yet started,
   `in-progress` only if the user explicitly states work is actively
   underway right now, never `complete` for pre-existing work.
8. Commit the draft (see
   [.ai/workflow/workflow.md §13](.ai/workflow/workflow.md#13-commit-discipline)) —
   include `.ai/info.md`/`.ai/context/context.md`/
   `.ai/decisions/decisions.md` in this same commit if you just
   created them. Stop. Constitution review is a gate at every profile
   — see `.ai/info.md` (read fresh, not from memory) for who approves
   it. Do not proceed to phase or task planning yourself unless
   authorized. **When approval comes back, that's a separate turn:**
   in `manual`/`assisted` mode, report the approval and explicitly ask
   whether to start planning now (phase planning at `full`/`medium`,
   task planning directly at `lite` — `workflow-phase` isn't invoked
   there, §14), rather than starting it in the same response (see
   [.ai/workflow/workflow.md §5](.ai/workflow/workflow.md#5-lifecycle--gates)).

## Output

At `full`: `.ai/constitution/mission.md`, `techstack.md`,
`roadmap.md` — always; `.ai/info.md`, `.ai/context/context.md`,
`.ai/decisions/decisions.md` — first run only.
At `medium`: same three constitution files, but `.ai/context/context.md`
is never created — always; `.ai/info.md`, `.ai/decisions/decisions.md`
— first run only.
At `lite`: `.ai/project.md` (Mission + Techstack[+Context] + Roadmap)
— always; `.ai/info.md`, `.ai/decisions/decisions.md` — first run
only.
