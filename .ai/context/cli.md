# CLI — the LAAW package

The `laaw/` Python package (stdlib only, zero dependencies) owns all deterministic workflow state. It is run as `python -m laaw ...` or via the thin wrappers `bin/laaw` / `bin/laaw.ps1` (which set `PYTHONPATH` to the repo root resolved from their own location and forward all args).

## Layering

- `laaw/cli/` — presentation only: argparse tree + dispatch; one thin controller per command (`run(args) -> (message, exit_code)`). No state logic, no persistence imports.
- `laaw/core/` — orchestrators grouped by domain; own the transaction (load → validate → mutate → save+render):
  - `base.py` — `tasks_dir()`, `load_or_empty(tasks_dir)` (empty state if tasks.json missing), `save_and_render(state, tasks_dir)` (writes tasks.json + tasks.md + each supertask's subtasks.md + every task's notes files via `domain.notes.render_notes`), `Refuse` exception.
  - `lifecycle.py` — register, plan, implement, propagate, done, cancel.
  - `metadata.py` — rename, desc, dep-add, dep-remove, promote.
  - `notes.py` — add_note (append + re-render).
  - `query.py` — deps, dependents, check (read-only: load, compute, print; no save).
  - `sync.py` — sync_workflow(target), sync_skills(dest).
  - `render_cmd.py` — render() (regenerate all generated files from state; idempotent).
- `laaw/domain/` — pure logic over the model, zero IO: `status.py` (enums + transition table), `deps.py` (sibling scoping, cycles, unsatisfied, dependents), `render.py` (table markdown), `notes.py` (word caps, tag grouping, auto-split).
- `laaw/model/` — dataclasses (`Task`, `Subtask`, `Note`, `ProjectState`).
- `laaw/persistence.py` — the repository: the only module that touches disk.

Core functions take structured params and return `(message, exit_code)`; they raise `Refuse` on refusal (nothing written). Refusal is handled once in the dispatch wrapper (`cli/__init__.py`): catches `Refuse`, prints `refused: <reason>`, returns 1. Controllers never handle refusals themselves.

## Commands

- Lifecycle:
  - `task register --name [--desc] [--deps ...] [--subtask-of PARENT_ID]` — without the flag, adds a top-level task in `not-planned`; next id from state; unknown dep → refuse. With `--subtask-of`, appends a subtask row (`tNN.n`, status `not-planned`) to the parent's state; refuses unknown or non-supertask parents and out-of-scope deps. Neither kind creates any folder or files.
  - `task plan <id>` — transition check; accepts task or subtask IDs; creates the folder (top-level `<id>_<slug>/`, subtask `<parent>/<tNN.n>_<slug>/`) and scaffolds `task.md` (section headings only, from `TASK_MD_SECTIONS`) and empty `notes.md`; legal from not-planned, in-progress, propagating-context (re-plan). For a subtask the owning supertask's status is set to `in-progress`.
  - `task implement <id>` — transition check + deps gate (task or subtask ID): refuses listing `unsatisfied_deps`; resume edge from propagating-context.
  - `task propagate <id>`, `task done <id>` — transition check only.
  - `task cancel <id>` — transition check (task or subtask ID); prints dependents as blocked list (sibling subtasks included).
- Edit:
  - `task rename <id> --name` — task or subtask ID; only from `not-planned`/`planning`; moves the folder (subtask folders stay inside the parent folder), updates name; refuse if `in-progress`+.
  - `task desc <id> --desc` — any non-terminal; clamped to 180 chars.
  - `task dep-add <id> tXX` — task or subtask ID, any non-terminal; refuses on unknown/out-of-scope dep or cycle; warns when the new dep is not `done`.
  - `task dep-remove <id> tXX` — any non-terminal; refuses if the dep is not present.
  - `task promote <id>` — flips a top-level task from `simple` to `supertask`; pre-implementation only, like rename; refuses subtask IDs and tasks that are already supertasks. There is no demote: cancel and re-create instead.
  - `task note <id> --tag --text` — task or subtask ID; appends a tagged note (150-word cap enforced) to the task/subtask's state, re-renders notes files into its folder.
- Query:
  - `task deps <id>` / `task dependents <id>` — task or subtask ID; read-only reports; `--json` for machine output. `deps` exits 1 when the task is blocked.
  - `task check` — drift report: planning+ tasks and subtasks have task.md; top-level and subtask folders ↔ state match (orphan subtask folders flagged); deps reference existing ids; no cycles; scoping respected. Exits 1 on any drift.
- Bootstrap:
  - `sync workflow [path]` — copies `workflow.md` from the LAAW checkout into `<target>/.ai/workflow/`; creates `.ai/tasks/index.md` and `.ai/context/index.md` skeletons if absent; appends missing `.gitignore` entries (`.ai/tasks/`, `.ai/workflow/`) without duplicates.
  - `sync skills <path>` — copies each skill folder from the LAAW checkout's `skills/` into `<dest>` (re-running overwrites).
  - `task render` — regenerates every generated file (tasks.json, tasks.md, per-supertask subtasks.md, all notes files) from state.

Every command: load → validate (refuse before writing) → mutate → save → render all generated files → print result. Fail loud, no silent mutation. If `tasks.json` does not exist, the core layer starts from an empty `ProjectState`, so `register` works on first run.

## Model and rendering

- `Task.to_dict()` / `Task.from_dict()`: serialize a task; the `subtasks` and `notes` keys are present only when non-empty. `Subtask` and `Note` round-trip losslessly (`Subtask.notes` serializes like `Task.notes`).
- `ProjectState.to_dict()` / `from_dict()`: serialize the whole `tasks.json` document shape (`version` + ordered `tasks`).
- `next_top_level_id()` → `tNN` (zero-padded to 2, widens past 99); `next_subtask_id(parent)` → `tNN.N`.
- `slug(name, taken)` → kebab-case with collision auto-suffix `-2`, `-3`, …
- `add_task` raises `ValueError` on duplicate id; `find_task`/`find_subtask` raise `KeyError` when missing.
- `ProjectState.find_any(id)` → `Resolved(kind, parent_id, id, name, status)`: resolves a top-level task or a subtask by id (`parent_id` is None for top); every core orchestrator resolves IDs through it, so all ID-addressed commands accept `tNN.n`.
- `Task.notes: list[Note]` lives in the model and is serialized into tasks.json only when non-empty (mirrors the `subtasks` key). Notes are state, not files — rendering regenerates `notes.md`/`notes_<n>.md` from them on every save.

Rendering (`domain/render.py`, pure):

- `TABLE_HEADER` — shared column tuple: `ID | Status | Name | Description | Type | Dependencies`.
- `render_tasks_md(state)` → `GENERATED_HEADER`, `# Tasks`, one row per top-level task in state order; subtasks are NOT included; deps comma-joined, empty when none.
- `render_subtasks_md(task)` → `GENERATED_HEADER`, `# Subtasks of <id>`, same column shape over the supertask's subtasks (type rendered as `subtask`); a supertask with no subtasks renders a `(no subtasks)` marker line instead of a table.
- Both outputs are deterministic: same state in → byte-identical text out, trailing newline included.

Notes rendering (`domain/notes.py`, pure):

- `validate_note(note)` raises `ValueError` if a note exceeds 150 words; `core/notes.add_note` converts it to `Refuse` so the single refusal path covers cap violations and unknown tasks uniformly.
- `render_notes(notes)` groups notes by tag in `TAG_ORDER` (unknown tags fold into `other`), packs under the 600-word file cap, and auto-splits overflow into `notes_1.md`, `notes_2.md`, … in emission order. A tag whose content alone exceeds the cap gets its own numbered file(s); smaller tags share files. Every file starts with `GENERATED_HEADER`; `notes.md` links each overflow as `- notes_N.md (tags: <tag>)`.
- The 600-word file cap counts **note content only** — section headers (`## tag`) and markdown structure are excluded.

Status machine (`domain/status.py`, pure):

- `TRANSITIONS`: maps each `Action` to `{status it is legal from: resulting status}`; `None` as a key means "no current status" (only `register`).
- `can_transition(current, action) -> bool`; `resulting_status(current, action) -> Status` (raises `ValueError` on an illegal move). Both read the same table, so legality and result cannot drift apart.
- Terminal states (`done`, `cancelled`) appear in no action's from-set, so they reject every action. Re-plan edges (`in-progress`/`propagating-context` → `planning`) and the resume edge (`propagating-context` → `in-progress`) are explicit table entries.

Dependency graph (`domain/deps.py`, pure):

- `scope_of(state, id)` → `(kind, parent_id)`: kind `'top'` or `'sub'`; basis for all sibling checks.
- `deps_of(state, id)`, `status_of(state, id)` — resolve a task-or-subtask's deps/status by id.
- `register_subtask(state, parent_id, name, desc, deps)` → `Subtask` (not-planned): validates the parent is an existing supertask and dep scope; the caller appends it to `parent.subtasks`.
- `can_depend(state, task_id, dep_id)` — true only if same scope (same parent for subtasks), not the same id, and both exist.
- `would_create_cycle(state, task_id, dep_id)` — DFS from `dep_id` following deps; true if it reaches `task_id`. Short-circuits when `can_depend` is false.
- `unsatisfied_deps(state, id)`, `is_implementable(state, id)` — a dep is satisfied only when its status is `done`.
- `dependents(state, id)` — sorted ids of all tasks/subtasks that list `id` as a dep (what would be blocked if it were cancelled).

## Subtask handling

- Subtasks live in state under their parent's `subtasks` list; the only CLI path into state is `register --subtask-of`. A subtask row must exist before it can be planned (planning a supertask does not auto-register its listed subtasks).
- Folders are created only by `plan`, for both kinds: top-level `<id>_<slug>/` and nested subtask `<parent_folder>/<tNN.n>_<slug>/`. `register` never creates folders or files.
- Notes files appear only once notes exist: `save_and_render` renders a task's or subtask's notes files only when its note list is non-empty; `plan`'s scaffold writes the initial empty `notes.md`. The parent's `subtasks.md` is rendered on every save.
- Planning a subtask sets the owning supertask to `in-progress` (refused if that transition is illegal for the supertask).
- Deps stay sibling-scoped: a subtask may only depend on siblings in the same supertask; `can_depend` enforces it and `check` flags violations.

## Conventions and gotchas

- Layering agreed with user: CLI = presentation, core = orchestrators (the "service" role, named `core` for CLI semantics), persistence = repository, domain+model = pure data/logic. All commands share this shape; no controller touches persistence or domain directly.
- Wrappers require Python 3 on PATH; they are the only non-Python entry points. The CLI is importable/runnable as `python -m laaw` when cwd or PYTHONPATH contains the repo root. A bare `exec python -m laaw "$@"` wrapper fails outside the repo root (`No module named laaw`) — wrappers must set `PYTHONPATH` to the repo root resolved from their own location.
- Sync behavior: copy, keep existing indexes (never overwrite), gitignore entries added exactly once. Path resolution lives in core (`expanduser().resolve()`), so CLI and direct calls behave identically.
- Persistence is function-level (no class): `save_text`, `load_text` (raises `FileNotFoundError` if missing), `ensure_dir` (idempotent, takes `str`), `list_files` (sorted names; empty list if dir absent), `save_state` (pretty-printed JSON `indent=2` + trailing newline), `load_state`. `load_state` imports `ProjectState` lazily to avoid a circular import.
- Imports that risk cycles (`persistence.load_state`, `deps.py` importing `Status`) are done lazily inside the function.

## Testing

- Tests mirror the code layout: `tests/model/`, `tests/domain/`, `tests/core/`, `tests/cli/`, one test file per code file; stdlib `unittest`, zero deps.
- Given-when-then method names, arrange-act-assert bodies.
- Core tests monkeypatch `core.base.tasks_dir` to a temp dir (`tests/core/helpers.run_in_dir`); persistence and model tests use `tempfile.TemporaryDirectory`; no files are written outside the temp dir.
- Code must pass `basedpyright` with 0 errors; `pyrightconfig.json` in the project root (this version does NOT auto-discover `basedpyright.config.json`). Modern type syntax everywhere: built-in generics (`list[...]`, `dict[...]`) and `| None`; JSON-shaped dicts typed `dict[str, Any]`; `reportUnusedCallResult: none`.
