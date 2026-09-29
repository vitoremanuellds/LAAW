---
name: gather-context
description: Use to build or refresh the .ai/context/ wiki of an existing project. Analyzes only the file tree, asks the user questions, then reads files in dependency order and writes the context files.
---

# Gather Context

Read `.ai/workflow/workflow.md` first if you have not read it this session.

## Steps

1. Verify the `.ai/` skeleton exists. If not, stop and tell the user to run `laaw.py sync workflow <project>`.
2. Read **only the file tree** of the project (e.g. `rg --files`, `find . -type f`). Do not read file contents.
3. From the tree alone, list your assumptions about the project (structure, stack, entry points, module boundaries) and your questions. Present them to the user. **Do not proceed until the user has answered.**
4. Create the queue file `.ai/.queue.md`: one path per line, ordered the way a person would read the project, top-down along the dependency tree:
   1. Entry point (main/CLI/server startup).
   2. Configuration (manifests, settings, build files).
   3. Core modules, dependency order.
   4. Utility files last.
   Skip files the existing `.ai/context/` already covers well.
5. Read the files in queue order. For each, decide which context file it belongs to (existing or new) and update `.ai/context/index.md`. Follow the context rules: descriptive names, no IDs, task-agnostic, current state only; split any context file that would pass 100 lines.
6. When the queue is exhausted, delete `.ai/.queue.md` and present the resulting context to the user for approval.

## Rules

- Step 3 is tree-only: no file contents before the user answers the questions.
- Never write task references (IDs, names, task files) into `.ai/context/`.
- Do not edit project code: this skill reads code and writes only `.ai/context/` and `.ai/.queue.md`.
- Context approval is a human gate: the context is complete only once the user approves it.
