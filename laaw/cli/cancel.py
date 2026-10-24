"""`laaw task cancel <id>` — set status to cancelled (terminal), report dependents."""

import argparse

from ..deps import dependents
from ..model.state import ProjectState
from ..status import Action, can_transition, resulting_status
from .base import Refuse, run_command


def run(args: argparse.Namespace) -> int:
    from .base import _tasks_dir

    return run_command(_tasks_dir(), lambda state: _cancel(state, args.id))


def _cancel(state: ProjectState, task_id: str) -> str:
    try:
        task = state.find_task(task_id)
    except KeyError:
        raise Refuse(f"no task with id {task_id}")

    if not can_transition(task.status, Action.CANCEL):
        raise Refuse(f"cannot cancel from status {task.status.value}")

    task.status = resulting_status(task.status, Action.CANCEL)

    blocked = dependents(state, task_id)
    if blocked:
        return f"{task.id} → cancelled; blocked dependents: {', '.join(blocked)}"
    return f"{task.id} → cancelled"
