"""`laaw task register --name ... [--desc ...] [--deps ...]`"""

import argparse
from pathlib import Path

from .. import persistence
from ..model.state import ProjectState, kebab
from ..model.task import Task
from ..status import Status
from .base import Refuse, run_command, task_folder


def run(args: argparse.Namespace) -> int:
    from .base import _tasks_dir

    return run_command(_tasks_dir(), lambda state: _register(state, args))


def _register(state: ProjectState, args: argparse.Namespace) -> str:
    for dep in args.deps:
        if state.find_task_or_none(dep) is None:
            raise Refuse(f"unknown dep {dep}")

    task_id = state.next_top_level_id()
    name = args.name
    folder = task_folder(task_id, name)

    task = Task(
        id=task_id,
        name=name,
        desc=args.desc[:180],
        type="simple",
        status=Status.NOT_PLANNED,
        deps=list(args.deps),
    )
    state.add_task(task)
    from .base import _tasks_dir

    persistence.ensure_dir(str(Path(_tasks_dir()) / folder))
    return f"registered {task_id} ({folder})"
