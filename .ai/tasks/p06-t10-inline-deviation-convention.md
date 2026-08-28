# P06-T10: Define an inline in-task-file deviation convention; update §6

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
`workflow.md` §6 currently describes a deviation as living in its own file
(`tasks/p01-t03-{name}-deviation.md`, next to the task it concerns), carrying a
`[HUMAN]` comment: "Maybe we can simplify it, leave it inside the task markdown
file." No such separate deviation file has ever actually existed in this repo's own
history (per the phase's repo survey); the lighter-profile templates already use an
inline `**Deviation (if any):**` field instead
(`templates/lite-project-template.md`, `templates/minimal-tasks-template.md`) — a
usable precedent for Full. This task replaces the separate-file mechanism with an
inline `## Deviations` subsection appended to the task file itself, defined as a
task-file convention in `define-task-full` (which already owns and documents the
task file's structural conventions, e.g. the `(flexible: ...)` step-marking
convention), and updates §6's text to match.

**A second, separate `[HUMAN]` comment sits a few lines below this one in §6**
("Maybe we can remove this part from here, as it is kind of a rule that should live
inside the skill" — on the Task-level/Phase-level/Project-level escalation bullet
list). That comment is about a different concern (whether the escalation-routing
rule itself belongs in `workflow.md` or in a skill) and isn't part of decision 10 —
the Plan item scopes this task to the file-vs-inline mechanism only. Left
unaddressed here, same as the still-open `info.md` Status-naming gap noted elsewhere
in this phase; worth its own decision if the human wants it done.

## Implementation

### Objective

Replace §6's separate-deviation-file mechanism with an inline `## Deviations`
task-file subsection, defined as a `define-task-full` task-file convention, keeping
the same fields and lifecycle the separate-file version already used.

### In scope

- `workflow.md` §6: the "File: ... Lifecycle: ..." paragraph and its `[HUMAN]`
  comment.
- `skills/define-task-full/SKILL.md`: one new convention paragraph describing the
  `## Deviations` subsection format.

### Out of scope

- §6's Task-level/Phase-level/Project-level escalation bullet list and its own
  `[HUMAN]` comment — a separate, unassigned concern (see Context above).
- §6's "Adding new, working-as-planned scope..." paragraph — already trimmed by
  `P06-T05`; unrelated to this task.
- `implement-task-full`/`review-work-full` — both already say "raise a deviation,
  see workflow.md §6" without naming a file mechanism; no format-specific detail to
  update there, since §6 → `define-task-full`'s convention is enough to resolve the
  "how."
- `templates/lite-project-template.md`/`templates/minimal-tasks-template.md` —
  read-only precedent; not edited by this task.

### Files to modify

- `workflow.md` — §6.
- `skills/define-task-full/SKILL.md` — add the Deviations convention.

### Steps

1. In §6, replace:

   ```
   File: `tasks/p01-t03-{name}-deviation.md`, next to the task it
   concerns. Lifecycle: `OPEN → ADDRESSED → INCORPORATED`, then delete —
   the fact must already live in the plan, implementation, or an ADR.

   [HUMAN] Maybe we can simplify it, leave it inside the task markdown file.
   ```

   with:

   ```
   Recorded inline, as a `## Deviations` subsection appended to the task file
   itself — never a separate file. Lifecycle: `OPEN → ADDRESSED → INCORPORATED`,
   then delete the entry — the fact must already live in the plan,
   implementation, or an ADR. See `define-task-full`'s task-file conventions for
   the exact subsection format.
   ```

   (flexible: exact prose — binding: "never a separate file," the lifecycle
   states, and the pointer to `define-task-full` must all be present.)
2. In `skills/define-task-full/SKILL.md`, insert a new unnumbered paragraph between
   the end of the numbered Procedure (after step 9) and the `## Output` heading:

   ```
   **Deviations convention:** a deviation
   ([.ai/workflow/workflow.md §6](.ai/workflow/workflow.md#6-deviations)) is
   recorded inline in the task file, not a separate file — append (or update) a
   `## Deviations` subsection with one entry per deviation: `Expected /
   Discovered / Why it fails / Proposed fix / Replan? (task/phase/project)`,
   lifecycle `OPEN → ADDRESSED → INCORPORATED`, then delete the entry once its
   fact already lives in the plan, implementation, or an ADR. This subsection
   doesn't exist in a freshly drafted task file — you don't create it while
   planning; it's added later, by whichever operation actually raises the
   deviation.
   ```

   (flexible: exact prose — binding: the field list, the lifecycle states, "not a
   separate file," and the note that this subsection isn't created at draft time
   must all be present.)

### Dependencies

`P06-T01` (already complete — no direct content overlap, listed as a dependency in
the phase file's Tasks table).

### Expected result

§6 describes deviations as living inline in the task file, with no reference to a
separate `-deviation.md` file; `define-task-full` documents the exact subsection
format as one of its task-file conventions.

### Automatic validations

- `grep -rn "\-deviation.md" workflow.md` returns nothing.
- `grep -n "## Deviations" skills/define-task-full/SKILL.md` returns one match.
- `grep -c "\[HUMAN\]" workflow.md` drops by exactly 1 (only the file-vs-inline
  comment; the escalation-bullet-list comment stays, per Out of scope).

### Manual validations

- Confirm §6 reads as a complete, self-contained rule — what a deviation is, how
  it's recorded, its lifecycle — with no dangling reference to the removed file
  mechanism.
- Confirm `define-task-full`'s new convention paragraph sits naturally alongside the
  skill's other task-file conventions (e.g. the `(flexible: ...)` marking
  convention), not as a stray afterthought.
- Confirm the untouched escalation bullet list (Task-level/Phase-level/Project-level)
  still reads correctly right after the rewritten paragraph — it never mentioned the
  file mechanism directly, so it shouldn't need wording changes.
