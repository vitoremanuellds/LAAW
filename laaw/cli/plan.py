"""`laaw task plan <id>` — set status to planning, scaffold task.md + notes.md."""

import argparse
from pathlib import Path

from .. import persistence
from ..constants import GENERATED_HEADER, TASK_MD_SECTIONS
from ..model.state import ProjectState
from ..status import Action, can_transition, resulting_status
from .base import Refuse, run_command, task_folder


def run(args: argparse.Namespace) -> int:
    from .base import _tasks_dir

    return run_command(_tasks_dir(), lambda state: _plan(state, args.id))


def _plan(state: ProjectState, task_id: str) -> str:
    try:
        task = state.find_task(task_id)
    except KeyError:
        raise Refuse(f"no task with id {task_id}")

    if not can_transition(task.status, Action.PLAN):
        raise Refuse(f"cannot plan from status {task.status.value}")

    task.status = resulting_status(task.status, Action.PLAN)

    from .base import _tasks_dir

    folder = Path(_tasks_dir()) / task_folder(task.id, task.name)
    persistence.ensure_dir(str(folder))

    task_md = folder / "task.md"
    if not task_md.is_file():
        lines = [f"# {task.name}", ""]
        for section in TASK_MD_SECTIONS:
            lines.append(f"## {section}")
            lines.append("")
        persistence.save_text(str(task_md), "\n".join(lines))

    notes_md = folder / "notes.md"
    if not notes_md.is_file():
        persistence.save_text(str(notes_md), GENERATED_HEADER + "\n")

    return f"{task.id} → planning"
