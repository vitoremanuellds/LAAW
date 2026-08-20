# Decisions Index

Copy this to `../decisions/index.md` (i.e. `.ai/decisions/index.md`) in
your project. One row per ADR. Check here before writing a new ADR — a
related decision may already exist (see `workflow.md` §7).

**Kept current by whoever writes the ADR** — Constitution Agent, Phase
Planning Agent, or Implementation Agent (see `workflow.md` §10). Add
the row in the same step as creating the ADR file.

| ID | Title | Topic | Scope |
|---|---|---|---|
<!-- d01 | Use PostgreSQL for session storage | sessions, storage | project -->

Scope is one of `project` / `phase` / `implementation`, matching who
wrote it. If a later ADR supersedes an earlier one, don't delete the old
row — add "(superseded by dNN)" to its Title cell. Git keeps full
history either way.
