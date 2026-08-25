# Info (medium profile)

```yaml
profile: medium   # fixed — this file is only ever used for the medium profile
```

## Policy — who's authorized for each gate

Full gate list and explanations live in
`.ai/workflow/workflow-medium.md §5` — this section holds only the
values, not the reasoning, so keep it short.

```yaml
mode: assisted   # manual | assisted | delegated | autonomous

overrides:
  # Only needed for exceptions to your mode's default (see
  # .ai/workflow/workflow-medium.md §5 for what each mode defaults
  # to). In delegated mode this list *is* your actual policy — every
  # gate you don't list here falls back to human.
```

## Status — the fast pointer

```
Active task: —
Blocked: none
```

ID only, no status values — this just tells you which file to open
next. The actual status of the active task lives in the permanent
record: `.ai/constitution/roadmap.md`. See
`.ai/workflow/workflow-medium.md §11`.
