# t{N} — {name}

Description: {description}

Context: <what the implementer must know to start; name the .ai/context/ files to re-read>

Subtasks:
<!-- one line per child, added at plan time, e.g.:
     - t{N}.1 (t{N}.1_login-form.md) — login form
     Status lives in .ai/tasks/state.json — read it via: python3 .ai/workflow/tools/tasks.py status -->

Validations:
- <run after ALL subtasks are done, e.g. `npm test`, build, grep>

Context updates:
- <aggregate of what the subtasks report in their files, or "none">

Notes:
<!-- blockers, decisions, validation results. Status lives in .ai/tasks/state.json — never in task files. -->
