# Info

```yaml
profile: full   # fixed — this file is only ever used for the full profile
```

## Policy — who's authorized for each gate

Full gate list and explanations live in `.ai/workflow/workflow.md §5`
— this section holds only the values, not the reasoning, so keep it
short.

```yaml
mode: assisted   # manual | assisted | delegated | autonomous

overrides:
  # Only needed for exceptions to your mode's default (see
  # .ai/workflow/workflow.md §5 for what each mode defaults to). In
  # delegated mode this list *is* your actual policy — every gate you
  # don't list here falls back to human.
```

## Status — the fast pointer

IDs only, no status values — this just tells you which two files to
open next. The actual status of the active phase/task lives in the
permanent record: `.ai/constitution/roadmap.md` (phase) and that
phase's own file's task table (task). See
`.ai/workflow/workflow.md §11`.

```
Active phase: P03
Active task: P03-T03
Blocked: none
```
