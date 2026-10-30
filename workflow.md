# LAAW Workflow

Read this file at the start of every session. It is the reference for how the agent works in this project.

LAAW is not a project management solution — it is a workflow for the user to work with the agent. Tasks are done sequentially, not in parallel, by a single agent. The tasks folder is git-ignored for that reason, so tasks and IDs are unique per user. The workflow folder is also git-ignored: it is a copy of the LAAW checkout's `workflow.md`, which stays the source of truth. If you want parallel agents, give each agent its own git worktree and bootstrap the project in each one.

## Principles

1. **Plan before code.** Every task gets a plan file; a human approves it before any implementation starts.
2. **Human gates.** The human approves the plan, then the implementation, then the propagated context. Never skip a gate.
3. **Deviations are recorded.** Anything that deviates from the approved plan is noted in the task folder's `notes.md`.
4. **Context propagates.** After implementation, the information the task created is written back into the context files.
5. **Files stay small.** Any file inside `.ai/` larger than 1000 words is split into smaller files (roughly 1250 tokens). The entry point links unidirectionally to its children; children do not link back. This rule applies only to files inside `.ai/`, not to project code, and does not apply to `workflow/workflow.md` itself — it is the session entry point and is always read in full.

## Layout

All agent-generated files live in `.ai/`:

```
.ai/
├── workflow/workflow.md    # this file
├── context/
│   ├── _index.md           # context index
│   ├── _index_{N}.md       # index overflow (one file per split piece)
│   └── {name}.md           # context files, descriptive names
└── tasks/                  # task plans (git-ignored by default)
    ├── _tasks.md           # master task table (top-level tasks)
    ├── _tasks_{N}.md       # task table overflow
    └── t02_add-auth/       # task folder (simple and supertask alike)
        ├── task.md         # task plan
        ├── task_{name}.md  # plan attachments (one per split piece)
        ├── notes.md        # deviations and observations; required, initially empty
        ├── notes_{N}.md    # notes overflow
        ├── subtasks.md     # supertasks only: subtask table
        ├── staged.md       # supertasks only: staging for subtask context
        ├── staged_{name}.md # staged overflow
        └── t02.1_jwt-service/  # subtask folder
            ├── task.md
            ├── task_{name}.md
            ├── notes.md
            └── notes_{N}.md
```

## Task table (`.ai/tasks/_tasks.md`)

A markdown table with one row per **top-level** task (subtasks are listed in their supertask's `subtasks.md`):

| ID | Status | Name | Description | Type | Dependencies |
|---|---|---|---|---|---|
| t01 | done | Add login | Adds a login endpoint… | simple | — |
| t02 | in-progress | Add auth | Full authentication module… | supertask | — |

- IDs are sequential: next ID = `max(existing) + 1`.
- Description ≤ 180 characters.
- Type is `simple` or `supertask`.

### Statuses

Every task — simple task, supertask, or subtask — has a status. Subtasks keep their status in the supertask's `subtasks.md`, top-level tasks in `_tasks.md`:

| Status | Meaning |
|---|---|
| `not-planned` | only registered in the table, no plan file exists |
| `planning` | the plan file exists and is being iterated with the user |
| `in-progress` | the plan is approved and the agent is implementing |
| `propagating-context` | the implementation is approved and the agent is propagating the context |
| `cancelled` | the user abandoned the task; work stopped (terminal state) |
| `done` | fully complete (terminal state) |

A dependency is satisfied only when its status is `done`.

## Task folder files

Every task folder — simple task, supertask, or subtask — contains:

| File | When | Content |
|---|---|---|
| `task.md` | always | the plan: Title, Description, Context, In scope / Out of scope, Steps, Validations; for supertasks it also links `subtasks.md`, `notes.md`, and (once created) `staged.md` |
| `task_{name}.md` | when `task.md` outgrows 1000 words | plan attachments, one per split piece, linked from `task.md` |
| `notes.md` | always | deviations and relevant observations; required, initially empty |
| `notes_{N}.md` | when `notes.md` overflows | notes overflow, numbered |
| `subtasks.md` | supertasks only | the subtask table, like `_tasks.md` but for its subtasks |
| `staged.md` | supertasks, created on first subtask propagation | staging area for subtask context, appended to during propagation |
| `staged_{name}.md` | when `staged.md` overflows | staged overflow, descriptive names |

Subtask context does not live in the task file: it is staged in the supertask's `staged.md`.

## Context files (`.ai/context/`)

The project's wiki: architecture, mission, tech stack, modules, decisions. Descriptive filenames, no IDs.

`.ai/context/_index.md` is a table; the agent reads the index first, then only the relevant files:

| Name | Description | Status |
|---|---|---|
| project.md | Mission and tech stack | valid |
| auth-module.md | Auth module: JWT service… | valid |

Context files describe the project's current state, not its history: they never mention task IDs, task names, or task files. If `_index.md` outgrows 1000 words it overflows into `_index_{N}.md`, numbered.

Keeping context current is part of propagation: files a task changed are updated; files a task made obsolete are marked not valid in the index.

## Rules

- **Dependencies gate implementation.** Never implement a task whose dependencies are not `done`. If asked, refuse and name the unsatisfied dependencies.
- **Registering ≠ planning.** Registering a task = adding its row to `_tasks.md`. Planning = creating its folder. For simple tasks and supertasks, do both in one swoop. For subtasks, never: a subtask folder is only created when the user explicitly asks.
- **Approved plans are immutable.** After a plan is approved, the only mutable files in the task folder are `notes.md` (and, for supertasks, `subtasks.md`). `staged.md` is the staging file and is appended to during propagation. If a plan turns out to be unimplementable, the agent stops, notifies the user, and the user must re-plan the whole task with the agent (the status goes back to `planning`). When the re-planned task is approved again, the agent reports its dependent tasks so the user can check the new plan still satisfies them.
- **Cancellation never unblocks.** A cancelled dependency can never become `done`, so its dependents are blocked forever unless the user acts on them. The agent never cascades cancellation: it reports the dependent tasks and the user decides for each (cancel it too, re-plan it without the dependency, or replace the dependency with a new task). Dependencies live in the table's Dependencies column, which is the mutable state ledger — re-pointing a dependency is a table edit.
- **Git.** `laaw.py sync workflow` adds `.ai/tasks/` and `.ai/workflow/` to `.gitignore`. Only `.ai/context/` is committed.
- **Splitting.** Any `.ai/` file over 1000 words (≈1250 tokens) is split (except `workflow/workflow.md`, which is always read in full); the entry point links one-way to the children. Split pieces are named per the layout above: `_tasks_{N}.md` and `_index_{N}.md` are numbered; `task_{name}.md` and `staged_{name}.md` have descriptive names; `notes_{N}.md` is numbered. One file per split piece.
- **Simple vs supertask.** Hard signals force a supertask: the plan file would exceed 1000 words, or the work spans 2+ modules in `.ai/context/`. Size is a trigger, not a verdict: the sizing rule below fires a split proposal (vetoable at the plan gate). Neither signal covers files that legitimately stay and outgrow 1000 words (a supertask's `task.md`, subtask folders, `staged.md`, or a simple plan whose split proposal was vetoed): those are split per **Splitting**.
- **Sizing.** A task is sized to fit one 64k session — plan + implementation + propagation — and one honest review. Change size is measured in lines of code: a split proposal fires if **any** of: >200 lines of net change with tests and fixtures counted in full; >5 files; >5 independent design decisions (counted in the plan's Steps); a change touching a public API, persistence/migration, security, or wire format; a verification pass (tests, build) that plausibly needs more than one fix round. The estimate must name the concrete files the lines land in — an estimate without file names is not an estimate — and show the session budget: plan+context ≈5k tokens, reading ≈3× the changed lines, the edits, two test rounds ≈10–15k, buffer for the gate. A hard cap the user cannot veto: >300 lines of total diff including tests, or >3 distinct design decisions in flight at once — past that the review gate is a rubber-stamp. A split must leave every subtask ending in a state that passes its own validations — verification loops must not stack.

## Loops

### Simple task (also applies to each subtask)

```
1. PLAN
   User asks to plan. Agent registers the task in _tasks.md and creates the folder.
   Iterate with the user until the plan is approved.

2. IMPLEMENT
   User asks to implement.
   If any dependency is not completed → refuse, name the dependencies.
   Implement, iterating with the user until the implementation is approved.
   - User requests a change incompatible with the plan → note the deviation in notes.md.
   - Plan turns out unimplementable → stop, notify the user, note the deviation. The user re-plans the whole task (status back to `planning`).
   - User asks to abandon or cancel the task → mark it `cancelled` in _tasks.md (or the supertask's subtasks.md), stop the work, and scan _tasks.md and all supertask subtask tables for tasks that depend on it. Report them to the user — they will never unblock — and let the user decide for each: cancel it too, re-plan it without the dependency, or replace the dependency with a new task. Never cancel dependents automatically.

3. PROPAGATE CONTEXT
   Agent writes the task's information back:
   - subtask → the supertask's `staged.md`
   - simple task → the context files (create new, update existing, mark obsolete)
   User approves the propagated context.
```

### Supertask

```
1. PLAN the supertask: register in _tasks.md, create folder with task.md and subtasks.md.
   Iterate until approved.

2. For each subtask (in order):
   User explicitly asks to plan the subtask (default: one at a time; the user may
   ask to plan several or all in advance). Planning a subtask sets the
   supertask's row in _tasks.md to `in-progress` right away.
   Then run IMPLEMENT and PROPAGATE, with propagation going to the supertask's
   `staged.md`.

3. FINAL PROPAGATION:
   Move the `staged.md` content into the context files.
```

## Skills

Use the skills installed for this workflow:

- `plan-task` — register and plan a task, or plan a subtask of an existing supertask; decides simple vs supertask.
- `implement-task` — check dependencies, implement, record deviations, handle cancellation, run validations.
- `propagate-context` — write context back to the right place.
