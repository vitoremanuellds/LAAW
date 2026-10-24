"""Shared transaction helpers for the core layer."""

import json
from pathlib import Path

from .. import persistence
from ..domain.notes import render_notes
from ..domain.render import render_subtasks_md, render_tasks_md
from ..model.note import Note
from ..model.state import ProjectState, kebab


class Refuse(Exception):
    """Raised by core logic to refuse an action; nothing is written."""


def tasks_dir() -> str:
    return str(Path.cwd() / ".ai" / "tasks")


def load_or_empty(tasks_dir: str) -> ProjectState:
    path = str(Path(tasks_dir) / "tasks.json")
    try:
        return persistence.load_state(path)
    except FileNotFoundError:
        return ProjectState()


def task_folder(task_id: str, name: str) -> str:
    return f"{task_id}_{kebab(name)}"


def save_and_render(state: ProjectState, tasks_dir: str) -> None:
    document = json.dumps(state.to_dict(), indent=2) + "\n"
    persistence.save_text(str(Path(tasks_dir) / "tasks.json"), document)
    persistence.save_text(str(Path(tasks_dir) / "tasks.md"), render_tasks_md(state))
    for task in state.tasks:
        folder = Path(tasks_dir) / task_folder(task.id, task.name)
        if task.type == "supertask":
            persistence.save_text(str(folder / "subtasks.md"), render_subtasks_md(task))
        notes_files = render_notes(list(task.notes))
        for filename, text in notes_files.items():
            persistence.save_text(str(folder / filename), text)


def notes_of(state: ProjectState, task_id: str) -> list[Note]:
    return state.find_task(task_id).notes
