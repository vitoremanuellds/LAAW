# Task/phase output-structure conventions

Established during P03. Applies to any future edit to
`define-task-full`, `define-phase`, or how their output is judged —
not itself a restatement of the rules those skills already state (see
each skill file for the actual instructions).

## Section order

**Task file** (`define-task-full`'s Implementation section): Objective
→ In scope → Out of scope → Files to modify → Files to create → Steps
(each flexible detail marked inline, e.g. `(flexible: ...)`; unmarked
is binding) → Pseudocode (optional) → Dependencies → expected result →
Automatic validations → Manual validations.

**Phase file** (`define-phase`'s section list): Context → In scope →
Out of scope → Requirements → Plan → Automatic validations → Manual
validations → Tasks (table).

In scope/Out of scope always sit right after the section that
motivates them (Objective for tasks, Context for phases) — before any
mechanical detail (Files, Steps, Plan). Automatic/Manual validations
always replace a single undifferentiated "validation instructions" or
"Validations" list — never merge them back into one.

## Why the flexible-detail marker is task-only

`(flexible: ...)` marks a Steps detail an implementer may adjust
without it counting as a deviation from the plan (`workflow.md §6`).
It doesn't exist at phase granularity: a phase's Plan section is
required not to read like a task list (`workflow.md §4`) — it has no
literal implementation steps to mark flexible or binding in the first
place. Don't invent a phase-level equivalent; that granularity is
task-only by design.

## Where the operational rules actually live

- The section-order rules above: `define-task-full/SKILL.md` step 4,
  `define-phase/SKILL.md` step 2.
- The flexible-marker's consequence during implementation:
  `implement-task-full/SKILL.md` step 4, `workflow.md §6`.
- "Plan one phase at a time, no pre-existing roadmap detail required":
  `workflow.md §5`, "Starting without a plan."
- The completion-time "what's next?" questions: `propagate-context/SKILL.md`,
  `propagate-context.task` step 5 and `propagate-context.project` step 6.
