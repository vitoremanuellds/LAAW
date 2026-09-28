# LAAW — Local AI Agent Workflow

LAAW is a workflow for local AI agents running on limited hardware. It targets models of 9b–35b with a 64k token context window, and structures the agent's work into small, reviewable, human-gated steps so a small model can reliably work on a codebase.

- **Plan before code.** Every task gets a plan file that you approve before implementation starts.
- **Human gates.** You approve the plan, the implementation, and the propagated context. The agent never skips a gate.
- **Deviations are recorded.** Anything that deviates from the approved plan is noted in the task file.
- **Context propagates.** What a task creates or changes is written back into the project's context files (a small wiki the agent reads before working).
- **Files stay small.** Files over 100 lines are split, so the agent only ever loads what it needs.

## Repository contents

| File | Purpose |
|---|---|
| `laaw.py` | CLI to bootstrap LAAW into a project |
| `workflow.md` | Condensed workflow reference, read by the agent at the start of every session |
| `skills/` | The workflow skills: `plan-task`, `implement-task`, `propagate-context` |
| `prompt.md` | The full specification this project is built from |

## Bootstrap a project

From this repository:

```sh
# Copy the workflow files into <project>/.ai/workflow/, create the
# .ai/tasks/ and .ai/context/ skeleton, and git-ignore .ai/tasks/
./laaw.py sync workflow /path/to/project
# (path is optional — defaults to the current directory)
```

This creates:

```
project/
└── .ai/
    ├── workflow/workflow.md   # the agent's workflow reference
    ├── tasks/index.md         # empty task index (git-ignored)
    └── context/index.md       # empty context index
```

### Install the skills

```sh
# Copy the skills wherever your agent picks them up from
./laaw.py sync skills /path/to/project/.agents/skills
# or, for a global installation:
./laaw.py sync skills ~/.agents/skills
```

## Tell the agent about the workflow

For the workflow to actually be used, the agent needs to know to read `workflow.md`. Add a section to the project's `AGENTS.md` (create it if it does not exist):

```markdown
## Workflow

This project uses LAAW. Before doing any task work, read
`.ai/workflow/workflow.md` and follow it. For planning, implementation, and
context propagation, use the `plan-task`, `implement-task`, and
`propagate-context` skills.
```

Adjust the paths if you installed the skills somewhere else.

## How a task flows

1. **Plan** — you ask to plan a task. The agent registers it in `.ai/tasks/index.md` and writes the plan file. You iterate until the plan is good.
2. **Implement** — you ask to implement it. The agent checks dependencies, implements, and you iterate until the implementation is good. Deviations from the plan are recorded.
3. **Propagate context** — the agent writes what the task created back into `.ai/context/` (or into the supertask's staging section, for subtasks). You approve it.

Big tasks become **supertasks**: one folder with a `task.md` and separate subtask files, each planned and implemented one at a time (you can ask to plan several in advance). Subtask context lands in the supertask's `New info` section and is moved into the context files when all subtasks are done.

### Task statuses

Every task moves through: `not-planned` → `planning` → `in-progress` → `propagating-context` → `done`. A task's dependencies must be `done` before it can be implemented.

## Git

- `.ai/tasks/` is git-ignored by default — plans are working documents, not repo content. `sync workflow` adds the entry for you.
- `.ai/context/` **should be committed** — it is the project's documentation for agents, and sharing it means a fresh agent session (or another person's agent) starts with the right context.
