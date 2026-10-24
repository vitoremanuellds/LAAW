"""Core query orchestrators: deps, dependents, check. Read-only — no save."""

import json
from pathlib import Path

from ..domain.deps import (
    can_depend,
    is_implementable,
    unsatisfied_deps,
    would_create_cycle,
)
from .base import Refuse, load_or_empty, task_folder


def deps(task_id: str, as_json: bool = False) -> tuple[str, int]:
    state = load_or_empty(_dir())
    _find(state, task_id)
    unsatisfied = unsatisfied_deps(state, task_id)
    implementable = is_implementable(state, task_id)
    if as_json:
        payload = {"id": task_id, "unsatisfied": unsatisfied, "implementable": implementable}
        return json.dumps(payload), 0
    if unsatisfied:
        return f"{task_id}: blocked by {', '.join(unsatisfied)}", 1
    return f"{task_id}: implementable", 0


def dependents(task_id: str, as_json: bool = False) -> tuple[str, int]:
    state = load_or_empty(_dir())
    _find(state, task_id)
    blocked = _dependents(state, task_id)
    if as_json:
        return json.dumps({"id": task_id, "dependents": blocked}), 0
    if blocked:
        return f"{task_id}: dependents {', '.join(blocked)} (would be blocked)", 0
    return f"{task_id}: no dependents", 0


def check(as_json: bool = False) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    drift = _drift(state, tasks_dir)
    if as_json:
        return json.dumps({"drift": drift}), (1 if drift else 0)
    if drift:
        return "drift:\n" + "\n".join(f"- {d}" for d in drift), 1
    return "no drift", 0


def _drift(state, tasks_dir: str) -> list[str]:
    from ..domain.status import Status

    problems: list[str] = []
    folders_on_disk: set[str] = set()

    for task in state.tasks:
        folder = Path(tasks_dir) / task_folder(task.id, task.name)
        if not folder.is_dir():
            problems.append(f"{task.id}: missing folder {folder.name}")
            continue
        folders_on_disk.add(folder.name)
        if task.status is not Status.NOT_PLANNED and not (folder / "task.md").is_file():
            problems.append(f"{task.id}: status {task.status.value} but no task.md")
        for dep in task.deps:
            if state.find_task_or_none(dep) is None:
                problems.append(f"{task.id}: unknown dep {dep}")
        for sub in task.subtasks:
            for dep in sub.deps:
                if not can_depend(state, sub.id, dep):
                    problems.append(f"{sub.id}: invalid dep {dep} (scope)")
                elif would_create_cycle(state, sub.id, dep):
                    problems.append(f"{sub.id}: cycle via dep {dep}")

    for name in _disk_folders(tasks_dir):
        if name not in folders_on_disk:
            problems.append(f"folder {name} has no matching task in state")

    return problems


def _disk_folders(tasks_dir: str) -> list[str]:
    root = Path(tasks_dir)
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir())


def _dependents(state, task_id: str) -> list[str]:
    result = []
    for task in state.tasks:
        if task_id in task.deps:
            result.append(task.id)
        for sub in task.subtasks:
            if task_id in sub.deps:
                result.append(sub.id)
    return sorted(result)


def _find(state, task_id: str):
    try:
        state.find_task(task_id)
    except KeyError:
        raise Refuse(f"no task with id {task_id}")


def _dir() -> str:
    from .base import tasks_dir

    return tasks_dir()
