---
name: build-context-full
description: Full-profile skill to populate .ai/context/ for a project that's unbootstrapped or has little context yet — a listing-only assumption pass, human-annotated review, then a batch-sized, status-tracked iteration that reads real files and builds context/ until the queue is empty. Not for propagating knowledge after a task/phase completes — see propagate-context. Requires .ai/info.md and .ai/context/context.md to already exist.
---

# Skill: build-context-full

This skill performs the **context** operation, survey half — see also
`propagate-context` for the propagation half
([.ai/workflow/workflow.md §10](.ai/workflow/workflow.md#10-operation-contracts)
covers what "operation" means and where authority comes from). This
one builds context by surveying an existing codebase, not by
propagating what a completed task/phase learned.

- **Can:** survey the codebase; write `.ai/context/*.md`.
- **Must:** get human review of `context.temp.md`'s assumptions
  before `.iterate` reconciles them into real context files; never
  delete an `[ASSUMPTION]`/`[QUESTION]` line unilaterally.
- **Should not:** copy task history; duplicate info; record
  reasoning.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for context building.

## When to use

A project is bootstrapped (`.ai/info.md`/`.ai/context/context.md`
already exist) but `.ai/context/` is thin relative to the actual
codebase — freshly bootstrapped onto an existing project, or a project
that's grown without `context/` keeping up. Not a required step of
bootstrap; invoked when the human wants context built up deliberately
rather than only accumulating through `propagate-context`'s
task/phase-completion path.

Three sub-operations, in order — `.assess` once, `.plan` once (after
human review of `.assess`'s output), `.iterate` repeatedly until done.

## build-context.assess — listing-only assumption pass

**Inputs:** the project's file/directory structure only — `tree`,
`find`, or `ls`, recursively. **Never `cat`/Read any file's contents
in this sub-operation** — if the temptation is to open a file to "just
check," stop; that belongs in `.iterate`, not here.

1. Run a recursive directory listing of the project, excluding
   `.git/`, `.ai/workflow/` (the submodule), and any build/dependency
   directory inferable from its name alone (`node_modules/`, `dist/`,
   `.venv/`, and similar) — inferred, never opened to confirm.
2. From names, extensions, and structure alone, write
   `.ai/context/context.temp.md` (copy
   [`.ai/workflow/templates/context-temp-template.md`](.ai/workflow/templates/context-temp-template.md)
   there first if it doesn't exist yet) with:
   - **Purpose/mission** — inferred, each distinct claim its own
     `[ASSUMPTION]` line.
   - **Architecture/module breakdown** — same, one `[ASSUMPTION]` line
     per claim, not a paragraph mixing several.
   - **Open questions** — anything genuinely unclear from structure
     alone, its own `[QUESTION]` line. Don't fold a question into an
     assumption just because they're related.
3. Commit: stage `.ai/context/context.temp.md`; the message should say
   this is the assumption pass (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
   Stop — tell the human `context.temp.md` is ready for review: they
   may add `[HUMAN]` lines confirming, correcting, or commenting on
   anything, but must **never delete an `[ASSUMPTION]` or
   `[QUESTION]` line, even a wrong one** — the record of what was
   assumed has to survive correction; `.iterate` reconciles it into
   real `context/*.md` content once the relevant files are actually
   read. This isn't a plan-review gate — no Status changes here — just
   a stop-and-wait for input before `.plan` runs.

## build-context.plan — iteration plan from assumptions

**Precondition:** `.ai/context/context.temp.md` exists (from
`.assess`, possibly human-annotated). If it doesn't, run `.assess`
first — don't skip ahead.

1. Read `.ai/context/context.temp.md` in full, including any
   `[HUMAN]` annotations.
2. Ask the human for the batch size (how many files to read per
   `.iterate` call) if not already stated.
3. Order the real file-read list: entry points and config/manifest
   files first (package manifests, main/index files, `README`) —
   these correct or confirm the most assumptions per file read — then
   the rest, grouped by the module breakdown `context.temp.md`
   inferred.
4. Write `.ai/context/build-plan.md` (copy
   [`.ai/workflow/templates/context-build-plan-template.md`](.ai/workflow/templates/context-build-plan-template.md)
   there first if it doesn't exist yet): the ordered file list, one
   row each, Status `queued`; the batch size; a link back to
   `context.temp.md`.
5. Commit: stage `.ai/context/build-plan.md`; the message should say
   the iteration plan was drafted (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
   Report the plan and the first batch, ready for `.iterate`.

## build-context.iterate — read a batch, build context/, repeat

**Precondition:** `.ai/context/build-plan.md` exists with at least one
`queued` row.

1. Take the next batch-size count of `queued` files from
   `build-plan.md`, in order.
2. Read each file in the batch in full.
3. For each file: reconcile it against `context.temp.md`'s
   assumptions — confirm, correct, or flag a discrepancy — and write
   or update the relevant `.ai/context/*.md` file(s). Group by
   module/domain, not one file per source file — a `context/` file
   should read as "everything about this architectural layer or
   feature-level concept," not as a per-source-file mirror. Update
   `context/context.md`'s table for every file touched, in the same
   step.
4. Set each processed file's row to `read` in `build-plan.md`.
5. Commit: stage the updated `.ai/context/*.md` file(s),
   `context.md`'s table, and `build-plan.md`'s Status column changes
   from this batch; the message should say which files were processed
   (see
   [.ai/workflow/workflow.md §12](.ai/workflow/workflow.md#12-commit-discipline)).
6. If `build-plan.md` still has `queued` rows: stop and report
   progress (X read, Y queued) — ready for the next `.iterate` call,
   not continued automatically in the same turn; batch size is the
   human's pacing control, not a suggestion to auto-continue. If the
   queue is now empty: report completion, and ask whether
   `context.temp.md` should be archived or deleted now that its
   assumptions have been reconciled into real `context/` content —
   never delete it unilaterally.

## Output

- `build-context.assess` — `.ai/context/context.temp.md`.
- `build-context.plan` — `.ai/context/build-plan.md`.
- `build-context.iterate` — updated `.ai/context/*.md` files and
  `context.md`'s table, plus `build-plan.md`'s Status column, every
  call.
