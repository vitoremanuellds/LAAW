# Why every operation re-reads its skill file, every time — detail

Referenced from [`../workflow.md §2`](../workflow.md#2-starting-point-for-any-agent).
The rule itself is already fully stated there — read this only for why
it exists, which isn't needed on every operation.

## The lesson

Gate-skip and scope-overstep bugs have repeatedly traced back to a
skill file being skipped or half-remembered rather than freshly read —
not to the rule itself being wrong, but to an agent assuming it already
knew the procedure from earlier in the session, or from having run the
same skill many times before, and acting on that assumption instead of
the file's actual current content. That's why every operation opens
and reads its matching skill file in full, every time, even when the
agent is confident it already knows the procedure: confidence isn't
the same as the file being unchanged, and the failure mode this guards
against produces no error — just a gate quietly skipped or a scope
quietly overstepped, discovered later if at all.

This is the same discipline `implement-task-full` documents for
`workflow.md` itself (see its "What to read" section) — a skill's own
partial summary of a rule, however careful, is not a substitute for
reading the rule's actual current text.
