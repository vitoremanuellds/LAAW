"""Core lifecycle orchestrators: register, plan, implement, propagate, done, cancel."""

from pathlib import Path

from .. import persistence
from ..constants import GENERATED_HEADER, TASK_MD_SECTIONS
from ..domain.deps import dependents, unsatisfied_deps
from ..domain.status import Action, Status, can_transition, resulting_status
from ..model.task import Task
from .base import Refuse, load_or_empty, save_and_render, task_folder


def register(name: str, desc: str, deps: list[str]) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
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
    persistence.ensure_dir(str(Path(tasks_dir) / folder))
    save_and_render(state, tasks_dir)
    return f"registered {task_id} ({folder})", 0


def plan(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)
    if not can_transition(task.status, Action.PLAN):
        raise Refuse(f"cannot plan from status {task.status.value}")

    task.status = resulting_status(task.status, Action.PLAN)
    folder = Path(tasks_dir) / task_folder(task.id, task.name)
    persistence.ensure_dir(str(folder))
    _scaffold(folder, task.name)
    save_and_render(state, tasks_dir)
    return f"{task.id} → planning", 0


def implement(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)
    if not can_transition(task.status, Action.IMPLEMENT):
        raise Refuse(f"cannot implement from status {task.status.value}")

    blocked = unsatisfied_deps(state, task_id)
    if blocked:
        raise Refuse(f"unsatisfied deps: {', '.join(blocked)}")

    task.status = resulting_status(task.status, Action.IMPLEMENT)
    save_and_render(state, tasks_dir)
    return f"{task.id} → in-progress", 0


def propagate(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)
    if not can_transition(task.status, Action.PROPAGATE):
        raise Refuse(f"cannot propagate from status {task.status.value}")

    task.status = resulting_status(task.status, Action.PROPAGATE)
    save_and_render(state, tasks_dir)
    return f"{task.id} → propagating-context", 0


def done(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)
    if not can_transition(task.status, Action.DONE):
        raise Refuse(f"cannot mark done from status {task.status.value}")

    task.status = resulting_status(task.status, Action.DONE)
    save_and_render(state, tasks_dir)
    return f"{task.id} → done", 0


def cancel(task_id: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)
    if not can_transition(task.status, Action.CANCEL):
        raise Refuse(f"cannot cancel from status {task.status.value}")

    task.status = resulting_status(task.status, Action.CANCEL)
    save_and_render(state, tasks_dir)
    blocked = dependents(state, task_id)
    if blocked:
        return f"{task.id} → cancelled; blocked dependents: {', '.join(blocked)}", 0
    return f"{task.id} → cancelled", 0


def _find(state, task_id: str):
    try:
        return state.find_task(task_id)
    except KeyError:
        raise Refuse(f"no task with id {task_id}")


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


def _dir() -> str:
    from .base import tasks_dir

    return tasks_dir()
