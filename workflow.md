# LAAW Workflow

Read this file at the start of every session. It is the reference for how the agent works in this project.

LAAW is not a project management solution — it is a workflow for the user to work with the agent. Tasks are done sequentially, not in parallel, by a single agent. The tasks folder is git-ignored for that reason, so tasks and IDs are unique per user. The workflow folder is also git-ignored: it is a copy of the LAAW checkout's `workflow.md`, which stays the source of truth. If you want parallel agents, give each agent its own git worktree and bootstrap the project in each one.

## Principles

1. **Plan before code.** Every task gets a plan file; a human approves it before any implementation starts.
2. **Human gates.** The human approves the plan, then the implementation, then the propagated context. Never skip a gate.
3. **Deviations are recorded.** Anything that deviates from the approved plan is noted in the task's notes (tag `deviation`).
4. **Context propagates.** After implementation, the information the task created is written back into the context files.
5. **Files stay small.** Any file inside `.ai/` larger than ~1500 words (≈2k tokens ≈ one read at the session's context budget) is split into smaller files; a file between the threshold and its next natural break is fine as long as it still reads in one pass. A split piece keeps a descriptive name chosen by the agent, in the same folder; the entry point links to its children one-way, which do not link back.
   - **Exceptions:** `workflow/workflow.md` itself — the session entry point, always read in full — and all project code outside `.ai/`.

## Invocation

The CLI is invoked as `laaw` when `bin/laaw` (bash) or `bin/laaw.ps1` (PowerShell) is on PATH; otherwise run `python -m laaw` with the LAAW checkout root on cwd or PYTHONPATH. Requires Python 3. All commands are non-interactive and fail loud: a refused action prints why and changes nothing.

## Layout

All agent-generated files live in `.ai/`:

```
.ai/
├── workflow/workflow.md    # this file
├── tasks/                  # task state (git-ignored by default)
│   ├── tasks.json          # source of truth (CLI-owned)
│   ├── tasks.md            # generated, readonly (top-level index)
│   ├── t01_add-login/      # simple task folder
│   │   ├── task.md         # model-owned plan
│   │   └── notes.md        # generated, readonly (+ notes_<n>.md overflow)
│   └── t02_add-auth/       # supertask folder
│       ├── task.md
│       ├── notes.md
│       ├── subtasks.md     # generated, readonly (subtask table)
│       └── t02.1_jwt-service/
│           ├── task.md
│           └── notes.md
└── context/                # project wiki (committed)
    ├── index.md
    ├── project.md
    └── auth-module.md
```

## State

Task state lives in `.ai/tasks/tasks.json` — the source of truth, written only by the CLI. The markdown tables are generated views, never hand-edited: `tasks.md` is the top-level index (simple + supertask tasks only) and `<supertask>/subtasks.md` is that supertask's subtask table; both use columns `ID | Status | Name | Description | Type | Dependencies`. Regenerate all generated files any time with `laaw task render`; the output is deterministic (no diff on re-run).

IDs are sequential: next top-level ID = `max(existing) + 1`; subtasks are `t{N}.{n}`. Folder names are `<id>_<kebab-name>`; a slug collision gets an auto-suffix.

### Statuses

Every task — simple task, supertask, or subtask — has a status, stored in state and transitioned only by the CLI:

| Status | Meaning |
|---|---|
| `not-planned` | registered in state, no plan file exists |
| `planning` | the plan file exists and is being iterated with the user |
| `in-progress` | the plan is approved and the agent is implementing |
| `propagating-context` | the implementation is approved and the agent is propagating the context |
| `cancelled` | the user abandoned the task; work stopped (terminal state) |
| `done` | fully complete (terminal state) |

A dependency is satisfied only when its status is `done`.

## Task files

Every task file (simple, supertask, or subtask) is a plan owned by the model, scaffolded by `laaw task plan` (section titles only). All task files have the same sections:

| Section | Content |
|---|---|
| Title | task name |
| Description | simple, more detailed than the index |
| Context | `.ai/context/` files, with paths; the implementer reads them before touching the codebase |
| In scope / Out of scope | boundaries |
| Steps | what to do, may include pseudocode |
| Validations | how to verify; may include human-only checks |

Notes are CLI-owned state, not part of `task.md`: `laaw task note <id> --tag <tag> --text "..."` appends a tagged note, rendered into the generated `notes.md` (tag-grouped, word-capped, auto-split into `notes_<n>.md`). A supertask's subtask context is staged as tagged notes on the supertask; there is no separate staging file.

## Context files (`.ai/context/`)

The project's wiki: architecture, mission, tech stack, modules, decisions. Descriptive filenames, no IDs.

`.ai/context/index.md` is a table; the agent reads the index first, then only the relevant files:

| Name | Description | Status |
|---|---|---|
| project.md | Mission and tech stack | valid |
| auth-module.md | Auth module: JWT service… | valid |

Context files describe the project's current state, not its history: they never mention task IDs, task names, or task files.

Keeping context current is part of propagation: files a task changed are updated; files a task made obsolete are marked not valid in the index.

## Rules

- **Dependencies gate implementation.** Never implement a task whose dependencies are not `done`; `laaw task implement` refuses and lists the unsatisfied deps.
- **Registering ≠ planning.** Registering a task = adding it to state (`laaw task register`). Planning = creating its plan file (`laaw task plan`). For simple tasks and supertasks, do both in one swoop. For subtasks, never on the agent's own initiative: a subtask file is only created when the user explicitly asks.
- **Approved plans are immutable.** After approval, the only mutable part of a task file is its Notes section (and, for supertasks, the subtask table in state). If a plan turns out to be unimplementable, the agent stops, notifies the user, and the user re-plans the whole task with the agent (`laaw task plan` again; status back to `planning`). When the re-planned task is approved again, the agent reports its dependent tasks so the user can check the new plan still satisfies them.
- **Cancellation never unblocks.** A cancelled dependency can never become `done`, so its dependents are blocked forever unless the user acts on them. The agent never cascades cancellation: it reports the dependent tasks (`laaw task dependents`) and the user decides for each (cancel it too, re-plan it without the dependency, or replace the dependency with a new task). Dependencies live in state; re-pointing one is `laaw task dep-add` / `dep-remove`.
- **Git.** `laaw sync workflow` adds `.ai/tasks/` and `.ai/workflow/` to `.gitignore`. Only `.ai/context/` is committed.
- **Splitting.** When a file must be split, each piece keeps a descriptive name chosen by the agent and lives in the same folder; the entry point links to its children one-way. The size threshold and its exceptions are Principle 5.
- **Simple vs supertask.** Hard signals force a supertask: the plan file exceeds the threshold of Principle 5, or the work spans 2+ modules in `.ai/context/`. Size is a trigger, not a verdict: the sizing rule below fires a split proposal (vetoable at the plan gate). A split must leave every subtask ending in a state that passes its own validations — verification loops must not stack.
- **Sizing.** A task is sized to fit one 64k session — plan + implementation + propagation — and one honest review. A split proposal fires if **any** of: >200 lines of net change with tests and fixtures counted in full; >5 files; >5 independent design decisions (counted in the plan's Steps); a change touching a public API, persistence/migration, security, or wire format; a verification pass that plausibly needs more than one fix round. The estimate must name the concrete files the lines land in and show the session budget: plan+context ≈5k tokens, reading ≈3× the changed lines, the edits, two test rounds ≈10–15k, buffer for the gate. A hard cap the user cannot veto: >300 lines of total diff including tests, or >3 distinct design decisions in flight at once — past that the review gate is a rubber-stamp.

## Loops

### Simple task (also applies to each subtask)

```
1. PLAN
   User asks to plan. Agent registers the task (`laaw task register`) and creates
   its plan file (`laaw task plan`). Iterate with the user until the plan is approved.

2. IMPLEMENT
   User asks to implement. `laaw task implement` refuses if any dependency is not
   done — refuse, name the dependencies. Implement, iterating with the user until
   the implementation is approved. Record a progress note after each Step
   (`laaw task note <id> --tag progress ...`). A note records what the
   implementation created as it happened — progress per step, deviations,
   decisions/gotchas worth keeping; notes are CLI-owned state rendered into
   `notes.md`, not prose appended to `task.md`.
   - User requests a change incompatible with the plan → note the deviation
     (`--tag deviation`).
   - Plan turns out unimplementable → stop, notify the user, note the deviation. The
     user re-plans the whole task (status back to `planning`).
   - User asks to abandon or cancel the task → `laaw task cancel`; it reports the
     dependent tasks — they will never unblock — and the user decides for each.
     Never cancel dependents automatically.

3. PROPAGATE CONTEXT
   `laaw task propagate`, then the agent writes the task's information back:
   - subtask → tagged notes on the supertask (`laaw task note <supertask-id> ...`)
   - simple task → the context files (create new, update existing, mark obsolete)
   User approves the propagated context. `laaw task done`.
```

### Supertask

```
1. PLAN the supertask: register in state, create folder and task.md (with subtask
   table in state). Iterate until approved.

2. For each subtask (in order):
   User explicitly asks to plan the subtask (default: one at a time; the user may
   ask to plan several or all in advance). Planning a subtask sets the
   supertask's status to `in-progress` right away.
   Then run IMPLEMENT and PROPAGATE, with propagation going to tagged notes on
   the supertask.

3. FINAL PROPAGATION:
   Move the supertask's staged note content into the context files.
```

## Skills

Use the skills installed for this workflow:

- `plan-task` — register and plan a task, or plan a subtask of an existing supertask; decides simple vs supertask.
- `implement-task` — check dependencies, implement, record deviations, handle cancellation, run validations.
- `propagate-context` — write context back to the right place.
