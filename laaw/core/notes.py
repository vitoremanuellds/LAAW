"""Core notes orchestrator: append a tagged note to a task, re-render notes files."""

from ..domain.notes import validate_note
from ..model.note import Note
from .base import Refuse, load_or_empty, save_and_render


def add_note(task_id: str, tag: str, text: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    task = _find(state, task_id)

    note = Note(tag=tag, text=text)
    try:
        validate_note(note)
    except ValueError as e:
        raise Refuse(str(e))
    task.notes.append(note)
    save_and_render(state, tasks_dir)
    return f"note added to {task_id} ({tag})", 0


def _find(state, task_id: str):
    try:
        return state.find_task(task_id)
    except KeyError:
        raise Refuse(f"no task with id {task_id}")


def _dir() -> str:
    from .base import tasks_dir

    return tasks_dir()
