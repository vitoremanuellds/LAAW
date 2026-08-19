# Project Structure

Not to be confused with [.ai/structure.md](../structure.md) — that one
describes the workflow's own layout. This one describes the actual
project being built.

**Kept current by the Implementation Agent** whenever a file or
directory is created, deleted, or moved — required, not judgment-based.
See [agents.md §Implementation Agent](../agents.md#implementation-agent)
and [workflow.md §6](../workflow.md#6-context-propagation).

## Granularity rule

List directories and notable entry-point files — not every file.

- Do list: feature/module directories, their one-line purpose, and
  files another agent would need to know exist to avoid rediscovering
  them (routers, providers, shared widgets, config, entry points).
- Do not list: generated code, build output, lockfiles, test fixtures,
  or anything a directory's own purpose line already makes obvious.
- If a directory's contents are self-explanatory from its name and
  purpose (e.g. `lib/features/settings/` once described), don't
  enumerate its files individually unless one of them is something
  other tasks will specifically need to reference or extend.

If you're unsure whether something belongs, ask: would an agent
starting a new task actually need this line to find the right file on
the first try? If not, leave it out.

## Format

```
### path/to/directory/
Purpose, one line.
- notable_file.ext — why it matters, only if not obvious from purpose
```

## Structure

<!--
Populate this during initial project setup (constitution / first
phase), then update incrementally as the file tree changes. Example
shape for a Flutter project — replace with the real tree:

### lib/core/
App-wide setup: theming, routing, shared config.
- router/app_router.dart — all route definitions
- theme/app_theme.dart — single source of app styling

### lib/features/auth/
Login, signup, session handling.
- providers/auth_provider.dart — auth state, used by other features
  for logout/session checks

### lib/features/home/
Post-login landing screen and its widgets.

### lib/features/settings/
(not yet created)
-->
