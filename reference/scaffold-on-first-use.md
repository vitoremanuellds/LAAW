# Scaffold on first use — detail

Referenced from [`../workflow.md §3`](../workflow.md#3-directory-structure).
Every layer but `.ai/tasks/` is optional, presence inferred from
whether its directory exists — nothing declares this in a config file.
This document states, once, how a layer comes into existence the first
time it's actually needed, so no skill repeats the mechanics in its
own prose.

## The convention

Before a skill writes its layer's first real content, it checks
whether that layer's directory already exists.

- **If it exists:** proceed normally — never re-scaffold, never
  overwrite an existing index file's content.
- **If it doesn't exist:** create the directory, plus that layer's
  starter index file (a table shaped `| ID | ... | Status |`, columns
  adapted per layer — see each layer's own skill for its exact
  columns), then proceed.

This is the only mechanism that brings a layer into existence — there
is no separate "enable this layer" step required first. A project can
reach any layer two ways: a human explicitly runs
[`bootstrap`](../skills/bootstrap/SKILL.md) and chooses it up front, or
an agent is simply asked to do work that layer's owning skill handles,
and that skill's own first-use check creates it on the spot. Both
paths converge on the same scaffold step — `bootstrap` doesn't own any
scaffolding logic itself, it just triggers each chosen layer's own
step early.

## Who owns which layer

| Layer | Directory | Starter file | Owning skill |
|---|---|---|---|
| Constitution | `.ai/constitution/` | `mission.md` + `techstack.md` (interviewed, not templated) | [`create-constitution`](../skills/create-constitution/SKILL.md) |
| Gate authority (not an optional layer — always scaffolded first, regardless of which layers a project uses) | `.ai/info.md` | copied from `templates/info-template.md` | [`create-constitution`](../skills/create-constitution/SKILL.md) |
| Phases | `.ai/phases/` | `phases.md` (empty table) | [`define-phase`](../skills/define-phase/SKILL.md) |
| Tasks (orphan only — phase-linked tasks need no scaffold beyond `.ai/tasks/` itself, which the first task of either kind creates) | `.ai/tasks/` | `tasks.md` (empty table, orphan tasks only) | [`define-task`](../skills/define-task/SKILL.md) |
| Context | `.ai/context/` | `context.md`, copied from `templates/context-template.md` | [`build-context`](../skills/build-context/SKILL.md) or [`propagate-context`](../skills/propagate-context/SKILL.md), whichever writes to it first |
| Decisions | `.ai/decisions/` | `decisions.md`, copied from `templates/decisions-template.md` | whichever skill writes the first-ever ADR — [`create-constitution`](../skills/create-constitution/SKILL.md), [`define-phase`](../skills/define-phase/SKILL.md), or [`implement-task`](../skills/implement-task/SKILL.md), per [`workflow.md §7`](../workflow.md#7-decisions-adrs)'s ownership rule |
| Workbench | `.ai/workbench/` | `README.md`, copied from `templates/workbench-readme-template.md` | whichever skill first writes into it — today, [`build-context`](../skills/build-context/SKILL.md)'s temp files |

Tasks are the one layer that's never optional — `.ai/tasks/` always
comes into existence with the project's first task, phase-linked or
orphan, via whichever of `define-task`'s two paths applies.
