# Deviations

Referenced from [workflow.md §5](workflow.md#5-deviations).

A deviation = actual work materially differs from the approved plan.
Not every unexpected discovery is a deviation.

## Minor Unexpected Detail — no deviation artifact needed

Example: the plan says a function lives in `auth.ts`, it's actually in
`token.ts`. Adjust and continue.

## Significant Task Deviation — record it

Record a deviation when:

- A planned library or API cannot do what was required.
- The expected interface does not exist.
- A different implementation strategy becomes necessary.
- Task scope must materially change.

A deviation file must state:

```
Expected:     what the plan assumed
Discovered:   what is actually true
Why it fails: why the original plan can't proceed
Proposed fix: the new approach
Replan?       task / phase / project
```

Create it next to the task: `tasks/p01-t03-.../deviation.md`.

## Phase-Level Deviation

If the discovery invalidates the phase plan, the Phase Planning Agent
replans the phase. Completed tasks are inputs to the new plan, not
discarded. If the change is architecturally significant, the Phase
Planning Agent also writes an ADR (see
[agents.md §Phase Planning Agent](agents.md#phase-planning-agent)).

## Project-Level Deviation

If the discovery changes project direction, the Constitution Agent
replans the project and writes an ADR (see
[decisions/_template.md](decisions/_template.md) and
[agents.md §Constitution Agent](agents.md#constitution-agent)) — a
project-level deviation is, by definition, a decision future work needs
to know about.

## Lifecycle

```
OPEN → ADDRESSED → INCORPORATED
```

- **OPEN** — recorded, not yet resolved.
- **ADDRESSED** — the fix/replan is decided.
- **INCORPORATED** — the fact now lives in the plan, implementation, or
  an ADR. Delete the deviation file once incorporated; Git keeps the
  history. Do not let deviation files accumulate as a permanent log.
