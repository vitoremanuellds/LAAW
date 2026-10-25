---
name: implement-task
description: Use when the user asks to implement an approved task or subtask. Checks dependencies, implements the task following its plan file, records deviations as notes, handles cancellation, and runs the validations — all state changes via the CLI.
---

# Implement Task

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Identify the task:
   - Simple task: `.ai/tasks/t{0N}_task-name/task.md`
   - Subtask: `.ai/tasks/t{0N}_supertask-name/t{0N}.{n}_subtask-name/task.md`
2. Check dependencies: `laaw task deps <id>`. If any dependency is not `done`, **refuse to implement** — the CLI lists the unsatisfied deps. Stop.
3. Read the task file and the context files linked in its Context section. This is your context for the task: do not read any other files from the codebase before finishing these.
4. Start: `laaw task implement <id>` (→ `in-progress`).
5. Implement following the Steps section, staying inside In scope. Record exactly one progress note per completed Step, right after that step finishes: `laaw task note <id> --tag progress --text "..."`. Never batch several steps into one note, and never skip a step — even trivial ones get their note. A note is for recording what the implementation created as it happened — progress per step, deviations, decisions/gotchas worth keeping; notes are CLI-owned state rendered into `notes.md`, not prose appended to `task.md`.
6. Iterate with the user until the implementation is approved:
   - If the user requests a change that is incompatible with the approved plan, apply it **and record the deviation**: in `task.md`'s Notes section and as `laaw task note <id> --tag deviation --text "..."`.
   - If the plan turns out to be unimplementable (a premise is wrong, something is missing), **stop and notify the user**, and record the deviation. The approved plan cannot be edited: the user must re-plan the whole task with the agent (`laaw task plan <id>` again; status back to `planning`). When the re-planned task is approved again, report its dependent tasks so the user can check the new plan still satisfies them.
   - If the user asks to abandon or cancel the task, run `laaw task cancel <id>` and stop the work. The CLI reports the dependent tasks — they are blocked forever now. Let the user decide for each: cancel it too, re-plan it without the dependency (`laaw task dep-remove`), or replace the dependency with a new task (`laaw task dep-add`). Never cancel dependents automatically.
7. Run the Validations section. Run the agent-doable validations yourself; tell the user which validations are human-only so they can run them.
8. Run `laaw task propagate <id>` only after the user explicitly approves the implementation. Passing the validations (Step 7) does not constitute approval — present the results, wait for the user's explicit approval, and only then run `laaw task propagate <id>` and tell the user to proceed with context propagation (`propagate-context`).

## Rules

- The approved plan is the contract and is immutable: after approval, the only mutable part of the task file is its Notes section (and, for supertasks, the subtask table in state). Any departure from the plan is a deviation and must be recorded.
- A cancelled dependency never becomes `done`, so its dependents are blocked until the user acts on them. Dependencies live in state — re-pointing one is `laaw task dep-add` / `dep-remove`.
- Do not expand scope. If you discover work that is out of scope, note it (in Notes and as a deviation note) and tell the user; do not do it.
- Context comes from the plan's Context section first: read the linked `.ai/context/` files before reading any other files from the codebase.
- Keep any new or edited project files consistent with the documented architecture in `.ai/context/`.
