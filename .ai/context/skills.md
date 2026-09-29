# Skills

LAAW ships five skills under `skills/`, synced into a project with `laaw.py sync skills <path>`.

Core (part of the task loop):

| Skill | When | What it does |
|---|---|---|
| `plan-task` | User asks to plan | Registers the task, creates the plan file, decides simple vs supertask, context before codebase |
| `implement-task` | User asks to implement an approved task | Checks dependencies, implements, records deviations, handles cancellation, runs validations |
| `propagate-context` | After implementation is approved | Writes the task's information back into `.ai/context/` (or the supertask's `new-info.md`) |

Optional (standalone, not part of the task loop):

| Skill | When | What it does |
|---|---|---|
| `bootstrap-project` | Starting LAAW on a new project | Interviews the user (mission, stack, architecture, design, paradigms), writes the answers to `.ai/context/`, optionally registers a roadmap of `not-planned` tasks |
| `gather-context` | Building context for an existing project | Tree-only analysis, user Q&A gate, ordered read queue in `.ai/.queue.md`, then writes `.ai/context/` |

Both optional skills write only to `.ai/`; they never plan tasks or touch project code.
