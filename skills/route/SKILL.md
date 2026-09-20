---
name: route
description: Entry point for any LAAW session. Reads .ai/tasks/index.md, picks the active root task, and hands off to exactly one skill or asks the pending approval question. Use when the human says "continue", "what's next", or starts work without naming a step.
---

# Skill: route

Route decides what happens next. It never does task work itself — it ends by handing off to
exactly one other skill, or by asking the human the pending approval question.

## Steps

1. Check `.ai/workflow/workflow.md` exists. If not: LAAW is not installed in this project. Tell
   the human to run `tools/sync-workflow.py <project-root>` from a LAAW checkout, then stop.
2. Check `.ai/tasks/index.md` exists. If not: hand off to **bootstrap** and stop.
3. Read `.ai/workflow/workflow.md` (once per session) and `.ai/tasks/index.md` fresh.
4. The index holds root rows only. Pick the lowest-ID non-`done` root task. If several roots are
   live, ask the human which one and stop. If none: report "no active tasks" and offer
   **plan-task** for a new task; stop.
5. Apply the resume table from workflow.md §7 to that task's status:

   | Status | Action |
   |---|---|
   | `draft` | Show the task file and ask "Approve plan for tN?" — unless the human's current message already approves it, in which case hand off to **implement-task** |
   | `in-progress` | Hand off to **implement-task** — except a super-task whose `Subtasks:` table is all `done` (read its `task.md`): hand off to **propagate-context** |
   | `impl-review` | Ask "Approve implementation of tN?" (diff summary + validation results) — unless the human's current message already approves it, in which case hand off to **propagate-context** |
   | `ctx-review` | Ask "Approve context changes for tN?" (exact edits) — unless the human's current message already approves it, in which case hand off to **propagate-context** to record/complete |

6. Hand off and stop. One skill per route decision; never chain more than one hand-off without
   returning control to the human at an approval gate.

## Rules

- Never ask and answer in the same response: if you asked for an approval this turn, stop after
  asking.
- Every question names the task ID and points at the artifact (task file, diff, context edits).
- Re-asking after edits is safe; approvals are not consumed.
