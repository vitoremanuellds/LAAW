---
name: plan-task
description: Use when the user asks to plan or create a task, or to plan a subtask of an existing supertask. Registers the task in the right index and creates its plan file. For new tasks, decides whether the task is simple or a supertask.
---

# Plan Task

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Understand the task the user described. Ask clarifying questions if the scope is unclear.
2. Gather context before touching the codebase:
   - Read `.ai/context/index.md`, then the context files that look relevant to the task's scope.
   - Only after that, read codebase files — and only what you still cannot answer from context.
   - If the context is missing or stale for the task's scope, note it in the plan's Context section.
3. Decide what kind of planning this is:
   - **Subtask** — the user asks to plan a subtask of an existing supertask. Work inside the supertask's folder; do not create a new top-level task.
   - **New simple task / new supertask** — classify using the Simple vs supertask criteria below.
4. Compute the ID:
   - New task: from `.ai/tasks/index.md`, `max(existing IDs) + 1`. If the index does not exist, create it with the table header.
   - Subtask: `t{N}.{next}`, read from the supertask's Subtask table.
5. Register the task:
   - New task: add a row to the index table with ID, Status, Name, Description (≤ 180 chars), Type (`simple` or `supertask`), Dependencies. Set the status to `planning` once the plan file is created. Tasks registered without a plan file stay `not-planned`.
   - Subtask: its row already exists in the supertask's Subtask table (add it if missing). Once the plan file is created, set its status to `planning` in the Subtask table, and set the owning supertask's status to `in-progress` in the top-level index (if it is not already `in-progress`). That status change is the only touch on the top-level index allowed when planning a subtask.
6. Create the plan file:
   - Simple task: `.ai/tasks/t{0N}_task-name.md`
   - Supertask: `.ai/tasks/t{0N}_task-name/task.md`, with a Subtask table listing its subtasks. Do NOT create subtask files or `new-info.md` yet — subtask files are only created when the user asks for them, and `new-info.md` is created on first subtask propagation.
   - Subtask: `.ai/tasks/t{0N}_supertask-name/t{0N}.{n}_subtask-name.md`
   - A plan file that outgrows 100 lines and must stay (a supertask's `task.md`, a subtask file, or a simple plan whose split proposal was vetoed) is split into `<base>_att_<descriptive>.md` files, named per the att convention in `workflow.md` and linked from the main file.
7. The plan file must contain: Title, Description, Context, In scope / Out of scope, Steps (with pseudocode where useful), Validations (including any human-only checks), and Notes (required, initially empty).
   - Context lists the relevant `.ai/context/` files **with their paths** (e.g. `../../context/auth-module.md`). It is the direct door to context: whoever implements this task reads those files first, before touching the codebase.

## Simple vs supertask

For a new task, classify it using these criteria:

- **Hard signals → supertask, no debate:**
  - the plan file would exceed 100 lines;
  - the work spans 2+ modules/layers defined in `.ai/context/`.
- **Sizing → present a split proposal (vetoable at the plan gate):** a task is sized to fit one 64k session — plan + implementation + propagation — and one honest review. A split proposal fires if **any** of: estimated more than 200 lines of net change with tests and fixtures counted in full; more than 5 files; more than 5 independent design decisions (count them in the plan's Steps); the change touches a public API, persistence/migration, security, or wire format; the verification pass (tests, build) plausibly needs more than one fix round. If the work genuinely cannot be split, it stays a simple task — but record the estimate and why. A split, when it happens, must leave every subtask ending in a state that passes its own validations: verification loops must not stack.
- **Transparency:** always write the estimate with concrete file names — an estimate without file names is not an estimate — the session budget (plan+context ≈5k tokens, reading ≈3× the changed lines, the edits, two test rounds ≈10–15k, gate buffer), and the decision with its reasoning into the plan file, so the user can veto it at the plan gate. The hard cap is not vetoable: more than 300 lines of total diff including tests, or more than 3 distinct design decisions in flight at once — past that the review gate is a rubber-stamp.

## Rules

- Keep the plan file under 100 lines. If it grows beyond that, the task is a supertask (hard signal above). A file that must stay and outgrows 100 lines is split into att files named per the att convention in `workflow.md`.
- Subtask files are only created when the user explicitly asks to plan that subtask — never on your own initiative.
- Context before codebase: read `.ai/context/index.md` first, then only the files that look relevant to the task's scope, and only then read codebase files.
- Present the plan to the user. Iterate with the user until the plan is approved. Do not start implementing.
