"""`laaw task done <id>` — set status to done (terminal)."""

import argparse

from ..model.state import ProjectState
from ..status import Action, can_transition, resulting_status
from .base import Refuse, run_command


def run(args: argparse.Namespace) -> int:
    from .base import _tasks_dir

    return run_command(_tasks_dir(), lambda state: _done(state, args.id))


def _done(state: ProjectState, task_id: str) -> str:
    try:
        task = state.find_task(task_id)
    except KeyError:
        raise Refuse(f"no task with id {task_id}")

    if not can_transition(task.status, Action.DONE):
        raise Refuse(f"cannot mark done from status {task.status.value}")

    task.status = resulting_status(task.status, Action.DONE)
    return f"{task.id} → done"
