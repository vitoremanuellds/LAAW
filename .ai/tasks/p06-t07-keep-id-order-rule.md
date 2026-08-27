# P06-T07: Keep the one-line ID-order-≠-execution-order rule in §11

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
Decision 7: `reference/status-and-info.md` already holds the worked-example
reasoning for "ID order ≠ execution order," but the paragraph in workflow.md
§11 ("A replan can insert a task... Resolve 'first/next' against Depends-on +
Status columns, never the lowest ID") is itself an operating rule agents must
follow, not just rationale — it stays in workflow.md. This task's actual change
is small: remove the resolved `[HUMAN]` comment marker and confirm the rule
paragraph and the pointer sentence above it are both still present and correct,
since the decision was to keep the current state rather than trim it.

## Implementation

### Objective

Confirm and preserve the "ID order ≠ execution order" rule in §11 as-is; remove
the now-resolved `[HUMAN]` comment; confirm `reference/status-and-info.md`
still holds only the reasoning/examples, not a restatement of the rule itself
that would make workflow.md's copy redundant in the other direction.

### In scope

- The `[HUMAN]` comment line in §11 that questioned this section.
- A read-only check of `reference/status-and-info.md`'s content.

### Out of scope

- The rule paragraph's own wording — no edit needed, it's being kept as-is.
- Any other content in `reference/status-and-info.md`.

### Files to modify

- `workflow.md` — §11 (remove one `[HUMAN]` comment line only).

### Steps

1. Read `reference/status-and-info.md` and confirm it holds the worked
   examples/reasoning for ID-order-≠-execution-order without itself stating the
   operating rule as a standalone directive — if it already does, no change
   needed there.
2. In workflow.md §11, remove the `[HUMAN]` comment line ("Maybe we do not need
   to say this, let the agent discover when it uses the skill.") that precedes
   the "ID order ≠ execution order" rule paragraph, leaving the rule paragraph
   and the pointer sentence to `reference/status-and-info.md` both unchanged.

### Dependencies

None.

### Expected result

§11's rule paragraph is unchanged in content; the resolved review comment is
gone; `reference/status-and-info.md` confirmed to hold only reasoning, not a
duplicate of the rule.

### Automatic validations

- `grep -n "let the agent discover when it uses the skill" workflow.md`
  returns no matches.
- `grep -c "ID order ≠ execution order" workflow.md` returns at least 1 (rule
  still present).

### Manual validations

- Confirm `reference/status-and-info.md` doesn't itself state the rule as a
  directive (only reasoning/examples) — if it does, that's a separate
  redundancy worth flagging, not silently fixing as part of this task.
