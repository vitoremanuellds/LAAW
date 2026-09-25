# route

Determine which skill should handle the next action, based on the current task status and
the human's message.

## When to use

Use **every turn** as the first step. The human's message may contain:
- An approval answer ("yes", "approved", "looks good")
- A question or request
- A re-ask or revision

## Steps

1. Run `python3 .ai/workflow/tools/laaw.py next` to get the current active task and its status.
2. Read `workflow.md` (§2, §7) to understand the status and expected gate.
3. Match the human's message to the expected gate:

| Current status | Expected gate | If human answers YES → | Skill to route to |
|---|---|---|---|
| `planning` | Plan approval | `set-status planning → in-progress` | implement-task |
| `in-progress` | Implementation approval | (fix work if no) | implement-task |
| `contextualizing` | Context approval | `set-status contextualizing → done` | propagate-context |

4. If the human's message does **not** answer an approval question, or if it's a new request,
   route to plan-task or another appropriate skill.
5. If the status is `created`, the next action is `laaw.py draft` to write the task file template.
6. Output the routing decision and the exact next action.

## Notes

- Never guess the skill. Always read `next` output first.
- The status in `state.json` is the source of truth; never infer status from file contents.
- If `next` reports multiple active roots, let the human choose which to work on.
