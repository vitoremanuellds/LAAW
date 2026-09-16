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
  starter index file (a table shaped per the layer's needs — see each
  layer's own skill for its exact columns), then proceed.

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
| Gate authority | `.ai/info.md` | `templates/info-template.md` | [`create-constitution`](../skills/create-constitution/SKILL.md) |
| Context | `.ai/context/` | `templates/context-template.md` | [`build-context`](../skills/build-context/SKILL.md) / [`propagate-context`](../skills/propagate-context/SKILL.md) |
| Workbench | `.ai/workbench/` | `templates/workbench-readme-template.md` | first skill writing into it |

Gate authority is not an optional layer — it's always scaffolded first,
regardless of which optional layers a project uses.

Tasks always come into existence with the first task via
`define-task` (no scaffold needed beyond the `tasks/` directory itself).
