"""Core metadata orchestrators: rename, desc, dep-add, dep-remove."""

from pathlib import Path

from .. import persistence
from ..constants import DESC_MAX_CHARS
from ..domain.deps import can_depend, deps_of, status_of, would_create_cycle
from ..domain.status import Status
from .base import Refuse, load_or_empty, save_and_render, task_folder


def rename(task_id: str, name: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)

    if task.status not in (Status.NOT_PLANNED, Status.PLANNING):
        raise Refuse(f"cannot rename from status {task.status.value} (re-plan to rename)")

    old_folder = Path(tasks_dir) / task_folder(task.id, task.name)
    new_folder = Path(tasks_dir) / task_folder(task.id, name)
    if old_folder.is_dir():
        old_folder.rename(new_folder)
    persistence.ensure_dir(str(new_folder))

    task.name = name
    save_and_render(state, tasks_dir)
    return f"{task.id} renamed to {name}", 0


def desc(task_id: str, text: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)

    if task.status.terminal:
        raise Refuse(f"cannot edit desc from terminal status {task.status.value}")

    task.desc = text[:DESC_MAX_CHARS]
    save_and_render(state, tasks_dir)
    return f"{task.id} desc updated", 0


def dep_add(task_id: str, dep_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)

    if task.status.terminal:
        raise Refuse(f"cannot add dep from terminal status {task.status.value}")
    if not can_depend(state, task_id, dep_id):
        raise Refuse(f"{dep_id} is not a valid dep of {task_id} (unknown or out of scope)")
    if would_create_cycle(state, task_id, dep_id):
        raise Refuse(f"adding {dep_id} to {task_id} would create a cycle")

    deps_of(state, task_id).append(dep_id)
    warning = ""
    if status_of(state, dep_id) is not Status.DONE:
        warning = f" (warning: {dep_id} is not done)"
    save_and_render(state, tasks_dir)
    return f"{task_id} now depends on {dep_id}{warning}", 0


def dep_remove(task_id: str, dep_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)

    if task.status.terminal:
        raise Refuse(f"cannot remove dep from terminal status {task.status.value}")

    deps = deps_of(state, task_id)
    if dep_id not in deps:
        raise Refuse(f"{dep_id} is not a dep of {task_id}")
    deps.remove(dep_id)
    save_and_render(state, tasks_dir)
    return f"{task_id} no longer depends on {dep_id}", 0


def _find(state, task_id: str):
    try:
        return state.find_task(task_id)
    except KeyError:
        raise Refuse(f"no task with id {task_id}")


def _dir() -> str:
    from .base import tasks_dir

    return tasks_dir()
