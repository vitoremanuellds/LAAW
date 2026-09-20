# t{N} — {name}

Description: <what this task is and why — one short paragraph>

Context: <what the implementer must know to start; name the .ai/context/ files to re-read>

Steps:
- [ ] <step 1, small and checkable>
- [ ] <step 2>

<!-- Super-task only (parent file inside the t{N}_{slug}/ folder): replace the Steps block above
     with a Subtasks table. A task has exactly one of Steps / Subtasks, never both. Child files
     live in this same folder, named by their own ID: t{N}.1_{slug}.md, ... -->
<!--
Subtasks:
| id | name | status |
|---|---|---|
| t{N}.1 | <child name> | draft |
| t{N}.2 | <child name> | draft |
-->

Validations:
- <real command or check that proves done, e.g. `npm test`, build, grep, manual check>

Context updates:
- <.ai/context/ file: exact change to make when this task finishes — or "none">

Notes:
<!-- blockers, decisions, validation results; status never lives here -->
