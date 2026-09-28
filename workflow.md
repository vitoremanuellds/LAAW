# LAAW Workflow

Read this file at the start of every session. It is the reference for how the agent works in this project. It is a condensed version of the full LAAW specification.

## Principles

1. **Plan before code.** Every task gets a plan file; a human approves it before any implementation starts.
2. **Human gates.** The human approves the plan, then the implementation, then the propagated context. Never skip a gate.
3. **Deviations are recorded.** Anything that deviates from the approved plan is noted in the task file's Notes section.
4. **Context propagates.** After implementation, the information the task created is written back into the context files.
5. **Files stay small.** Any file larger than 100 lines is split into smaller files. The entry point links unidirectionally to its children; children do not link back.

## Layout

All agent-generated files live in `.ai/`:

```
.ai/
├── workflow/workflow.md    # this file
├── tasks/                  # task plans (git-ignored by default)
│   ├── index.md            # master task index
│   ├── t01_add-login.md    # simple task
│   └── t02_add-auth/       # supertask folder
│       ├── task.md         # supertask plan
│       ├── t02.1_jwt-service.md
│       └── t02.2_user-model.md
└── context/                # project wiki (committed)
    ├── index.md            # context index
    ├── project.md
    └── auth-module.md
```

## Task index (`.ai/tasks/index.md`)

A markdown table with one row per **top-level** task (subtasks are listed inside their supertask's `task.md`):

| ID | Status | Name | Description | Type | Dependencies |
|---|---|---|---|---|---|
| t01 | done | Add login | Adds a login endpoint… | simple | — |
| t02 | in-progress | Add auth | Full authentication module… | supertask | — |

- IDs are sequential: next ID = `max(existing) + 1`.
- Description ≤ 180 characters.
- Type is `simple` or `supertask`.

### Statuses

Every task — simple task, supertask, or subtask — has a status. Subtasks keep their status in the supertask's subtask table, top-level tasks in the task index:

| Status | Meaning |
|---|---|
| `not-planned` | only registered in the index, no plan file exists |
| `planning` | the plan file exists and is being iterated with the user |
| `in-progress` | the plan is approved and the agent is implementing |
| `propagating-context` | the implementation is approved and the agent is propagating the context |
| `done` | fully complete (terminal state) |

A dependency is satisfied only when its status is `done`.

## Task file sections

Every task file (simple, supertask, or subtask) contains:

| Section | When | Content |
|---|---|---|
| Title | always | task name |
| Description | always | simple, more detailed than the index |
| Context | always | context files / info needed to implement |
| In scope / Out of scope | always | boundaries |
| Steps | always | what to do, may include pseudocode |
| Validations | always | how to verify; may include human-only checks |
| Subtask table | supertasks only | like the task index, for its subtasks |
| New info | supertasks only | staging area for subtask context |
| Notes | optional | deviations and relevant observations |

## Context files (`.ai/context/`)

The project's wiki: architecture, mission, tech stack, modules, decisions. Descriptive filenames, no IDs.

`.ai/context/index.md` is a table; the agent reads the index first, then only the relevant files:

| Name | Description | Status |
|---|---|---|
| project.md | Mission and tech stack | valid |
| auth-module.md | Auth module: JWT service… | valid |

Keeping context current is part of propagation: files a task changed are updated; files a task made obsolete are marked not valid in the index.

## Rules

- **Dependencies gate implementation.** Never implement a task whose dependencies are not `done`. If asked, refuse and name the unsatisfied dependencies.
- **Registering ≠ planning.** Registering a task = adding its index row. Planning = creating its file. For simple tasks and supertasks, do both in one swoop. For subtasks, never: a subtask file is only created when the user explicitly asks.
- **Splitting.** Files over 100 lines are split; the entry point links one-way to the children.

## Loops

### Simple task (also applies to each subtask)

```
1. PLAN
   User asks to plan. Agent registers the task in the index and creates the file.
   Iterate with the user until the plan is approved.

2. IMPLEMENT
   User asks to implement.
   If any dependency is not completed → refuse, name the dependencies.
   Implement, iterating with the user until the implementation is approved.
   - User requests a change incompatible with the plan → note the deviation in Notes.
   - Plan turns out unimplementable → notify the user, note the deviation.

3. PROPAGATE CONTEXT
   Agent writes the task's information back:
   - subtask → the supertask's task.md "New info" section
   - simple task → the context files (create new, update existing, mark obsolete)
   User approves the propagated context.
```

### Supertask

```
1. PLAN the supertask: register in index, create folder and task.md (with subtask table).
   Iterate until approved.

2. For each subtask (in order):
   User explicitly asks to plan the subtask (default: one at a time; the user may
   ask to plan several or all in advance).
   Then run IMPLEMENT and PROPAGATE, with propagation going to the supertask's
   "New info" section.

3. FINAL PROPAGATION:
   Move the "New info" content into the context files.
```

## Skills

Use the skills installed for this workflow:

- `plan-task` — register and plan a task; decides simple vs supertask.
- `implement-task` — check dependencies, implement, record deviations, run validations.
- `propagate-context` — write context back to the right place.
