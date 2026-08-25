# Status detail — who sets what, and the distinctions that get conflated

Referenced from [`../workflow.md §11`](../workflow.md#11-status-the-fast-pointer-and-the-permanent-record).
The enum itself, the fast-pointer/permanent-record split, and the
"never write a status word into `info.md`" rule are already fully
stated there. This file holds the lookup table and the extended
explanations — read it when you're actually unsure which skill sets a
given value, or need the full reasoning behind the ID-order caveat, not
as a matter of routine.

## Which skill sets which status value

| Value | Set by |
|---|---|
| `not-planned` | `create-constitution-full` (every phase, initially); `define-task-full` (every undrafted plan step, on first invocation per phase) |
| `awaiting-plan-review` | `define-phase`/`define-task-full`, end of drafting |
| `plan-approved` | Whichever skill's ending receives approval — see `workflow.md §5`'s unlocking-≠-starting rule |
| `in-progress` | `define-task-full` (phase, task planning begins) / `implement-task-full` (task, implementation begins) |
| `validating` | `validate-work-full` |
| `reviewing` | `review-work-full` — a different check than plan-review, see below |
| `complete` | `propagate-context`, only after its completion-review is approved |
| `blocked` | any agent, from any active state |

Each skill's own procedure already tells you what status to set at its
own steps — use this table to cross-check, not as your first source
when actively transitioning a status yourself.

`define-task-full`'s first invocation per phase stubs every remaining
plan step at `not-planned` at once (cheap — titles only), then fully
drafts whatever's actually in scope for that invocation.

## Plan-review vs. `reviewing` — same word, different check

Plan-review (`awaiting-plan-review`/`plan-approved`) checks a *plan*
before work begins; `reviewing` checks the *result* after
(`workflow.md §8`). Same word "review" surfaces in both — a plan
that's `awaiting-plan-review` has not had any implementation done
against it yet; a task/phase at `reviewing` has already been
implemented and validated, and is now being checked for coherence
before being marked complete. Don't conflate the two just because both
involve a human or agent looking at something and using the word
"review."

## ID order ≠ execution order, in full

A replan can insert a task — or a new phase — that logically belongs
earlier but still gets the next-highest ID (IDs are sequential and
never reused or renumbered, per `workflow.md §3`'s Naming rule).
Resolve "first/next task" against the phase file's Depends-on and
Status columns; resolve "first/next phase" the same way against
`roadmap.md`'s Depends-on and Status columns — no unmet dependencies,
Status `awaiting-plan-review`/`plan-approved` — not the lowest ID.

This matters in practice: "implement the first task" or "plan the next
phase" reads as precise but is genuinely ambiguous once any replanning
has happened, since the newest-ID item may be exactly the one that
needs to happen first. Naming the task/phase explicitly by ID or title
avoids an agent guessing wrong and building on top of the wrong plan.
Ask rather than guess if it's still ambiguous after checking
Depends-on and Status.
