# Execution Policy

Copy this to `../policy.md` (i.e. `.ai/policy.md`) in your project and
edit freely — this file is yours, never touched by a submodule update.
Defines **who** satisfies each gate.

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

task-completion-review:
  authority: human

phase-completion-review:
  authority: human

context-update:
  authority: agent
```

Default authority for any gate not listed is `human`. An agent must not
assume delegation — if a gate is absent here, treat it as human-owned.

## Changing Authority

To delegate a gate, add or edit its entry above. This is the only file
that should ever change when adjusting how much autonomy agents have.
The protocol itself (including agent contracts) stays fixed regardless
of mode — see `workflow.md` (i.e. `.ai/workflow/workflow.md`) §10.
