# Template bootstrap conventions

Established during P01. Applies to any future template this repo adds
or changes, not just the ones P01 touched.

## Template → destination → copying skill

| Template | Copied to | Copying skill(s) |
|---|---|---|
| `info-template.md` | `.ai/info.md` | `create-constitution-full` |
| `medium-info-template.md` | `.ai/info.md` | `create-constitution-medium` |
| `lite-project-template.md` | `.ai/project.md` | `workflow-lite` |
| `minimal-tasks-template.md` | `.ai/tasks.md` | `workflow-minimal` |
| `decisions-template.md` | `.ai/decisions/decisions.md` | `create-constitution-full`, `create-constitution-medium` |
| `context-template.md` | `.ai/context/context.md` | `create-constitution-full`, `create-constitution-medium` |
| `adr-template.md` | `.ai/decisions/adr{NN}-{name}.md` | referenced from `workflow.md §7` / `workflow-medium.md §7`, and from `implement-task-full` / `implement-task-medium` when an implementation-time ADR is written |

## Convention: templates hold only artifact content

A template file must never contain agent-facing bootstrap instructions
("copy this to `.ai/X`", "edit this after copying," which skill's
rules apply). The skill that performs the copy is solely responsible
for stating the destination path and the "copy unedited" instruction —
it must never depend on the template's own text for that. This matters
because copies are unedited: any bootstrap prose in a template gets
carried verbatim into the live per-project artifact, where it's
immediately false ("copy this to `.ai/info.md`" inside a file that
already *is* `.ai/info.md`) and gets re-read on every gate check for
the life of the project.

Genuine usage guidance that belongs in the live artifact (e.g.
`decisions-template.md`'s "one row per ADR, check before adding a new
one") is not bootstrap prose and stays.

**When adding a new template:** write it as pure artifact content from
line 1, and put the copy instruction (destination + "unedited") in
whichever skill performs the copy, not in the template itself.
