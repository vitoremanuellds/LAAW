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
| `not-planned` | `define-phase` (stubbing a bare phase title, or every remaining plan step on a phase's first `define-task` invocation) |
| `awaiting-plan-review` | `define-phase`/`define-task`, end of drafting |
| `plan-approved` | Whichever skill's ending receives approval — see `workflow.md §5`'s unlocking-≠-starting rule |
| `in-progress` | `define-task` (phase, task planning begins) / `implement-task` (task, implementation begins) |
| `validating` | `validate-work` |
| `reviewing` | `review-work` — a different check than plan-review, see below |
| `complete` | `propagate-context`, only after its completion-review is approved |
| `blocked` | any agent, from any active state |

Each skill's own procedure already tells you what status to set at its
own steps — use this table to cross-check, not as your first source
when actively transitioning a status yourself.

`define-task`'s first invocation per phase stubs every remaining plan
step at `not-planned` at once (cheap — titles only), then fully drafts
whatever's actually in scope for that invocation. This applies to the
phase-linked path only — an orphan task has no phase Plan to stub
from; it's drafted directly, one request at a time.

## Where each value lives — phase-linked vs. orphan vs. phase

A phase-linked task's Status lives exclusively in its owning phase
file's own Tasks table. An orphan task's Status lives in
`.ai/tasks/tasks.md`. A phase's own Status lives in
`.ai/phases/phases.md`. Never duplicated across two of these for the
same item, and never written into `.ai/info.md` — that file holds
Policy only (`workflow.md §2`, §10).

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
Status columns (or `tasks.md`'s, for an orphan task); resolve
"first/next phase" the same way against `phases.md`'s Depends-on and
Status columns — no unmet dependencies, Status
`awaiting-plan-review`/`plan-approved` — not the lowest ID.

This matters in practice: "implement the first task" or "plan the next
phase" reads as precise but is genuinely ambiguous once any replanning
has happened, since the newest-ID item may be exactly the one that
needs to happen first. Naming the task/phase explicitly by ID or title
avoids an agent guessing wrong and building on top of the wrong plan.
Ask rather than guess if it's still ambiguous after checking
Depends-on and Status.
