"""Human-readable rendering of tasks: the board and the `next` output.

Pure over Task objects — no I/O here. (The consistency report is
State.check(), because it probes the files the state refers to.)

Renderers take the data they need directly: a list of root Task objects
(State.roots), not the whole State document.
"""

from .errors import TaskError
from .state import DONE


class BoardRenderer:
    """Render the task board as a markdown table."""

    def render(self, roots):
        """Render the board from a list of root Task objects."""
        lines = ["| id | name | status |", "|---|---|---|"]
        for root in roots:
            lines.append(f"| {root.id} | {root.name} | {root.status} |")
            for child in root.children:
                lines.append(f"| {child.id} | {child.name} | {child.status} |")
        return "\n".join(lines)


class NextGuidance:
    """Generate 'Next:' guidance for a task after a status flip."""

    def get_guidance(self, task, parent=None):
        """Get the next guidance string for a Task (parent Task or None)."""
        tid, st = task.id, task.status
        if st == "draft":
            return f"{tid} is draft — ask plan approval (plan-task), or work it if the human already approved."
        if st == "in-progress":
            if parent is not None:
                return f"Work {tid}'s Steps like a leaf task (implement-task), then: tasks.py set-status {tid} impl-review."
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
            return f"Work {tid}'s Steps (implement-task), then: tasks.py set-status {tid} impl-review."
        if st == "impl-review":
            return f'Now ask the human: "Approve implementation of {tid}?" — show the diff summary and validation results, then stop.'
        if st == "ctx-review":
            return f'Now ask the human: "Approve context changes for {tid}?" — show the exact context edits, then stop.'
        if st == DONE:
            if parent is not None:
                live = [c for c in parent.children if c.status != DONE]
                if not live:
                    return (
                        f"{tid} is done and every subtask of {parent.id} is done — run the parent's "
                        "Validations, aggregate Context updates, then hand off to propagate-context (workflow.md §7)."
                    )
                return f"{tid} is done. Continue to {live[0].id} (implement-task)."
            return f"{tid} is done."
        return ""


class NextOutput:
    """Generate the 'next' command output (workflow.md §7)."""

    def get_output(self, roots):
        """Generate next output from a list of root Task objects."""
        roots = [r for r in roots if r.status != DONE]

        if not roots:
            return "No active tasks. Offer plan-task for new work (workflow.md §7)."

        if len(roots) > 1:
            lines = ["Multiple active roots — ask the human which one to work (workflow.md §7):"]
            for r in sorted(roots, key=self._sort_key):
                lines.append(f"  {r.id} — {r.name} ({r.status})")
            return "\n".join(lines)

        r = min(roots, key=self._sort_key)
        tid = r.id

        if r.status == "draft":
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
                return f"Hand off to implement-task. Next subtask of {tid}: {first.id} — {first.name}."
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
