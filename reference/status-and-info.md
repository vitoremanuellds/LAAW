# Status detail — who sets what, and the distinctions that get conflated

Referenced from [`../workflow.md §11`](../workflow.md#11-status-the-permanent-record).
The enum itself and the "status lives only in the relevant table,
never `info.md`" rule are already fully stated there. This file holds
the lookup table and the extended explanations — read it when you're
actually unsure which skill sets a given value, or need the full
reasoning behind the ID-order caveat, not as a matter of routine.

## Which skill sets which status value

| Value | Set by |
|---|---|
| `not-started` | `define-task` (when drafting a new task) |
| `planned` | `define-task` (end of drafting, task-review gate pending) |
| `in-progress` | `implement-task` (implementation begins) |
| `done` | `propagate-context` (only after its completion-review is approved) |
| `blocked` | any agent, from any active state |

No skill sets `reviewing` — the two-gate lifecycle has no `reviewing`
status. `validate-work` and `review-work` are the two internal checks
of the `task-completion-review` gate, not status setters.

Each skill's own procedure already tells you what status to set at its
own steps — use this table to cross-check, not as your first source
when actively transitioning a status yourself.

## Where each value lives

A root task's Status lives exclusively in `.ai/tasks/tasks.md`. A
subtask's Status lives in the parent task file's Subtasks table.
Never duplicated across two of these for the same item, and never
written into `.ai/info.md` — that file holds Policy only
(`workflow.md §2`, §10).

## ID order ≠ execution order, in full

A replan can insert a task that logically belongs earlier but still gets
the next-highest ID (IDs are sequential and never reused or renumbered,
per `workflow.md §3`'s Naming rule). Resolve "first/next task" against
the parent task's Subtasks table or `tasks.md`'s Depends-on and Status
columns — no unmet dependencies, Status `planned` — not the lowest ID.

This matters in practice: "implement the first task" or "plan the next
task" reads as precise but is genuinely ambiguous once any replanning
has happened, since the newest-ID item may be exactly the one that
needs to happen first. Naming the task explicitly by ID or title avoids
an agent guessing wrong and building on top of the wrong plan. Ask
rather than guess if it's still ambiguous after checking Depends-on
and Status.
