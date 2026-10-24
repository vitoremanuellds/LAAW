"""Dependency logic for the LAAW CLI. Pure — operates on a ProjectState, no IO."""

from typing import List, Optional, Tuple

from .model.state import ProjectState


def scope_of(state: ProjectState, task_id: str) -> Tuple[str, Optional[str]]:
    """Return (kind, parent_id). kind is 'top' or 'sub'; parent_id is None for top."""
    if state.find_task_or_none(task_id) is not None:
        return "top", None
    for task in state.tasks:
        for sub in task.subtasks:
            if sub.id == task_id:
                return "sub", task.id
    raise KeyError(f"no task or subtask with id {task_id}")


def deps_of(state: ProjectState, task_id: str) -> List[str]:
    kind, _ = scope_of(state, task_id)
    if kind == "top":
        return state.find_task(task_id).deps
    parent_id = scope_of(state, task_id)[1]
    return state.find_subtask(parent_id, task_id).deps


def status_of(state: ProjectState, task_id: str):
    from .status import Status

    kind, _ = scope_of(state, task_id)
    if kind == "top":
        return state.find_task(task_id).status
    parent_id = scope_of(state, task_id)[1]
    return state.find_subtask(parent_id, task_id).status


def can_depend(state: ProjectState, task_id: str, dep_id: str) -> bool:
    if task_id == dep_id:
        return False
    try:
        task_kind, task_parent = scope_of(state, task_id)
        dep_kind, dep_parent = scope_of(state, dep_id)
    except KeyError:
        return False
    return task_kind == dep_kind and task_parent == dep_parent


def would_create_cycle(state: ProjectState, task_id: str, dep_id: str) -> bool:
    if not can_depend(state, task_id, dep_id):
        return False
    seen = set()
    frontier = [dep_id]
    while frontier:
        current = frontier.pop()
        if current == task_id:
            return True
        if current in seen:
            continue
        seen.add(current)
        frontier.extend(deps_of(state, current))
    return False


def unsatisfied_deps(state: ProjectState, task_id: str) -> List[str]:
    from .status import Status

    return [dep for dep in deps_of(state, task_id) if status_of(state, dep) is not Status.DONE]


def is_implementable(state: ProjectState, task_id: str) -> bool:
    return not unsatisfied_deps(state, task_id)


def dependents(state: ProjectState, task_id: str) -> List[str]:
    result = []
    for task in state.tasks:
        if task_id in task.deps:
            result.append(task.id)
        for sub in task.subtasks:
            if task_id in sub.deps:
                result.append(sub.id)
    return sorted(result)
