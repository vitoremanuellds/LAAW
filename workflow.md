# LAAW workflow

Source of truth for the loop, statuses, IDs, layout, and approvals. Skills hold step-by-step
instructions; this file holds the rules they must not contradict. If a skill and this file
disagree, this file wins — report the contradiction to the human instead of improvising.

## 1. The loop

```text
plan ──approve plan──▶ implement ──approve implementation──▶ propagate context ──approve context──▶ done
task        │            task                            │                                │
            ▼                                             ▼                                ▼
      (re-plan)                                      (fix & re-ask)                   (fix & re-ask)
```

One task at a time. Each gate is a human message answering a specific question; the agent never
asks and answers in the same response.

## 2. Statuses — single-writer table

All task state (ids, names, statuses, file paths) lives in ONE file: `.ai/tasks/state.json`.
It is written only by the tasks CLI (`python3 .ai/workflow/tools/tasks.py`) — never by hand,
never via a file-editing tool, no matter what. The CLI validates every `set-status` call
against the table below and refuses anything else, so the table is also the complete set of
legal status changes. `tools/test_tasks.py` keeps the CLI's table in sync with this one.
Which skill may trigger each transition:

| From | To | Only writer | Trigger |
|---|---|---|---|
| — | `draft` | plan-task | `tasks.py new` / `subtask` scaffolds the task(s) |
| `draft` | `in-progress` | implement-task | plan approved (root), or a subtask's turn comes |
| `impl-review` | `in-progress` | implement-task | implementation rejected → fix work |
| `in-progress` | `impl-review` | implement-task | Steps done, Validations run, Context updates filled |
| `impl-review` | `done` | implement-task | implementation approved (subtasks only) |
| `impl-review` | `ctx-review` | propagate-context | task with Steps: context changes written |
| `in-progress` | `ctx-review` | propagate-context | super-task: all subtasks `done`, parent Validations run, context changes written |
| `ctx-review` | `done` | propagate-context | context approved; `.ai/context/` committed |

Rules:
- **No markdown file holds a status.** Task files hold content (Description, Steps, Validations,
  Context updates, Notes); `tasks.py status` is the only place to read one.
- A task with Steps reaches `impl-review` and waits there for implementation approval.
- A super-task stays `in-progress` while its subtasks are worked; each subtask goes
  `draft → in-progress → impl-review → done` on its own. The parent then moves to the context gate.
- After any rejection, the fix work happens before the re-ask, and the status flips back first.
- A `done` task never changes status again; wrong work gets a new task via plan-task.

## 3. Approvals

- Human-only: an approval is a human message answering the specific question asked. Never ask
  and answer in the same response. Re-asking after edits is safe; approvals are not consumed.
- Every question names the task ID and points at the artifact being approved.
- The agent records each approval as its first action — a `tasks.py set-status` call — then
  continues in the same turn.

| Gate | Question asked | Recorded by |
|---|---|---|
| Plan | "Approve plan for tN?" (task file shown/linked) | implement-task: `set-status` `draft → in-progress` |
| Implementation | "Approve implementation of tN?" (diff summary + validation results shown) | subtask: implement-task sets `done`; task with Steps: propagate-context sets `ctx-review` |
| Context | "Approve context changes for tN?" (exact edits shown) | propagate-context: `set-status` `ctx-review → done` |

## 4. Layout and IDs

```text
.ai/
  workflow/            ← synced LAAW copy; never hand-edit
    workflow.md
    skills/<name>/SKILL.md
    templates/
    tools/             ← tasks.py lives here
  tasks/               ← local working files, gitignored
    state.json         ← single source of truth: ids, names, statuses, files
    t1_add-login.md            ← leaf task: flat file
    t2_auth-flow/              ← super-task: folder
      task.md                  ← parent file (content only)
      t2.1_login-form.md       ← child files, named by their own ID
      t2.2_session.md
  context/             ← committed project knowledge
    index.md           ← | file | one-line summary |
    project.md
    <topic>.md
```

- IDs, slugs, and filenames are minted by the tasks CLI: root `t{N}` (highest root + 1),
  child `t{N}.{k}` (highest child + 1). Files: leaf `t{N}_{slug}.md`; super-task folder
  `t{N}_{slug}/` with `task.md`; child `t{N}.{k}_{slug}.md`. Slugs are derived from names by
  the CLI. Agents never construct an ID, slug, or task filename.
- Shape follows content: a leaf task is one flat file; a super-task is a folder with `task.md`
  plus one child file per workstream.
- A task's shape is fixed at plan time; re-planning a draft may change it (`tasks.py rename`,
  `remove`, `new` — all refused once any status left `draft`).
- Tasks are local working files: `.ai/tasks/.gitignore` contains `*`. Context is committed.

The tasks CLI (run from the project root, or with `--root`):

```text
init                     create .ai/tasks/ (state.json, .gitignore) and .ai/context/ (index.md)
new <name> [--super] [--desc T]
subtask <root-id> <name> [--desc T]
rename <id> <new-name>   draft tasks only
remove <id>              draft tasks only
set-status <id> <status> validated against §2
status [id]              one task, or the board
next                     active task + exact next action/question
check                    state/file consistency report
```

## 5. Task files

One file per task, scaffolded from `templates/task-template.md` (leaf/child) or
`templates/super-task-template.md` (super-task parent) — scaffolding is done by
`tasks.py new` / `subtask`, which also registers the task in `state.json`:

```markdown
# tN — name

Description: …

Context: …            ← what the implementer must know; names the .ai/context/ files read at plan time

Steps:                ← leaf/child tasks only
- [ ] …

<!-- super-task parent instead of Steps:
Subtasks:             ← static list, added by plan-task; NO status column
- tN.1 (tN.1_login-form.md) — login form
- tN.2 (tN.2_session.md) — session store
-->

Validations:          ← commands/checks proving the work is done
- …

Context updates:      ← exact changes to make in .ai/context/ when this task finishes
- …

Notes:                ← blockers, decisions, deviations (status never lives here)
```

- A task has **either** `Steps` or subtasks, never both.
- The parent's `Subtasks:` list is static content (ids + filenames + names); child statuses
  live in `state.json` and are read via `tasks.py status`.
- The parent's plan approval covers the whole breakdown; each child gets its own
  implementation approval. The parent's `Context updates` aggregate what the children report.

## 6. Context

- One file per topic, named after the topic (no numbers); edit in place.
- Small, factual, present tense; split a file past ~100 lines.
- `.ai/context/index.md` is the only map: `| file | one-line summary |` — prose-maintained by
  propagate-context (and setup-project for initial seeding), always behind approval.
- Context changes happen **only** in propagate-context (and setup-project for initial seeding),
  always behind approval.

## 7. Resume rules

On every resume, from the project root run:

```text
python3 .ai/workflow/tools/tasks.py next
```

It picks the lowest-ID non-`done` root and prints the exact action or question — the table
below documents what it prints; follow its output:

| Status | `next` prints / action |
|---|---|
| `draft` | "Approve plan for tN?" — or if the human's current message approves it, hand to implement-task |
| `in-progress` | hand to implement-task — except a super-task whose subtasks are all `done` → propagate-context |
| `impl-review` | "Approve implementation of tN?" — or if the human's current message approves it, hand to propagate-context |
| `ctx-review` | "Approve context changes for tN?" — or if the human's current message approves it, hand to propagate-context to record/complete |

If `next` reports several live roots, let the human choose. If it reports none, offer plan-task.

## 8. Re-read discipline

Before acting, re-read — never from memory of an earlier read: this file (once per session),
the active task file, and the `.ai/context/` files you need. Task state is re-read via
`tasks.py` (it is cheap and always current — never trust a status read in an earlier turn).
Context is chosen by index, not read wholesale:

- **plan-task** reads `.ai/context/index.md`, opens `project.md` plus every file whose name or
  summary matches the task, and lists the files it read in the task's `Context:` section — visible
  to the human at the plan-approval gate.
- **implement-task** re-reads exactly the files named in the task's `Context:` section.
- **propagate-context** reads the index plus every file it is about to edit.

Context files stay small (§6) — that is what makes selective reading safe.

## 9. Git rules

- `.ai/tasks/` — never committed (self-gitignored, including `state.json`).
- `.ai/context/` — committed by propagate-context on context approval: `git add .ai/context && git commit -m "tN: context"`.
- Project code changes are committed by the human or explicitly requested work; skills never
  commit project code on their own.
