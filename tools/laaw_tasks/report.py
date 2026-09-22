"""Human-readable rendering of tasks: the board and the `next` output.

Pure over Task objects — no I/O here. (The consistency report is
State.check(), because it probes the files the state refers to.)

Renderers take the data they need directly: a list of root Task objects
(State.roots), not the whole State document.
"""

from .errors import TaskError
from .state import DONE, unmet_dependencies


def _blocked_note(task, statuses):
    """'blocked by t1 (in-progress), t2 (unknown)' suffix parts, or None."""
    blocked = unmet_dependencies(task, statuses)
    if not blocked:
        return None
    return ", ".join(f"{d} ({statuses.get(d) or 'unknown'})" for d, _ in blocked)


class BoardRenderer:
    """Render the task board as a markdown table."""

    def render(self, roots):
        """Render the board from a list of root Task objects."""

        def row(t):
            return f"| {t.id} | {t.name} | {t.status} | {', '.join(t.depends) or '—'} |"

        lines = ["| id | name | status | depends |", "|---|---|---|---|"]
        for root in roots:
            lines.append(row(root))
            for child in root.children:
                lines.append(row(child))
        return "\n".join(lines)


class NextGuidance:
    """Generate 'Next:' guidance for a task after a status flip.

    statuses (optional) maps every task id to its current status; when given,
    the guidance also reports blocked follow-up subtasks.
    """

    def get_guidance(self, task, parent=None, statuses=None):
        """Get the next guidance string for a Task (parent Task or None)."""
        tid, st = task.id, task.status
        if st == "draft":
            return f"{tid} is draft — ask plan approval (plan-task), or work it if the human already approved."
        if st == "in-progress":
            if parent is not None:
                return (
                    f"Work {tid}'s Steps like a leaf task (implement-task), then: tasks.py set-status {tid} impl-review. "
                    f"When you ask for approval, STOP — the next subtask starts only on the human's approval message."
                )
            if task.is_super:
                if not task.children:
                    return (
                        f"{tid} has no subtasks yet — plan-task must add them before work can start: "
                        f"tasks.py subtask {tid} <child name>."
                    )
                if all(c.status == DONE for c in task.children):
                    return (
                        f"All subtasks of {tid} are done. Run the parent's Validations, aggregate "
                        f"Context updates, then: tasks.py set-status {tid} ctx-review."
                    )
                return f"{tid} stays in-progress while its subtasks are worked — implement-task walks them in ID order."
            return (
                f"Work {tid}'s Steps (implement-task), then: tasks.py set-status {tid} impl-review. "
                "When you ask for approval, STOP — do not start any other work this turn."
            )
        if st == "impl-review":
            return (
                f'Now ask the human: "Approve implementation of {tid}?" — show the diff summary and '
                "validation results, then stop. Continue only on the human's answer."
            )
        if st == "ctx-review":
            return (
                f'Now ask the human: "Approve context changes for {tid}?" — show the exact context edits, '
                "then stop. Continue only on the human's answer."
            )
        if st == DONE:
            if parent is not None:
                live = [c for c in parent.children if c.status != DONE]
                if not live:
                    return (
                        f"{tid} is done and every subtask of {parent.id} is done — run the parent's "
                        "Validations, aggregate Context updates, then hand off to propagate-context (workflow.md §7)."
                    )
                nxt = live[0]
                note = _blocked_note(nxt, statuses) if statuses is not None else None
                if note:
                    return f"{tid} is done, but the next subtask {nxt.id} is blocked by {note} — do not start it; ask the human how to proceed."
                return f"{tid} is done. Continue to {nxt.id} (implement-task)."
            return f"{tid} is done."
        return ""


class NextOutput:
    """Generate the 'next' command output (workflow.md §7)."""

    def get_output(self, roots):
        """Generate next output from a list of root Task objects."""
        all_roots = list(roots)
        roots = [r for r in all_roots if r.status != DONE]
        statuses = {}
        for r in all_roots:
            statuses[r.id] = r.status
            for c in r.children:
                statuses[c.id] = c.status

        if not roots:
            return "No active tasks. Offer plan-task for new work (workflow.md §7)."

        if len(roots) > 1:
            lines = ["Multiple active roots — ask the human which one to work (workflow.md §7):"]
            for r in sorted(roots, key=self._sort_key):
                line = f"  {r.id} — {r.name} ({r.status})"
                note = _blocked_note(r, statuses)
                if note:
                    line += f" [BLOCKED by {note}]"
                lines.append(line)
            return "\n".join(lines)

        r = min(roots, key=self._sort_key)
        tid = r.id

        if r.status == "draft":
            note = _blocked_note(r, statuses)
            if note:
                return (
                    f"{tid} is BLOCKED by {note} — its plan is not ready to approve. Resume the blocking "
                    "task, or ask the human to revise the plan (plan-task/plan-project; workflow.md §7)."
                )
            return f'Ask the human: "Approve plan for {tid}?" — show {r.file} first. On approval, hand off to implement-task.'
        if r.status == "in-progress":
            if r.is_super:
                if not r.children:
                    return (
                        f"{tid} has no subtasks yet — plan-task must add them before work can start: "
                        f"tasks.py subtask {tid} <child name>."
                    )
                live = [c for c in r.children if c.status != DONE]
                if not live:
                    return (
                        f"All subtasks of {tid} are done. Run the parent's Validations, aggregate its "
                        "Context updates, then hand off to propagate-context (workflow.md §7)."
                    )
                first = live[0]
                out = f"Hand off to implement-task. Next subtask of {tid}: {first.id} — {first.name}."
                note = _blocked_note(first, statuses)
                if note:
                    out += f"\n  NOTE: {first.id} is BLOCKED by {note} — do not start it; ask the human (workflow.md §7)."
                return out
            return f"Hand off to implement-task for {tid} (file: {r.file})."
        if r.status == "impl-review":
            return (
                f'Ask the human: "Approve implementation of {tid}?" — show the diff summary and '
                "validation results. On approval, hand off to propagate-context."
            )
        if r.status == "ctx-review":
            return (
                f'Ask the human: "Approve context changes for {tid}?" — show the exact context edits. '
                "On approval, propagate-context records/commits done."
            )
        return ""

    @staticmethod
    def _sort_key(root):
        try:
            return int(root.id[1:])
        except ValueError:
            raise TaskError(
                f"root id '{root.id}' does not match t<N> — state.json looks corrupt; run tasks.py check."
            ) from None
