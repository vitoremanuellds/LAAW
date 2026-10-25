"""Core notes orchestrator: append a tagged note to a task, re-render notes files."""

from ..domain.notes import validate_note
from ..domain.status import Status
from ..model.note import Note
from ..model.state import Resolved
from .base import Refuse, load_or_empty, save_and_render


def add_note(task_id: str, tag: str, text: str) -> tuple[str, int]:
    tasks_dir = _dir()
    state = load_or_empty(tasks_dir)
    resolved = _find_any(state, task_id)
    if resolved.status is Status.NOT_PLANNED or resolved.status.terminal:
        raise Refuse(f"cannot note {task_id} from status {resolved.status.value}")

    note = Note(tag=tag, text=text)
    try:
        validate_note(note)
    except ValueError as e:
        raise Refuse(str(e))
    target = _target(state, resolved)
    target.notes.append(note)
    save_and_render(state, tasks_dir)
    return f"note added to {task_id} ({tag})", 0


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


def _dir() -> str:
    from .base import tasks_dir

    return tasks_dir()
