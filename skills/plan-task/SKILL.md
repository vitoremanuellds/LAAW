# plan-task

Plan a task: fill its file sections (In scope, Out of scope, Context, Steps/Validations,
Context updates) and ask for plan approval.

## When to use

- After a task is created (`created` status) and its file is drafted (`planning` status).
- When the human asks to plan a task or re-plan it.

## Steps

1. Run `python3 .ai/workflow/tools/laaw.py status <task-id>` to get the task's current state.
2. Read `workflow.md` (§2, §5, §8) for task file rules and re-read discipline.
3. If the task is in `created` status (no file yet), run:
   ```
   python3 .ai/workflow/tools/laaw.py draft <task-id>
   ```
   This writes the task file template and transitions to `planning`.
4. Read `.ai/context/index.md`, then `project.md` plus every file whose name or summary
   matches the task (workflow.md §8). List the files read in the task's `Context:` section.
5. Fill the task file sections:
   - **In scope**: what this task covers (one short paragraph + bullet list).
   - **Out of scope**: what it explicitly does NOT do, naming where that work belongs.
   - **Context**: files read from `.ai/context/` (workflow.md §8).
   - **Steps** (leaf/child only): implementation-ready, concrete actions. Each step is small
     enough to execute without re-designing. After plan approval, step text is a record —
     implement-task may only flip `- [ ]` to `- [x]`.
   - **Validations**: commands/checks proving the work is done.
   - **Context updates**: exact changes to make in `.ai/context/` when this task finishes.
   - **Subtasks** (super-task parent only): static list of child IDs + filenames + names.
     Add children with `laaw.py subtask <root-id> <name>` before work starts.
6. Save the task file.
7. Run `python3 .ai/workflow/tools/laaw.py set-status <task-id> planning` if not already done.
8. Ask the human: **"Approve plan for <task-id>?"** — show the task file. On approval,
   stop and wait for the human's answer. Do not ask and answer in the same response.

## Re-planning

- Tasks still in `created` or `planning` status can be re-planned: rename, remove, add/remove
  subtasks, or change depends-on lists.
- Tasks that left `created` (i.e., are `planning` or beyond) can be re-planned too, but
  `laaw.py` refuses operations that would touch tasks that are `in-progress` or beyond.
- A `done` task is never re-planned — wrong work gets a new task via `laaw.py new`.

## Notes

- A super-task with no subtasks never reaches the context gate; add subtasks before work starts.
- The parent's plan approval covers the whole breakdown; each child gets its own
  implementation approval.
- Use `laaw.py board` to see the whole board; `laaw.py next` for the exact next action.
