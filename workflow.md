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
It is written only by the tasks CLI (`python3 .ai/workflow/tools/laaw.py`) — never by hand,
never via a file-editing tool, no matter what. The CLI validates every `set-status` call
against the table below and refuses anything else, so the table is also the complete set of
legal status changes. `tools/tests/` keeps the CLI's table in sync with this one.

Linear 5-state flow:

```text
created ──draft──▶ planning ──approve plan──▶ in-progress ──approve impl──▶ contextualizing ──approve ctx──▶ done
```

Which skill may trigger each transition:

| From | To | Only writer | Trigger |
|---|---|---|---|
| — | `created` | laaw.py | `laaw.py <state.json> new` / `subtask` registers the task (no file written yet) |
| `created` | `planning` | laaw.py | `laaw.py <state.json> draft` writes the task file template |
| `planning` | `in-progress` | implement-task | plan approved (root), or a subtask's turn comes |
| `in-progress` | `contextualizing` | implement-task | Steps done, Validations run, Context updates filled |
| `contextualizing` | `done` | propagate-context | context approved; `.ai/context/` committed |

Rules:
- **No markdown file holds a status.** Task files hold content (Description, In scope, Out of
  scope, Steps, Validations, Context updates, Notes); `laaw.py status` is the only place to read one.
- A **blocked** task — its depends-on list is not all `done` — cannot move past `created`; the CLI
  refuses the flip and `next` marks it. Depends-on lists are set with `laaw.py depends` while a
  task is still `created` (workflow.md §4).
- A task with Steps reaches `contextualizing` and waits there for context approval.
- A root task with Steps always passes through `contextualizing` — the `in-progress → done` path
  is for subtasks only.
- A super-task stays `in-progress` while its subtasks are worked; each subtask goes
  `created → planning → in-progress → contextualizing → done` on its own. The parent then moves to the context gate.
- A super-task with no subtasks never reaches the context gate; plan-task adds the subtasks
  before work starts (`laaw.py subtask` is refused once the root left `created`).
- After any rejection, the fix work happens before the re-ask, and the status flips back first.
- A `done` task never changes status again; wrong work gets a new task via plan-task.

## 3. Approvals

- Human-only: an approval is a human message answering the specific question asked. Never ask
  and answer in the same response. Re-asking after edits is safe; approvals are not consumed.
- Every question names the task ID and points at the artifact being approved.
- The agent records each approval as its first action — a `laaw.py set-status` call — then
  continues in the same turn.

| Gate | Question asked | Recorded by |
|---|---|---|
| Plan | "Approve plan for tN?" (task file shown/linked) | implement-task: `set-status` `planning → in-progress` |
| Implementation | "Approve implementation of tN?" (diff summary + validation results shown) | subtask: implement-task sets `done`; task with Steps: propagate-context sets `contextualizing` |
| Context | "Approve context changes for tN?" (exact edits shown) | propagate-context: `set-status` `contextualizing → done` |

## 4. Layout and IDs

```text
.ai/
  workflow/            ← synced LAAW copy; never hand-edit
    workflow.md
    skills/<name>/SKILL.md
    tools/             ← laaw.py lives here
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
- A task's shape is fixed at plan time; **re-planning** may still change any task that is still
  `created`: `laaw.py rename`, `remove`, `depends`, and — for a live super-task — `subtask` (adding
  a child) and `remove`/`rename` (dropping or renaming a child that has not started). The CLI
  refuses any operation that would touch a task that left `created`; a super-task stops accepting
  children once it reaches the context gate. A `done` task is never re-planned — wrong work gets
  a new task via plan-task.
- Tasks are local working files: `.ai/tasks/.gitignore` contains `*`. Context is committed.

The tasks CLI (run from the project root, or with `--root`):

```text
init                     create .ai/tasks/ (state.json, .gitignore) and .ai/context/ (index.md)
new <name> [--super] [--desc T]
draft <id>               write task file template, flip created → planning
subtask <root-id> <name> [--desc T]    register a child of a super-task
rename <id> <new-name>   created/planning tasks only
remove <id>              created/planning tasks only
set-status <id> <status> validated against §2 (refused while blocked)
depends <id> <dep-id>…  set the depends-on list (created/planning tasks only; replaces it; --clear empties it)
status [id]              one task, or the board
board                    the whole board as a markdown table (includes depends-on)
next                     active task + exact next action/question
check                    state/file consistency report
```

Every `set-status` prints a `Next:` line saying exactly what the agent should do next — including
the approval question to ask and where to stop. `next` and `board` say the same on resume. Agents
follow that output; an approval question always ends the turn.

## 5. Task files

One file per task, scaffolded by `laaw.py draft` — which also transitions the task to `planning`:

```markdown
# tN — name

Status: created

Description: …

In scope:             ← what this task covers; checked by the human at plan approval
- …

Out of scope:         ← what it explicitly does NOT do, and where that work belongs
- …

Context: …            ← what the implementer must know; names the .ai/context/ files read at plan time

Steps:                ← leaf/child tasks only; implementation-ready
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
- Every task has `In scope` and `Out of scope`; out-of-scope items name where the work belongs
  if anywhere.
- Steps must be **implementation-ready**: concrete, in order, each one a small action or a short
  pseudocode block the implementer can execute without re-designing — abstract enough to stay
  code-free, concrete enough that it is not a second planning exercise. Pseudocode and well-defined
  micro-steps are encouraged. After plan approval a step's text is a record: implement-task may
  only flip `- [ ]` to `- [x]` — never reword, merge, or delete step text.
- The parent's `Subtasks:` list is static content (ids + filenames + names); child statuses
  live in `state.json` and are read via `laaw.py status`.
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
python3 .ai/workflow/tools/laaw.py next
```

It picks the lowest-ID non-`done` root and prints the exact action or question — the table
below documents what it prints; follow its output:

| Status | `next` prints / action |
|---|---|
| blocked (depends-on not all `done`) | "tN is BLOCKED by tX (status)" — do not work it; resume the blocking task or ask the human to revise the plan |
| `created` | "Draft the task file (laaw.py draft), fill sections, then ask plan approval" |
| `planning` | "Approve plan for tN?" — or if the human's current message approves it, hand to implement-task |
| `in-progress` | hand to implement-task — except a super-task whose subtasks are all `done` → propagate-context |
| `contextualizing` | "Approve context changes for tN?" — or if the human's current message approves it, hand to propagate-context to record/complete |

If `next` reports several live roots, let the human choose. If it reports none, offer plan-task.

## 8. Re-read discipline

Before acting, re-read — never from memory of an earlier read: this file (once per session),
the active task file, and the `.ai/context/` files you need. Task state is re-read via
`laaw.py` (it is cheap and always current — never trust a status read in an earlier turn).
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
