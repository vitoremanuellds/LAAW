# LAAW — Local AI Agents Workflow

A file-based workflow for developing software with AI coding agents, built
around the hardest constraints of local models: small context windows and
weaker instruction-following. The same discipline works on frontier models,
just with more slack.

One loop, three human approval gates:

```text
plan ──approve plan──▶ implement ──approve implementation──▶ propagate context ──approve context──▶ done
```

`workflow.md` is the source of truth for all rules. Skills hold step-by-step
instructions; when they disagree, `workflow.md` wins.

---

## The loop in one paragraph

`plan-task` turns a request into task file(s) with simple IDs (`t1`, `t2.1`)
and asks for plan approval. `implement-task` does the work — Steps for a
single task, subtasks walked in ID order for a super-task — runs validations,
and asks for implementation approval. `propagate-context` writes the task's
`Context updates` into `.ai/context/`, asks for context approval, marks the
task `done`, and commits the context. All task state (ids, names, statuses) lives in one file,
`.ai/tasks/state.json`, written only by the tasks CLI (`.ai/workflow/tools/tasks.py`), which
enforces the legal status transitions; every status flip also has exactly one writer skill
(`workflow.md` §2).

## Directory structure

```text
.ai/
  workflow/            ← this repo's content, installed by sync-workflow.py; never hand-edit
    workflow.md        ← the whole workflow, self-contained
    skills/            ← one SKILL.md per operation (6 skills)
    templates/         ← task-template.md, super-task-template.md, context-file-template.md
    tools/             ← tasks.py + laaw_tasks/, sync-workflow.py, sync-skills.py
  tasks/               ← local working files, gitignored (.ai/tasks/.gitignore contains *)
    state.json         ← single source of truth: ids, names, statuses, files (CLI-written)
    t1_add-login.md            ← leaf task: flat file
    t2_auth-flow/              ← super-task: folder
      task.md                  ← parent (content only; static Subtasks list)
      t2.1_login-form.md       ← child files, named by their own ID
  context/             ← committed project knowledge, one file per topic
    index.md           ← | file | one-line summary |
    project.md
    <topic>.md
```

Tasks are local working files and never enter git history. Context is
committed (by `propagate-context`, on approval).

## Skills

| Skill | Does |
|---|---|
| `route` | Entry point: runs `tasks.py next`, then asks the pending approval or hands off to exactly one skill |
| `bootstrap` | One-time scaffold of `.ai/tasks/` and `.ai/context/` via `tasks.py init`; triggers `setup-project` when context is empty |
| `setup-project` | One-time interview seeding `.ai/context/` (mission, stack/constraints, standing rules) behind approval |
| `plan-task` | The only skill that creates tasks: mints IDs, writes task file(s), adds `draft` rows, asks plan approval |
| `implement-task` | The only skill that modifies project files; runs validations; owns `in-progress` / `impl-review` / subtask `done` |
| `propagate-context` | Applies Context updates to `.ai/context/`; owns `ctx-review` and `done`; commits context |

## Bootstrap into a project

Clone this repo somewhere on disk, then run `sync-workflow.py` against your
project. No `git submodule` involved.

```bash
git clone <this-repo-url> /path/to/LAAW
cd your-project
/path/to/LAAW/tools/sync-workflow.py
```

Then point an agent at `.ai/workflow/skills/route/SKILL.md` and say
"bootstrap". Route hands off to `bootstrap`, which scaffolds the layout and
runs `setup-project` to seed context.

Optional: if your harness auto-discovers skills from `.agents/skills/`, run
`.ai/workflow/tools/sync-skills.py` (re-run after every re-sync). Otherwise
the lookup in `workflow.md` works without it.

Suggested `AGENTS.md` section:

```markdown
## Agent Workflow
This project uses LAAW. Before acting, every session, from the project root:
- `.ai/tasks/state.json` exists → read [.ai/workflow/workflow.md](.ai/workflow/workflow.md)
  and run [.ai/workflow/skills/route/SKILL.md](.ai/workflow/skills/route/SKILL.md).
- It doesn't exist → unbootstrapped: run the route skill with "bootstrap".
Do this fresh each session, not from memory of a previous read.
```

## House rules (short version)

- **Approvals are human messages only.** The agent never asks and answers in
  the same response; every question names the task ID and the artifact.
- **One task at a time** — `tasks.py next` works the lowest-ID non-done root; if several
  roots are live it lists them and the human chooses (§7).
- **State lives in `state.json`, written only by `tasks.py`** — never hand-edited; the CLI
  refuses any transition not in the table in `workflow.md` §2, and that table also says which
  skill may trigger each flip.
- **Markdown holds content, never status.** Task files carry Steps/Validations/Notes;
  statuses are read via `tasks.py status`.
- **A task has either Steps or subtasks, never both.** Super-tasks get
  per-subtask implementation approvals; the parent closes via its own context
  pass.
- **Context is small and factual**: one file per topic, edited in place,
  split past ~100 lines, changed only behind approval.
- **Keep `.ai/workflow/` clean.** If a skill seems to want to edit
  `workflow.md` mid-task, that's feedback for this repo — a local patch gets
  overwritten by the next sync.

## Updating the workflow

Re-running `sync-workflow.py` wholesale-replaces `.ai/workflow/` with the
source checkout's current state:

```bash
cd /path/to/LAAW && git pull
cd your-project
/path/to/LAAW/tools/sync-workflow.py
```

Review what changed before adopting it — this repo doesn't publish tagged
releases, so treat every commit as a potential breaking change (pin with
`git -C /path/to/LAAW checkout <sha>` if needed). Your project's own content
(`.ai/tasks/`, `.ai/context/`) is untouched.

## What's in this repo

```text
README.md
workflow.md                    ← the whole workflow, self-contained
skills/
  route/  bootstrap/  setup-project/  plan-task/  implement-task/  propagate-context/
templates/
  task-template.md             ← leaf/child scaffold
  super-task-template.md       ← super-task parent scaffold
  context-file-template.md
tools/
  tasks.py                     ← CLI entry point: single writer of .ai/tasks/state.json
  laaw_tasks/                  ← the implementation: state.py, scaffold.py, report.py,
                                 persistence.py, cli.py, errors.py
  tests/                       ← unittest suite (keeps the transition table in sync with
                                 workflow.md §2; NOT installed into projects)
  sync-workflow.py             ← installs/re-syncs .ai/workflow/ into a project (skips tests/)
  sync-skills.py               ← optional mirror into .agents/skills/
```
