"""Dependency logic for the LAAW CLI. Pure — operates on a ProjectState, no IO."""

from ..model.state import ProjectState
from ..model.subtask import Subtask


def scope_of(state: ProjectState, task_id: str) -> tuple[str, str | None]:
    """Return (kind, parent_id). kind is 'top' or 'sub'; parent_id is None for top."""
    if state.find_task_or_none(task_id) is not None:
        return "top", None
    for task in state.tasks:
        for sub in task.subtasks:
            if sub.id == task_id:
                return "sub", task.id
    raise KeyError(f"no task or subtask with id {task_id}")


def deps_of(state: ProjectState, task_id: str) -> list[str]:
    kind, parent_id = scope_of(state, task_id)
    if kind == "top":
        return state.find_task(task_id).deps
    assert parent_id is not None
    return state.find_subtask(parent_id, task_id).deps


def status_of(state: ProjectState, task_id: str):
    kind, parent_id = scope_of(state, task_id)
    if kind == "top":
        return state.find_task(task_id).status
    assert parent_id is not None
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
    seen: set[str] = set()
    frontier: list[str] = [dep_id]
    while frontier:
        current = frontier.pop()
        if current == task_id:
            return True
        if current in seen:
            continue
        seen.add(current)
        frontier.extend(deps_of(state, current))
    return False


def unsatisfied_deps(state: ProjectState, task_id: str) -> list[str]:
    from .status import Status

    return [dep for dep in deps_of(state, task_id) if status_of(state, dep) is not Status.DONE]


def is_implementable(state: ProjectState, task_id: str) -> bool:
    return not unsatisfied_deps(state, task_id)


def dependents(state: ProjectState, task_id: str) -> list[str]:
    result = []
    for task in state.tasks:
        if task_id in task.deps:
            result.append(task.id)
        for sub in task.subtasks:
            if task_id in sub.deps:
                result.append(sub.id)
    return sorted(result)


def register_subtask(
    state: ProjectState,
    parent_id: str,
    name: str,
    desc: str,
    deps: list[str],
) -> Subtask:
    """Build a subtask row for `parent_id` without mutating state.

    Raises ValueError when the parent is unknown, not a supertask, or a dep
    is out of sibling scope. The caller appends the result to
    `parent.subtasks`.
    """
    from .status import Status

    parent = state.find_task_or_none(parent_id)
    if parent is None:
        raise ValueError(f"unknown parent {parent_id}")
    if parent.type != "supertask":
        raise ValueError(f"{parent_id} is not a supertask")
    for dep in deps:
        if not can_depend(state, state.next_subtask_id(parent_id), dep):
            raise ValueError(f"{dep} is not a valid dep of a subtask of {parent_id}")
    return Subtask(
        id=state.next_subtask_id(parent_id),
        name=name,
        desc=desc,
        status=Status.NOT_PLANNED,
        deps=list(deps),
    )
