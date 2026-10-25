"""Core lifecycle orchestrators: register, plan, implement, propagate, done, cancel."""

from pathlib import Path

from .. import persistence
from ..constants import GENERATED_HEADER, TASK_MD_SECTIONS
from ..domain.deps import dependents, register_subtask, unsatisfied_deps
from ..domain.status import Action, Status, can_transition, resulting_status
from ..model.state import Resolved
from ..model.task import Task
from .base import Refuse, load_or_empty, save_and_render, task_folder


def register(
    name: str,
    desc: str,
    deps: list[str],
    subtask_of: str | None = None,
) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)

    if subtask_of is not None:
        try:
            subtask = register_subtask(state, subtask_of, name, desc[:180], deps)
        except ValueError as e:
            raise Refuse(str(e))
        parent = state.find_task(subtask_of)
        parent.subtasks.append(subtask)
        save_and_render(state, tasks_dir)
        return f"registered {subtask.id} under {subtask_of}", 0

    for dep in deps:
        if state.find_task_or_none(dep) is None:
            raise Refuse(f"unknown dep {dep}")

    task_id = state.next_top_level_id()
    folder = task_folder(task_id, name)
    task = Task(
        id=task_id,
        name=name,
        desc=desc[:180],
        type="simple",
        status=Status.NOT_PLANNED,
        deps=list(deps),
    )
    state.add_task(task)
    save_and_render(state, tasks_dir)
    return f"registered {task_id} ({folder})", 0


def plan(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)
    if not can_transition(resolved.status, Action.PLAN):
        raise Refuse(f"cannot plan from status {resolved.status.value}")

    target = _target(state, resolved)
    target.status = resulting_status(resolved.status, Action.PLAN)
    folder = _folder_for(state, tasks_dir, resolved)
    persistence.ensure_dir(str(folder))
    _scaffold(folder, resolved.name)
    if resolved.kind == "sub":
        supertask = state.find_task(resolved.parent_id or "")
        if supertask.status is not Status.IN_PROGRESS:
            if not can_transition(supertask.status, Action.IMPLEMENT):
                raise Refuse(f"cannot set supertask {supertask.id} to in-progress from status {supertask.status.value}")
            supertask.status = resulting_status(supertask.status, Action.IMPLEMENT)
    save_and_render(state, tasks_dir)
    return f"{task_id} → planning", 0


def implement(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)
    if not can_transition(resolved.status, Action.IMPLEMENT):
        raise Refuse(f"cannot implement from status {resolved.status.value}")

    blocked = unsatisfied_deps(state, task_id)
    if blocked:
        raise Refuse(f"unsatisfied deps: {', '.join(blocked)}")

    _target(state, resolved).status = resulting_status(resolved.status, Action.IMPLEMENT)
    save_and_render(state, tasks_dir)
    return f"{task_id} → in-progress", 0


def propagate(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)
    if not can_transition(resolved.status, Action.PROPAGATE):
        raise Refuse(f"cannot propagate from status {resolved.status.value}")

    _target(state, resolved).status = resulting_status(resolved.status, Action.PROPAGATE)
    save_and_render(state, tasks_dir)
    return f"{task_id} → propagating-context", 0


def done(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)
    if not can_transition(resolved.status, Action.DONE):
        raise Refuse(f"cannot mark done from status {resolved.status.value}")

    _target(state, resolved).status = resulting_status(resolved.status, Action.DONE)
    save_and_render(state, tasks_dir)
    return f"{task_id} → done", 0


def remove(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)
    if resolved.status is not Status.CANCELLED:
        raise Refuse(f"can only remove cancelled tasks ({task_id} is {resolved.status.value})")

    blocked = dependents(state, task_id)
    if blocked:
        raise Refuse(f"{task_id} has dependents: {', '.join(blocked)}")

    folder = _folder_for(state, tasks_dir, resolved)  # computed before mutation

    if resolved.kind == "top":
        parent = state.find_task(resolved.id)
        if parent.subtasks:
            raise Refuse(f"{task_id} still has subtasks: {', '.join(s.id for s in parent.subtasks)}")
        state.tasks.remove(parent)
    else:
        assert resolved.parent_id is not None
        parent = state.find_task(resolved.parent_id)
        sub = state.find_subtask(resolved.parent_id, resolved.id)
        parent.subtasks.remove(sub)

    _delete_tree(folder)
    save_and_render(state, tasks_dir)
    return f"{task_id} removed", 0


def cancel(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)
    if not can_transition(resolved.status, Action.CANCEL):
        raise Refuse(f"cannot cancel from status {resolved.status.value}")

    _target(state, resolved).status = resulting_status(resolved.status, Action.CANCEL)
    save_and_render(state, tasks_dir)
    blocked = dependents(state, task_id)
    if blocked:
        return f"{task_id} → cancelled; blocked dependents: {', '.join(blocked)}", 0
    return f"{task_id} → cancelled", 0


def _find_any(state, task_id: str) -> Resolved:
    try:
        return state.find_any(task_id)
    except KeyError:
        raise Refuse(f"no task or subtask with id {task_id}")


def _target(state, resolved: Resolved):
    """The mutable Task or Subtask behind a resolved id."""
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


def _scaffold(folder: Path, name: str) -> None:
    task_md = folder / "task.md"
    if not task_md.is_file():
        lines = [f"# {name}", ""]
        for section in TASK_MD_SECTIONS:
            lines.append(f"## {section}")
            lines.append("")
        persistence.save_text(str(task_md), "\n".join(lines))

    notes_md = folder / "notes.md"
    if not notes_md.is_file():
        persistence.save_text(str(notes_md), GENERATED_HEADER + "\n")


def _delete_tree(folder: Path) -> None:
    if not folder.is_dir():
        return
    paths = sorted((p for p in folder.rglob("*") if p != folder), key=lambda p: len(str(p)), reverse=True)
    for path in paths:
        if path.is_file() or path.is_symlink():
            path.unlink()
        elif path.is_dir():
            path.rmdir()
    folder.rmdir()


def _dir() -> str:
    from .base import tasks_dir

    return tasks_dir()
