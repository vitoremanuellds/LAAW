# Workflow docs — workflow.md, skills, README

## Modules

- `workflow.md` (repo root) is the source of truth for the LAAW workflow doc; `.ai/workflow/workflow.md` is a synced copy refreshed with `laaw sync workflow <path>`; both are byte-identical after sync.
- Structure: Principles (5), Invocation, Layout, State (tasks.json + generated tables, IDs/slugs, Statuses), Task files, Context files, Rules, Loops (simple task + supertask), Skills.
- `skills/` — the five skills; synced into a project with `laaw sync skills <path>`. The three core skills (`plan-task`, `implement-task`, `propagate-context`) drive the CLI-backed workflow; the two optional ones (`bootstrap-project`, `gather-context`) handle bootstrap and never touch task state.
- `README.md` — project entry point for new users: documents the `laaw/` package, `bin/` wrappers, the Python 3 requirement, and invocation (`laaw` on PATH or `python -m laaw`).
- `.ai/context/skills.md` — committed context file documenting the five skills.

## Conventions

- The workflow doc describes the CLI-backed workflow: `tasks.json` is the source of truth; `tasks.md`, `subtasks.md`, `notes.md`/`notes_<n>.md` are generated and readonly; `task.md` is model-owned (scaffolded by `laaw task plan`; all task files have identical sections).
- Invocation: `laaw` may be on PATH (`bin/laaw` / `bin/laaw.ps1`, requires Python 3); otherwise `python -m laaw` with the checkout root on cwd/PYTHONPATH. Commands are non-interactive and fail loud.
- Notes are CLI-owned state, not part of `task.md`: `laaw task note <id> --tag <tag> --text "..."`, rendered into `notes.md`. Supertask subtask context is staged as tagged notes on the supertask; there is no separate staging file (`new-info.md` is retired from the documented workflow).
- Loops name the CLI commands at each step: register, plan, implement, propagate, done, cancel, note (one progress note per completed Step, deviation for plan changes), dependents. A note records what the implementation created as it happened — progress per step, deviations, decisions/gotchas worth keeping; notes are CLI-owned state rendered into `notes.md`, not prose in `task.md`.
- plan-task: register = `laaw task register`, plan file = `laaw task plan <id>`; IDs are CLI-computed — the agent never derives them (no "compute the ID" step); subtask rows must already exist in the supertask's state; plan content sections per workflow.md (no Notes section in task.md).
- implement-task: dep check = `laaw task deps`, start = `laaw task implement`; exactly one progress note per completed Step (`--tag progress`), never batched or skipped; deviations recorded in task.md Notes + as `--tag deviation` notes; cancellation = `laaw task cancel` (CLI reports dependents); re-pointing deps = `dep-add`/`dep-remove`; `laaw task propagate` only after the user's explicit approval — passing validations is not approval.
- propagate-context: subtask → tagged notes on the supertask via `laaw task note <supertask-id>` (no staging file); simple task → context files; final propagation reads the supertask's staged `notes.md` and distributes into `.ai/context/`; approval → `laaw task done`.
- bootstrap-project: skeleton check `.ai/workflow/`, `.ai/tasks/`, `.ai/context/index.md`; if missing → run `laaw sync workflow <project>` from the LAAW checkout; roadmap registered into state via `laaw task register --name [--desc] [--deps]` (→ `not-planned`); never creates plan files or task folders; writes only to `.ai/context/`, state changes via the CLI.
- gather-context: same skeleton check; tree-only analysis, user Q&A gate, ordered read queue in `.ai/.queue.md`, then writes `.ai/context/`.
- README bootstrap section: `laaw sync workflow [path]` / `laaw sync skills <path>`; `.ai/tasks/` starts empty — the CLI creates `tasks.json` on first `register`; all other files under `.ai/tasks/` are generated from state. The agent hook is automatic: `sync workflow` ensures a `Workflow` section in the project's `AGENTS.md` (created/appended/idempotent); the README still documents adding it by hand for non-default layouts.
- README "How a task flows": state in `tasks.json` (source of truth, written only by the CLI), tables and notes generated/readonly, model writes only `task.md`, deviations as notes, subtask context staged as tagged notes on the supertask.

## Decisions and gotchas

- Deduplication: each rule appears verbatim in exactly one place — the file-size threshold in Principle 5 (Splitting and Simple-vs-supertask point to it), sizing triggers + hard cap only in Sizing. The skills do not restate these rules; they cross-reference workflow.md (threshold number, sizing text appear zero times verbatim in the five skills).
- Task files table dropped the `When` column and the Notes row: all task.md files are identical, and notes live in CLI-rendered `notes.md`, not in task.md.
- Principle 5: any `.ai/` file larger than ~1500 words (≈2k tokens ≈ one read at the session's context budget) is split; a file between the threshold and its next natural break is fine as long as it still reads in one pass. Split pieces keep a descriptive name chosen by the agent, live in the same folder, and the entry point links to them one-way — there is no base/att naming grammar. Exceptions: `workflow/workflow.md` itself (session entry point, always read in full; currently ~1770 words, above the threshold but exempt) and project code outside `.ai/`. Note: `.ai/context/cli.md` is ~1890 words, slightly over the threshold — a candidate for a future split.
- User-requested deviation: plan-task's "Compute the ID" step was removed because the CLI computes IDs for the agent.
