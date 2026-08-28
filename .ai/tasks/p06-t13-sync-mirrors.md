# P06-T13: Sync mirrors: run sync-skills.sh and refresh .ai/workflow/'s copy

## Context

See [../phases/p06-workflow-doc-pruning.md](../phases/p06-workflow-doc-pruning.md).
`.ai/workflow/` (this repo's self-mounted copy of its own canonical root content) and
`.agents/skills/` haven't been refreshed since 2026-08-25 — every edit from
`P06-T01` through `P06-T12` (all now complete) landed only at the root. Confirmed
during planning:

- `workflow.md`, `workflow-medium.md`, every file under `skills/`, and
  `templates/decisions-template.md` all differ from their `.ai/workflow/`
  counterparts.
- `reference/reread-skill-discipline.md` (added by `P06-T04`) doesn't exist in the
  mirror at all yet.
- `sync-skills.sh` itself is already byte-identical at root and mirror — no action
  needed there.
- `README.md` also differs from its mirror copy, but that diff is a pre-existing,
  uncommitted local edit unrelated to P06 (present in `git status` before this phase
  started) — **not** touched by this task; see Out of scope.

**Two design calls made while planning, since the Plan item's shorthand list
("`workflow.md`, `skills/`, `templates/`, `reference/`") doesn't literally name
every affected file:**

1. `workflow-medium.md` is included in the refresh even though it isn't named in
   the Plan item's list — `P06-T01` genuinely edited it (the role-agnostic §10
   rewrite applies to the medium profile too, per that task's own scope), so its
   mirror copy is just as stale as `workflow.md`'s. Leaving it out would violate the
   phase's own Requirement that `.ai/workflow/` be byte-identical to root.
2. `sync-skills.sh` needs to run in a specific order relative to the `.ai/workflow/`
   refresh, not before it: the script copies *from* its own sibling `skills/`
   directory, so running `.ai/workflow/sync-skills.sh` before `.ai/workflow/skills/`
   itself is refreshed would copy stale content into `.agents/skills/`. Steps below
   refresh `.ai/workflow/` first, then run the mirror's own `sync-skills.sh` — the
   same order an actual downstream project would follow after a
   `git submodule update`.

## Implementation

### Objective

Bring `.ai/workflow/`'s copy of `workflow.md`, `workflow-medium.md`, `skills/`,
`templates/`, and `reference/` back to byte-identical with the canonical root
copies, then run `sync-skills.sh` so `.agents/skills/` matches too — closing out
every P06 edit made since the mirror was last refreshed.

### In scope

- `.ai/workflow/workflow.md`, `.ai/workflow/workflow-medium.md` — overwritten from
  root.
- `.ai/workflow/skills/` — overwritten from root `skills/` (all 15 directories).
- `.ai/workflow/templates/` — overwritten from root `templates/`.
- `.ai/workflow/reference/` — overwritten from root `reference/` (adds the missing
  `reread-skill-discipline.md`).
- `.agents/skills/` — synced from the (now-fresh) `.ai/workflow/skills/` via
  `.ai/workflow/sync-skills.sh`.

### Out of scope

- `README.md` / `.ai/workflow/README.md` — the root copy has its own pre-existing,
  uncommitted local edit unrelated to P06; do not overwrite, commit, or otherwise
  touch either copy.
- `sync-skills.sh` / `.ai/workflow/sync-skills.sh` — already byte-identical;
  no action needed.
- Any further content change to `workflow.md`/`workflow-medium.md`/skills — this
  task only copies already-approved, already-committed content; it does not author
  anything new.

### Files to modify

- `.ai/workflow/workflow.md`
- `.ai/workflow/workflow-medium.md`
- `.ai/workflow/skills/**` (all 15 skill directories)
- `.ai/workflow/templates/**`
- `.ai/workflow/reference/**`
- `.agents/skills/**` (all 15 skill directories)

### Steps

1. From the repo root, overwrite the mirror's copies with the canonical root
   content:
   - `workflow.md` → `.ai/workflow/workflow.md`
   - `workflow-medium.md` → `.ai/workflow/workflow-medium.md`
   - `skills/` → `.ai/workflow/skills/` (recursive replace)
   - `templates/` → `.ai/workflow/templates/` (recursive replace)
   - `reference/` → `.ai/workflow/reference/` (recursive replace)

   (flexible: exact shell commands — binding: the result must be byte-identical,
   confirmed by the Automatic validations below; do not touch `README.md` or
   `sync-skills.sh` while doing this.)
2. From the repo root, run `.ai/workflow/sync-skills.sh` with no arguments. It
   resolves the standard mount point (`.ai/workflow/` → project root two levels up)
   and copies `.ai/workflow/skills/` — now fresh from step 1 — into
   `.agents/skills/`, adding or overwriting each of the 15 skill directories.
3. Run every Automatic validation below before committing; if any shows a
   difference, re-check step 1 rather than hand-patching individual files.

### Dependencies

`P06-T01`…`P06-T12` (all complete — this task only mirrors their already-approved
content; it doesn't wait on anything still in review).

### Expected result

`skills/`, `.ai/workflow/skills/`, and `.agents/skills/` are byte-identical.
`.ai/workflow/workflow.md`, `.ai/workflow/workflow-medium.md`,
`.ai/workflow/templates/`, and `.ai/workflow/reference/` match their root
counterparts exactly. `README.md`'s pre-existing unrelated local edit is untouched.

### Automatic validations

- `diff -rq skills/ .agents/skills/` — no output.
- `diff -rq skills/ .ai/workflow/skills/` — no output.
- `diff workflow.md .ai/workflow/workflow.md` — no output.
- `diff workflow-medium.md .ai/workflow/workflow-medium.md` — no output.
- `diff -rq templates/ .ai/workflow/templates/` — no output.
- `diff -rq reference/ .ai/workflow/reference/` — no output.

### Manual validations

- Confirm `README.md`'s pre-existing uncommitted diff (present before this phase
  started) is unchanged — `git diff -- README.md` should show the same diff as
  before this task ran, and it must not appear in this task's own commit.
- Spot-check that `.ai/workflow/reference/reread-skill-discipline.md` now exists.
- Confirm `git status` after this task shows only the expected sync changes (plus
  the pre-existing, untouched `README.md`/`.gitignore` items) — nothing else swept
  in.
