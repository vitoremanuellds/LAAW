# Context

Entry point for `context/` — everything about the actual codebase:
architecture, conventions, terminology, and however many additional
files make sense for this project's actual moving parts. No fixed
subfolder convention — name and organize additional files by whatever
groups the project naturally: an architectural layer, a feature-level
concept, a domain area. "Module" here means a conceptual group of
moving parts that make up a feature, not a coding-language module or a
folder of classes.

| File | Description | Status | Relations |
|---|---|---|---|
| [workflow-doc-conventions.md](workflow-doc-conventions.md) | workflow.md section-stability rule + reference/ file convention (P02) + multi-sub-operation skill shape (P04) | active | — |
| [template-bootstrap-conventions.md](template-bootstrap-conventions.md) | Template → destination → copying-skill map; "templates hold only artifact content" rule (established P01) | active | — |
| [task-phase-output-structure.md](task-phase-output-structure.md) | Section order for define-task-full/define-phase's output, why the flexible-detail marker is task-only (established P03) | active | — |

**Status** is `active` or `superseded`. When an architecture changes,
don't delete the old file — mark it superseded and point to what
replaced it, same as an ADR. Whoever writes or updates a context file
updates its row here in the same step.
