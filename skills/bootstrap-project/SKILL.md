---
name: bootstrap-project
description: Use when starting LAAW on a new project. Interviews the user about the project (mission, stack, architecture, design, paradigms), writes the answers into .ai/context/, and optionally registers a roadmap of not-planned tasks.
---

# Bootstrap Project

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Verify the `.ai/` skeleton exists (`.ai/workflow/`, `.ai/tasks/index.md`, `.ai/context/index.md`). If it does not, stop and tell the user to run `laaw.py sync workflow <project>` from the LAAW checkout.
2. Interview the user in small batches. Topics:
   - Mission: what the project is for, who it serves.
   - Tech stack: language, runtime, key dependencies.
   - Architecture: layout, main components, how they interact.
   - Code design: structure, naming, style, testing approach.
   - Paradigms: OOP/functional/etc., and the conventions the agent must follow.
   Record answers as given. Do not invent facts; mark unknowns as unknown.
3. Write the answers into `.ai/context/` (e.g. `project.md`, `architecture.md`) and update the `.ai/context/index.md` table. Follow the context rules: descriptive names, no IDs, no task references, current state only, no file over 100 lines.
4. Ask the user whether they want a roadmap.
   - **Yes:** break the project into sequential milestones and add one row per task to `.ai/tasks/index.md` with Status `not-planned`, Type per the simple/supertask criteria, and Dependencies as the user confirms. **Never create plan files or task folders.** Tell the user to ask for planning, one task at a time.
   - **No:** stop here.
5. Stop. This skill never plans or implements.

## Rules

- Write only to `.ai/context/` and `.ai/tasks/index.md`.
- Never create or edit task plan files — the roadmap is registration only.
- All context rules from `workflow.md` apply (100-line split, one-way links, task-agnostic).
- Do not start any implementation work.
