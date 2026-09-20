---
name: setup-project
description: One-time interview that seeds .ai/context/ for a new project (mission, stack/constraints, standing agent rules) behind an approval. Use right after bootstrap when .ai/context/ has no topic files, or when the human asks to re-seed context.
---

# Skill: setup-project

Setup-project is the only other writer of `.ai/context/` besides propagate-context. It seeds the
initial project knowledge; everything after that flows through task Context updates.

## Steps

1. Precondition: bootstrap has run (`.ai/context/index.md` exists). If it has not, hand off to
   **bootstrap** and stop. If topic files already exist and the human did not ask to re-seed,
   report and stop.
2. Interview — three short questions, in one message:
   1. What is this project? (mission in one or two sentences)
   2. Stack and hard constraints? (language, runtime, packages, things that must stay true)
   3. Standing rules for agents working here? (conventions, style, things never to do)
3. Draft the context from the answers:
   - `.ai/context/project.md` — mission + stack/constraints.
   - A separate topic file (e.g. `conventions.md`) only if a cluster of answers is big enough to
     deserve its own name; otherwise keep it in `project.md`.
   - Matching rows for `.ai/context/index.md`.
4. Show the exact file contents and index rows, then ask: "Approve context seeding?" and stop.
5. On approval: write the files and index rows. On rejection: revise from the human's notes and
   re-ask (nothing is written until approved).
6. If the project is a git repo, commit: `git add .ai/context && git commit -m "context: seed"`.
   Report done.

## Rules

- Context style per workflow.md §6: small, factual, present tense; one file per topic; split past
  ~100 lines.
- This skill creates no tasks and touches no status — seeding has no task ID.
- Never overwrite existing topic files without the human explicitly asking to re-seed that topic.
