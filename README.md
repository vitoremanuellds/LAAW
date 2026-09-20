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
task `done`, and commits the context. Each task's status lives in one row — roots in
`.ai/tasks/index.md`, subtasks in the parent's `Subtasks:` table — and every status flip has
exactly one writer skill (`workflow.md` §2).

## Directory structure

```text
.ai/
  workflow/            ← this repo's content, installed by sync-workflow.py; never hand-edit
    workflow.md        ← the whole workflow, self-contained
    skills/            ← one SKILL.md per operation (6 skills)
    templates/         ← task-template.md, context-file-template.md
    tools/             ← sync-workflow.py, sync-skills.py
  tasks/               ← local working files, gitignored (.ai/tasks/.gitignore contains *)
    index.md           ← | id | name | status | — root rows only
    t1_add-login.md            ← leaf task: flat file
    t2_auth-flow/              ← super-task: folder
      task.md                  ← parent; Subtasks table holds child status rows
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
| `route` | Entry point: reads the task index, picks the active root task, asks the pending approval or hands off to exactly one skill |
| `bootstrap` | One-time scaffold of `.ai/tasks/` and `.ai/context/`; triggers `setup-project` when context is empty |
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
This project uses LAAW. Before acting, every session:
- `.ai/tasks/index.md` exists → read [.ai/workflow/workflow.md](.ai/workflow/workflow.md)
  and run [.ai/workflow/skills/route/SKILL.md](.ai/workflow/skills/route/SKILL.md).
- It doesn't exist → unbootstrapped: run the route skill with "bootstrap".
Do this fresh each session, not from memory of a previous read.
```

## House rules (short version)

- **Approvals are human messages only.** The agent never asks and answers in
  the same response; every question names the task ID and the artifact.
- **One task at a time**, lowest-ID non-done root first (`workflow.md` §7).
- **Status has one writer per transition** — see the table in `workflow.md` §2.
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
  task-template.md
  context-file-template.md
tools/
  sync-workflow.py             ← installs/re-syncs .ai/workflow/ into a project
  sync-skills.py               ← optional mirror into .agents/skills/
```
