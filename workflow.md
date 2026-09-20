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

Each task's status lives in exactly one row, by level:

- Root tasks → their row in `.ai/tasks/index.md` (`| id | name | status |`).
- Subtasks → their row in the parent's `task.md` `Subtasks:` table (same columns).

A task never tracks its own status. No other status values exist (no `blocked`; blockers are
Notes lines).

| From | To | Only writer | Trigger |
|---|---|---|---|
| — | `draft` | plan-task | task file(s) created; root row (and child rows) added as `draft` |
| `draft` | `in-progress` | implement-task | plan approved (root), or a subtask's turn comes |
| `impl-review` | `in-progress` | implement-task | implementation rejected → fix work |
| `in-progress` | `impl-review` | implement-task | Steps done, Validations run, Context updates filled |
| `impl-review` | `done` | implement-task | implementation approved (subtasks only) |
| `impl-review` | `ctx-review` | propagate-context | task with Steps: context changes written |
| `in-progress` | `ctx-review` | propagate-context | super-task: all subtasks `done`, parent Validations run, context changes written |
| `ctx-review` | `done` | propagate-context | context approved; `.ai/context/` committed |

Rules:
- A task with Steps reaches `impl-review` and waits there for implementation approval.
- A super-task stays `in-progress` while its subtasks are worked; each subtask goes
  `draft → in-progress → impl-review → done` on its own. The parent then moves to the context gate.
- After any rejection, the fix work happens before the re-ask, and the status flips back first.

## 3. Approvals

- Human-only: an approval is a human message answering the specific question asked. Never ask
  and answer in the same response. Re-asking after edits is safe; approvals are not consumed.
- Every question names the task ID and points at the artifact being approved.
- The agent records each approval as its first action (the status flip), then continues in the
  same turn.

| Gate | Question asked | Recorded by |
|---|---|---|
| Plan | "Approve plan for tN?" (task file shown/linked) | implement-task: `draft → in-progress` |
| Implementation | "Approve implementation of tN?" (diff summary + validation results shown) | subtask: implement-task sets `done`; task with Steps: propagate-context sets `ctx-review` |
| Context | "Approve context changes for tN?" (exact edits shown) | propagate-context: `ctx-review → done` |

## 4. Layout and IDs

```text
.ai/
  workflow/            ← synced LAAW copy; never hand-edit
    workflow.md
    skills/<name>/SKILL.md
    templates/
    tools/
  tasks/               ← local working files, gitignored
    index.md           ← | id | name | status |  (root rows only)
    t1_add-login.md            ← leaf task: flat file
    t2_auth-flow/              ← super-task: folder
      task.md                  ← parent file; Subtasks table holds child status rows
      t2.1_login-form.md       ← child files, named by their own ID
      t2.2_session.md
  context/             ← committed project knowledge
    index.md           ← | file | one-line summary |
    project.md
    <topic>.md
```

- Root IDs: `t1`, `t2`, … Subtask IDs: `t2.1`, `t2.2`. Next root ID = highest root ID + 1 in the
  index; next child ID = highest child + 1 in the parent's table. No scripts, no epoch.
- Shape follows content: a leaf task is one flat file `t{NN}_{slug}.md`; a super-task is a folder
  `t{NN}_{slug}/` containing `task.md` plus one child file per workstream, each named by its own
  ID (`t{N}.{k}_{slug}.md`). Find a task by ID: for `t2`, use `t2_*/task.md` if that folder
  exists, else the file `t2_*.md`; children live inside the parent folder.
- Slugs: lowercase, hyphens, no spaces, ~30 chars max, chosen at plan time. The ID is the only
  reference used in tables, cross-links, and approval questions — filenames are display
  convenience. If a draft's name changes on re-plan, plan-task renames the file or folder.
- A task's shape is fixed at plan time; re-planning a draft may change it (plan-task moves the
  file).
- Tasks are local working files: `.ai/tasks/.gitignore` contains `*`. Context is committed.

## 5. Task files

One file per task, from `templates/task-template.md`:

```markdown
# tN — name

Description: …

Context: …            ← what the implementer must know; names the .ai/context/ files read at plan time

Steps:                ← exactly ONE of Steps / Subtasks
- [ ] …

<!-- super-task parent instead of Steps:
Subtasks:
| id | name | status |
|---|---|---|
| tN.1 | <child name> | draft |
-->

Validations:          ← commands/checks proving the work is done
- …

Context updates:      ← exact changes to make in .ai/context/ when this task finishes
- …

Notes:                ← blockers, decisions, deviations (status never lives here)
```

- A task has **either** `Steps` or subtasks, never both.
- Super-task: the parent's `Subtasks:` table is the only home of child status rows; each child is
  also its own file in the parent folder, named by its own ID. The parent's plan approval covers
  the whole breakdown; each child gets its own implementation approval. The parent's
  `Context updates` aggregate what the children report in theirs.

## 6. Context

- One file per topic, named after the topic (no numbers); edit in place.
- Small, factual, present tense; split a file past ~100 lines.
- `.ai/context/index.md` is the only map: `| file | one-line summary |`.
- Context changes happen **only** in propagate-context (and setup-project for initial seeding),
  always behind approval.

## 7. Resume rules

Read `.ai/tasks/index.md` fresh on every resume — it holds root rows only. Pick the lowest-ID
non-`done` root (if several roots are live, let the human choose). For a super-task, read its
`task.md` `Subtasks:` table to know the children's state.

| Status | Action |
|---|---|
| `draft` | Ask plan approval — or if the human's current message approves it, hand to implement-task |
| `in-progress` | Run implement-task — except a super-task whose subtasks are all `done` → propagate-context |
| `impl-review` | Ask implementation approval — or if the human's current message approves it, hand to propagate-context |
| `ctx-review` | Ask context approval — or if the human's current message approves it, hand to propagate-context to record/complete |

## 8. Re-read discipline

Before acting, re-read — never from memory of an earlier read: this file (once per session), the
active task file (and for a super-task, its `Subtasks:` table), and the `.ai/context/` files you
need. Context is chosen by index, not read wholesale:

- **plan-task** reads `.ai/context/index.md`, opens `project.md` plus every file whose name or
  summary matches the task, and lists the files it read in the task's `Context:` section — visible
  to the human at the plan-approval gate.
- **implement-task** re-reads exactly the files named in the task's `Context:` section.
- **propagate-context** reads the index plus every file it is about to edit.

Context files stay small (§6) — that is what makes selective reading safe.

## 9. Git rules

- `.ai/tasks/` — never committed (self-gitignored).
- `.ai/context/` — committed by propagate-context on context approval: `git add .ai/context && git commit -m "tN: context"`.
- Project code changes are committed by the human or explicitly requested work; skills never
  commit project code on their own.
