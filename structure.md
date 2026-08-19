# Directory Structure

Referenced from [workflow.md](workflow.md).

```
.ai/
├── index.md              Navigation entry point
├── workflow.md            Protocol (this system)
├── policy.md               Execution policy
├── state.md                 Current state (small, not historical)
├── structure.md              This file
├── lifecycle.md               Full lifecycle diagrams
├── deviations.md               Deviation rules
├── agents.md                    Agent contracts
│
├── constitution/
│   ├── mission.md
│   ├── techstack.md
│   └── roadmap/
│       ├── roadmap.md
│       └── p01-phase-name.md
│
├── project-context/
│   ├── context.md
│   ├── structure.md          (project structure, not workflow structure)
│   └── modules/
│       └── auth.md
│
├── decisions/
│   ├── _template.md
│   └── d01-decision-name.md
│
└── phases/
    └── p01-phase-name/
        ├── context.md
        ├── requirements.md
        ├── plan.md
        ├── validations.md
        └── tasks/
            └── p01-t01-task-name/
                ├── context.md
                └── implementation.md
```

## Link Rule

Every link is relative to the file that contains it — never to `.ai/`
root or repo root.

```
.ai/phases/p01-auth/tasks/p01-t01-model/context.md
    → ../context.md                     (phase context)
    → ../../../project-context/modules/auth.md
```

This keeps artifacts movable and lets an agent navigate without knowing
the repository root.

## Naming

- Phase directories: `p{NN}-{kebab-name}/`
- Task directories: `p{NN}-t{NN}-{kebab-name}/`
- Decisions: `d{NN}-{kebab-name}.md`
- IDs are sequential and never reused (see [workflow.md §12](workflow.md#12-ids)).
