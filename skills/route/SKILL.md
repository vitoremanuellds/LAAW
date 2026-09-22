---
name: route
description: Entry point for any LAAW session. Runs tasks.py next, which picks the active root task, and either hands off to exactly one skill or asks the pending approval question. Use when the human says "continue", "what's next", or starts work without naming a step.
---

# Skill: route

Route decides what happens next. It never does task work itself — it follows the output of
`tasks.py next`, handing off to exactly one other skill, or asking the human the pending
approval question.

## Steps

1. Check `.ai/workflow/workflow.md` exists. If not: LAAW is not installed in this project.
   Tell the human to run `tools/sync-workflow.py <LAAW-checkout> <project-root>` from a LAAW checkout, then stop.
2. From the project root run:

   ```text
   python3 .ai/workflow/tools/tasks.py next
   ```

   - If it reports **no state file** (not bootstrapped): hand off to **bootstrap** and stop.
   - If it reports **no active tasks**: report that and offer **plan-task** (a single task) or
     **plan-project** (several root tasks for the project); stop.
   - If it reports **multiple active roots**: ask the human which one to work; stop.
3. Follow exactly what it printed:
   - **It printed a question** ("Approve … for tN?"): unless the human's current message already
     answers that exact question, show the artifact it named (task file, diff summary +
     validation results, exact context edits), ask the question, and stop. If the human's
     current message already answers it, do the hand-off the output names, in this turn.
   - **It printed a block** ("… is BLOCKED by …"): report the block and the blocking task to the
     human; ask whether to resume the blocker or revise the plan (plan-task/plan-project); stop.
   - **It printed a hand-off** (implement-task / propagate-context): hand off and stop.
   - **It printed a `Next:` line after a status flip**: do exactly what it says — the same
     rules apply, including stopping after an approval question.

## Rules

- Never ask and answer in the same response: if you asked for an approval this turn, stop after asking.
- Every question names the task ID and points at the artifact (task file, diff, context edits).
- Never do task work yourself, never hand off to more than one skill per route decision.
- Never hand-edit `.ai/tasks/state.json` — if `tasks.py` refuses something, report the error
  to the human instead of working around it.
