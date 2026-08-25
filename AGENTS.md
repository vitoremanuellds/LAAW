## Agent Workflow
This project uses a structured agent workflow, one of four
independent profiles depending on what's already bootstrapped:
- `.ai/info.md` exists → read its `profile:` field, then open and
  read in full — not "recall it exists," actually read it —
  [.ai/workflow/workflow.md](.ai/workflow/workflow.md) (full) or
  [.ai/workflow/workflow-medium.md](.ai/workflow/workflow-medium.md) (medium).
- `.ai/project.md` exists (no `info.md`) → open and read in full
  [.ai/workflow/skills/workflow-lite/SKILL.md](.ai/workflow/skills/workflow-lite/SKILL.md) (lite).
- `.ai/tasks.md` exists (no `info.md`, no `project.md`) → open and
  read in full
  [.ai/workflow/skills/workflow-minimal/SKILL.md](.ai/workflow/skills/workflow-minimal/SKILL.md) (minimal).
- None of the three exist → unbootstrapped. Ask which profile
  before doing anything else, then bootstrap accordingly (see this
  repo's README, "Choosing a profile").

Do this before acting, every session — not just once, and not from
memory of a previous read. Gate-skip and scope-overstep bugs have
consistently traced back to this step being skipped.

This project uses the **full** profile — `.ai/info.md` exists.

Note: `.ai/workflow/` is a self-referential **plain copy**, not a git
submodule — this repo mounts itself, since this is the workflow's own
source repo, and a submodule doesn't work here: any commit after this
project's own `.ai/` was bootstrapped contains `.ai/` itself, so
pinning the submodule to a recent commit would nest a stale copy of
`.ai/` inside `.ai/workflow/`, breaking the "never written to"
boundary. Instead, `.ai/workflow/` is refreshed by directly copying
the current root `workflow.md`, `workflow-medium.md`, `README.md`,
`sync-skills.sh`, `templates/`, `skills/`, and `reference/` over it
whenever they change meaningfully — a manual sync, not a version pin.
Never edit anything under `.ai/workflow/` directly; edit the real
files at the repo root instead, same as any other change to this
project's own source, then re-copy.
