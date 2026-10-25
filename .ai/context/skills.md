# Skills

LAAW ships five skills under `skills/`, synced into a project with `laaw sync skills <path>`.

Core (part of the task loop):

| Skill | When | What it does |
|---|---|---|
| `plan-task` | User asks to plan | Registers the task in state (`laaw task register`) and creates its plan file via the CLI (`laaw task plan`); decides simple vs supertask; planning a subtask sets the supertask `in-progress`; context before codebase |
| `implement-task` | User asks to implement an approved task | Checks dependencies (`laaw task deps`), implements, records exactly one progress note per completed Step plus deviation notes (`laaw task note`), handles cancellation (`laaw task cancel`), runs validations; `laaw task propagate <id>` only after explicit user approval (validations are not approval) |
| `propagate-context` | After implementation is approved | Writes the task's information back into `.ai/context/`, or as tagged notes on the supertask for subtasks; final propagation moves staged notes into the context files |

Optional (standalone, not part of the task loop):

| Skill | When | What it does |
|---|---|---|
| `bootstrap-project` | Starting LAAW on a new project | Interviews the user (mission, stack, architecture, design, paradigms), writes the answers to `.ai/context/`, optionally registers a roadmap of `not-planned` tasks in state |
| `gather-context` | Building context for an existing project | Tree-only analysis, user Q&A gate, ordered read queue in `.ai/.queue.md`, then writes `.ai/context/` |

Both optional skills write only to `.ai/`; they never plan tasks or touch project code.
