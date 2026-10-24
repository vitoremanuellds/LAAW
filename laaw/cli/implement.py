"""`laaw task implement <id>` — set status to in-progress (deps must be done)."""

import argparse

from ..deps import unsatisfied_deps
from ..model.state import ProjectState
from ..status import Action, can_transition, resulting_status
from .base import Refuse, run_command


def run(args: argparse.Namespace) -> int:
    from .base import _tasks_dir

    return run_command(_tasks_dir(), lambda state: _implement(state, args.id))


def _implement(state: ProjectState, task_id: str) -> str:
    try:
        task = state.find_task(task_id)
    except KeyError:
        raise Refuse(f"no task with id {task_id}")

    if not can_transition(task.status, Action.IMPLEMENT):
        raise Refuse(f"cannot implement from status {task.status.value}")

    blocked = unsatisfied_deps(state, task_id)
    if blocked:
        raise Refuse(f"unsatisfied deps: {', '.join(blocked)}")

    task.status = resulting_status(task.status, Action.IMPLEMENT)
    return f"{task.id} → in-progress"
