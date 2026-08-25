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
<!-- auth-module.md | Auth flow, session handling, token lifecycle | active | related: score-engine.md -->

**Status** is `active` or `superseded`. When an architecture changes,
don't delete the old file — mark it superseded and point to what
replaced it, same as an ADR. Whoever writes or updates a context file
updates its row here in the same step.
