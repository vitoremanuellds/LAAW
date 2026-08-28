## Agent Workflow
This project uses a structured agent workflow — one process, no
profile choice:
- `.ai/info.md` exists → open and read in full — not "recall it
  exists," actually read it —
  [.ai/workflow/workflow.md](.ai/workflow/workflow.md).
- `.ai/info.md` doesn't exist → unbootstrapped. Run
  `.ai/workflow/skills/create-constitution-full/SKILL.md` to bootstrap
  it before doing anything else.

Do this before acting, every session — not just once, and not from
memory of a previous read. Gate-skip and scope-overstep bugs have
consistently traced back to this step being skipped.

Note: `.ai/workflow/` is a self-referential **plain copy**, not a git
submodule — this repo mounts itself, since this is the workflow's own
source repo, and a submodule doesn't work here: any commit after this
project's own `.ai/` was bootstrapped contains `.ai/` itself, so
pinning the submodule to a recent commit would nest a stale copy of
`.ai/` inside `.ai/workflow/`, breaking the "never written to"
boundary. Instead, `.ai/workflow/` is refreshed by directly copying
the current root `workflow.md`, `README.md`, `sync-skills.sh`,
`templates/`, `skills/`, and `reference/` over it whenever they change
meaningfully — a manual sync, not a version pin. Never edit anything
under `.ai/workflow/` directly; edit the real files at the repo root
instead, same as any other change to this project's own source, then
re-copy.
