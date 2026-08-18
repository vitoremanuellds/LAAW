# Execution Policy

Referenced from [workflow.md §9–10](workflow.md#9-gates). Defines **who**
satisfies each gate. Changing this file never requires changing
[workflow.md](workflow.md).

## Mode

```
mode: assisted
```

One of: `manual` · `assisted` · `delegated` · `autonomous`.

- **manual** — humans perform every gate.
- **assisted** — agents perform mechanical review/validation; humans
  retain approval authority.
- **delegated** — selected gates delegated to agents; humans approve the
  rest.
- **autonomous** — agents may perform the full workflow subject to the
  gates below.

## Gates

```yaml
constitution-review:
  authority: human

phase-review:
  authority: human

task-review:
  authority: human

task-validation:
  authority: agent

phase-validation:
  authority: agent

context-update:
  authority: agent
```

Default authority for any gate not listed is `human`. An agent must not
assume delegation — if a gate is absent here, treat it as human-owned.

## Changing Authority

To delegate a gate, add or edit its entry above. This is the only file
that should ever change when adjusting how much autonomy agents have.
[workflow.md](workflow.md) and the [agent contracts](agents.md) stay
fixed regardless of mode.
