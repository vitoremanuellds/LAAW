# Lifecycle Diagrams

Referenced from [workflow.md §4](workflow.md#4-lifecycle). Read this file
only if the compressed flow there isn't enough detail for the current
operation.

## Implementation Loop (per task)

```
Read Task
    ↓
Read Task Context
    ↓
Read Required References
    ↓
Review Implementation Plan
    ↓
Implement
    ↓
Run Task Validation
    ↓
Problem?
 ┌──┴──┐
No     Yes
│       │
↓       ↓
Done   Can fix within task?
        ┌────┴────┐
       Yes        No
        │          │
        ↓          ↓
     Rework     Deviation → see deviations.md
```

Do not silently expand task scope. If the intended work changes
materially, stop and replan.

## Task Completion

```
Implementation → Validation → Review → Context Evaluation → Task Complete
```

## Phase Completion

```
All Tasks Complete
        ↓
Phase Validation
        ↓
Phase Review
        ↓
Phase Context Reconciliation
        ↓
Project Context Reconciliation
        ↓
Phase Complete
```

## Full Project Flow

```
Define Constitution → Constitution Review
        ↓
Define Phase → Requirements → Phase Plan → Phase Validations → Phase Review
        ↓
Generate Tasks → Task Context → Task Implementation → Task Review
        ↓
Implement → Validate → Review → Evaluate Context → Task Complete
        ↓
   More tasks? → yes: next task / no: Phase Validation
        ↓
Phase Review → Reconcile Phase Context → Reconcile Project Context
        ↓
Phase Complete
        ↓
   More phases? → yes: next phase / no: Project Complete
```

Who performs each review/approval step is defined per gate in
[policy.md](policy.md), not here.
