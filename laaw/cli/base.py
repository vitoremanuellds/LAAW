"""Shared pipeline helpers for lifecycle commands. Load, mutate, save, render."""

import json
from pathlib import Path

from .. import persistence
from ..model.state import ProjectState, kebab
from ..render import render_subtasks_md, render_tasks_md


class Refuse(Exception):
    """Raised when a command must be refused; message is printed, nothing is written."""


def _tasks_dir() -> str:
    return str(Path.cwd() / ".ai" / "tasks")


def load(tasks_dir: str) -> ProjectState:
    path = str(Path(tasks_dir) / "tasks.json")
    return persistence.load_state(path)


def save_and_render(state: ProjectState, tasks_dir: str) -> None:
    document = json.dumps(state.to_dict(), indent=2) + "\n"
    persistence.save_text(str(Path(tasks_dir) / "tasks.json"), document)
    persistence.save_text(str(Path(tasks_dir) / "tasks.md"), render_tasks_md(state))
    for task in state.tasks:
        if task.type == "supertask":
            folder = Path(tasks_dir) / task_folder(task.id, task.name)
            persistence.save_text(str(folder / "subtasks.md"), render_subtasks_md(task))


def run_command(tasks_dir: str, action) -> int:
    """Load state, run action (may raise Refuse), save+render, print result.

    `action` is a callable taking ProjectState and returning a message string.
    On Refuse: prints reason, returns 1, writes nothing.
    If tasks.json does not exist yet, starts from an empty state.
    """
    try:
        state = load(tasks_dir)
    except FileNotFoundError:
        from ..model.state import ProjectState

        state = ProjectState()
    try:
        message = action(state)
    except Refuse as e:
        print(f"refused: {e}")
        return 1
    save_and_render(state, tasks_dir)
    print(message)
    return 0


def task_folder(task_id: str, name: str) -> str:
    return f"{task_id}_{kebab(name)}"
