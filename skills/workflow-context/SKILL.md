---
name: workflow-context
description: Use this skill to propagate reusable knowledge into context files after a task or phase completes, and to finalize status (mark complete in the owning task table, clear info.md). At full/medium, only after its completion-review gate is already approved via workflow-review. At lite, this operation itself is where the single combined task-completion gate stops — see workflow.md §14. Not for task history, temporary implementation details, or internal reasoning.
---

# Skill: workflow.context

Operation for the **Context Agent**. Contract:
[.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-agent-contracts). Three
sub-operations — use whichever matches the trigger.

**All `.ai/`-artifact paths below are relative to the project root,
not to this skill file — write the full `.ai/...` path.** Status
values you set here (`complete`) are one of exactly eight in a closed
enum — see
[.ai/workflow/workflow.md §11](.ai/workflow/workflow.md#11-status-the-fast-pointer-and-the-permanent-record)
for the full list; never invent one not on it.

## workflow.context.task — on task completion

**Precondition at `full`/`medium`:** the task's Status must already be
`reviewing` with an approved `task-completion-review` (see
[workflow-review](.ai/workflow/skills/workflow-review/SKILL.md)) — this operation
finalizes an already-approved review, it doesn't substitute for one.
If Status isn't `reviewing` with approval confirmed, that gate hasn't
passed yet; don't mark complete regardless of how the task looks.

**At `lite`:** there is no prior approval to check — `workflow-review`
hands off its findings directly, without stopping (§14). This
operation is where the single combined `task-completion` gate actually
stops: before step 4 below, present the validation result +
review findings + any context change from step 3 together as one
report, and stop for `task-completion` — see `.ai/info.md` (read
fresh). Only proceed to step 4 once that comes back approved; a
"changes requested" outcome returns to the implementation loop instead
of continuing.

1. Inspect what the task actually produced.
2. Ask: does anything discovered here matter to *other tasks* (at
   `full`/`medium`, other tasks in this phase; at `lite`, other tasks
   in the project — there's no phase grouping)? If not, skip to step 4
   — not every task needs this.
3. If yes, update the persistent fact in the right place for your
   profile (never the task's history or reasoning): at `full`, the
   owning phase file's own Context section — and if the fact is
   general enough to matter beyond this one phase, `.ai/context/`
   instead (new or existing file; update its row in
   `.ai/context/context.md`'s table in the same step) — see the
   propagation rule in
   [.ai/workflow/workflow.md §9](.ai/workflow/workflow.md#9-context-propagation).
   At `medium`, `techstack.md`'s own `## Context` subsection (no
   phase/project distinction to make — one merged location, no index
   row to maintain). At `lite`, `project.md`'s Techstack `## Context`
   subsection (same single-location rule).
4. Set the task's Status to `complete` in its owning Tasks table (the
   phase file's at `full`/`medium`, `.ai/project.md`'s Roadmap table at
   `lite`) — this is the actual "task complete" marker. Clear it as
   the active task in `.ai/info.md`'s Status section. At `full`/
   `medium`, leave `Active phase` alone if the phase itself isn't done;
   at `lite` there's no `Active phase` to manage.

## workflow.context.phase — reconciling during a phase

**Not applicable at `profile: lite`** — no phase layer exists (§14).

Run periodically or when a task's context-agent step flags something
phase-wide. Ensure the phase file's own Context section still
accurately describes shared architecture, constraints, and task
relationships as the phase progresses.

## workflow.context.project — on phase completion

**Not applicable at `profile: lite`** — no phase layer and no
phase-completion ceremony exists at that tier; a project small enough
to run at `lite` finishes when its flat task list runs out of
`not-planned` rows, with no separate project-completion gate (§14).

**Precondition at `full`/`medium`:** the phase's Status must already be
`reviewing` with an approved `phase-completion-review`, and all tasks
in the phase already `complete` — same principle as the task-level
precondition above.

1. Read the finished phase file's own Context section.
2. Ask: does this remain relevant *beyond this phase*? Only
   sufficiently general, persistent knowledge qualifies.
3. If yes, at `full`: update the relevant file under `.ai/context/`
   (new or existing), and update its row in `.ai/context/context.md`'s
   table (Description, Status, Relations) in the same step. At
   `medium`: update `techstack.md`'s own `## Context` subsection
   instead — no index row to maintain.
4. Set the phase's Status to `complete` in
   `.ai/constitution/roadmap.md` — this is the actual "phase complete"
   marker. Clear `.ai/info.md`'s Status section entirely (both `Active
   phase` and `Active task` go back to `—`) unless a next phase is
   already starting in the same breath.
5. Commit (see
   [.ai/workflow/workflow.md §13](.ai/workflow/workflow.md#13-commit-discipline)).

## Never propagate

Task history, temporary implementation details, information already
recorded elsewhere, internal reasoning, progress reports. See
[.ai/workflow/workflow.md §9](.ai/workflow/workflow.md#9-context-propagation).

## Output

Updated context at the appropriate level only. At `full`: a phase
file's own Context section, or a file under `.ai/context/` (plus its
row in `.ai/context/context.md`'s table) — don't write to more than
one level per invocation unless the fact genuinely applies at both. At
`medium`: `techstack.md`'s `## Context` subsection. At `lite`:
`project.md`'s Techstack `## Context` subsection.

The relevant Status set to `complete` in its owning Tasks table (the
phase file's or `.ai/constitution/roadmap.md` at `full`/`medium`,
`.ai/project.md`'s Roadmap table at `lite`), and `.ai/info.md`'s Status
section updated to match. At `lite`, also the `task-completion` gate's
approval outcome — this operation is where it was requested and
resolved.
