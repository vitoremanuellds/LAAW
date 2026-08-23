# Info

Copy this to `.ai/info.md` in your project and edit — this file is
yours, never touched by a submodule update. It's read at the start of
every operation (see `.ai/workflow/workflow.md §2`) — always read it
fresh, never rely on what you saw earlier in a session; it can change
mid-session and stale memory of it is exactly what causes a gate to
get ignored.

## Policy — who's authorized for each gate, and how much structure applies

Full gate list and explanations live in `.ai/workflow/workflow.md §5`;
profile tiers live in `.ai/workflow/workflow.md §14` — this section
holds only the values, not the reasoning, so keep it short.

```yaml
mode: assisted   # manual | assisted | delegated | autonomous
profile: full    # lite | medium | full — structural/ceremony/detail tier,
                 # independent of mode (any combination is valid).
                 # Missing key = full, for compatibility with info.md files
                 # written before this field existed.
                 # See .ai/workflow/workflow.md §14 for what each tier cuts.

overrides:
  # Only needed for exceptions to your mode's default (see
  # .ai/workflow/workflow.md §5 for what each mode defaults to). In
  # delegated mode this list *is* your actual policy — every gate you
  # don't list here falls back to human.
  # A gate that doesn't exist at your current profile (§14) is ignored
  # here even if listed — profile controls which gates exist at all;
  # mode/overrides only control who approves the ones that do.
```

## Status — the fast pointer

```
Active phase: —
Active task: —
Blocked: none
```

IDs only, no status values — this just tells you which two files to
open next. The actual status of the active phase/task lives in the
permanent record: `.ai/constitution/roadmap.md` (phase) and that
phase's own file's task table (task). See
`.ai/workflow/workflow.md §11`.
