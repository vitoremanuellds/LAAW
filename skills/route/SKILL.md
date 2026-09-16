---
name: route
description: Routes plain-language requests to the correct operation skill. The router does no operation work itself; it only reads the user's request, decides which skill to delegate to, and points the agent at that skill's file.
---

# Skill: route

This skill performs **routing** — mapping a plain-language request to the
correct operation skill. It does no operation work itself; it only reads
the user's request, decides which skill to delegate to, and points the
agent at that skill's file.

- **Can:** read the user's request; read `../info.md` for gate authority;
  read `workflow.md` for the operation table; point the agent at the
  correct skill file.
- **Must:** read `info.md` fresh, every time; read the matched skill file
  in full before delegating; never do operation work itself.
- **Cannot:** implement, validate, review, plan, build context, or
  propagate — the router only routes.

Always use `tools/generate-id.py --prefix t` to generate IDs for any
project file that requires an ID. Never hardcode, guess, or manually
construct IDs — the script is the single source of truth for ID
generation across the entire project.

Always use `tools/generate-id.py --prefix c` to generate IDs for
context files.

Read [.ai/workflow/workflow.md](.ai/workflow/workflow.md) in full, same
as every other skill — do not skip it for routing.

## Operation table

Maps user intents to the correct skill. Same entries and order as
`workflow.md §2`:

| User intent | Skill |
|---|---|
| "bootstrap" | `bootstrap/SKILL.md` |
| "constitution", "mission", "techstack", "context setup" | `create-constitution/SKILL.md` |
| "plan", "task", "break down" | `define-task/SKILL.md` |
| "implement", "write", "code" | `implement-task/SKILL.md` |
| "validate", "check", "test" | `validate-work/SKILL.md` |
| "review", "check quality", "judgment" | `review-work/SKILL.md` |
| "build context", "survey", "fill context" | `build-context/SKILL.md` |
| "propagate", "finalize", "mark done" | `propagate-context/SKILL.md` |

## Procedure

1. Read `../info.md` fresh — policy = gate authority.
2. Parse the user's request to determine intent.
3. Match the intent against the operation table above.
4. Read the matched skill file in full.
5. Delegate to that skill's procedure.

## Output

The matched skill file is now loaded; the agent proceeds with that
skill's procedure.
