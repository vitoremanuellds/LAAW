"""Core metadata orchestrators: rename, desc, dep-add, dep-remove, promote."""

from pathlib import Path

from .. import persistence
from ..constants import DESC_MAX_CHARS
from ..domain.deps import can_depend, deps_of, status_of, would_create_cycle
from ..domain.status import Status
from ..model.state import Resolved
from .base import Refuse, load_or_empty, save_and_render, task_folder


def rename(task_id: str, name: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)

    if resolved.status not in (Status.NOT_PLANNED, Status.PLANNING):
        raise Refuse(f"cannot rename from status {resolved.status.value} (re-plan to rename)")

    target = _target(state, resolved)
    old_folder = _folder_for(state, tasks_dir, resolved)
    new_folder = Path(tasks_dir) / task_folder(resolved.id, name)
    if resolved.kind == "sub":
        assert resolved.parent_id is not None
        parent = state.find_task(resolved.parent_id)
        new_folder = Path(tasks_dir) / task_folder(parent.id, parent.name) / new_folder.name
    if old_folder.is_dir():
        old_folder.rename(new_folder)
    persistence.ensure_dir(str(new_folder))

    target.name = name
    save_and_render(state, tasks_dir)
    return f"{task_id} renamed to {name}", 0


def desc(task_id: str, text: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)

    if resolved.status.terminal:
        raise Refuse(f"cannot edit desc from terminal status {resolved.status.value}")

    _target(state, resolved).desc = text[:DESC_MAX_CHARS]
    save_and_render(state, tasks_dir)
    return f"{task_id} desc updated", 0


def dep_add(task_id: str, dep_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)

    if resolved.status.terminal:
        raise Refuse(f"cannot add dep from terminal status {resolved.status.value}")
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
    resolved = _find_any(state, task_id)

    if resolved.status.terminal:
        raise Refuse(f"cannot remove dep from terminal status {resolved.status.value}")

    deps = deps_of(state, task_id)
    if dep_id not in deps:
        raise Refuse(f"{dep_id} is not a dep of {task_id}")
    deps.remove(dep_id)
    save_and_render(state, tasks_dir)
    return f"{task_id} no longer depends on {dep_id}", 0


def promote(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)

    if resolved.kind != "top":
        raise Refuse(f"{task_id} is a subtask; promote applies to top-level tasks")
    task = state.find_task(task_id)
    if task.status not in (Status.NOT_PLANNED, Status.PLANNING):
        raise Refuse(f"cannot promote from status {task.status.value} (pre-implementation only)")
    if task.type == "supertask":
        raise Refuse(f"{task_id} is already a supertask")

    task.type = "supertask"
    save_and_render(state, tasks_dir)
    return f"{task_id} promoted to supertask", 0


def _find_any(state, task_id: str) -> Resolved:
    try:
        return state.find_any(task_id)
    except KeyError:
        raise Refuse(f"no task or subtask with id {task_id}")


def _target(state, resolved: Resolved):
    if resolved.kind == "top":
        return state.find_task(resolved.id)
    assert resolved.parent_id is not None
    return state.find_subtask(resolved.parent_id, resolved.id)


def _folder_for(state, tasks_dir: str, resolved: Resolved) -> Path:
    if resolved.kind == "top":
        task = state.find_task(resolved.id)
        return Path(tasks_dir) / task_folder(task.id, task.name)
    assert resolved.parent_id is not None
    parent = state.find_task(resolved.parent_id)
    sub = state.find_subtask(resolved.parent_id, resolved.id)
    return Path(tasks_dir) / task_folder(parent.id, parent.name) / task_folder(sub.id, sub.name)


def _dir() -> str:
    from .base import tasks_dir

    return tasks_dir()
