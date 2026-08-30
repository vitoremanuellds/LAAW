# Info

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
