"""Pure markdown rendering of the generated table files. No filesystem access."""

from ..constants import GENERATED_HEADER
from ..model.state import ProjectState
from ..model.subtask import Subtask
from ..model.task import Task

TABLE_HEADER = ("ID", "Status", "Name", "Description", "Type", "Dependencies")


def _table(header: tuple[str, ...], rows: list[tuple[str, ...]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("|" + "|".join("---" for _ in header) + "|")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def _task_row(task: Task) -> tuple[str, ...]:
    return (
        task.id,
        task.status.value,
        task.name,
        task.desc,
        task.type,
        ", ".join(task.deps),
    )


def render_tasks_md(state: ProjectState) -> str:
    rows = [_task_row(task) for task in state.tasks]
    lines = [GENERATED_HEADER, "# Tasks", ""] + _table(TABLE_HEADER, rows)
    return "\n".join(lines) + "\n"


def render_subtasks_md(task: Task) -> str:
    if not task.subtasks:
        lines = [GENERATED_HEADER, f"# Subtasks of {task.id}", "", "(no subtasks)"]
        return "\n".join(lines) + "\n"
    rows = [_subtask_row(sub) for sub in task.subtasks]
    lines = [GENERATED_HEADER, f"# Subtasks of {task.id}", ""] + _table(TABLE_HEADER, rows)
    return "\n".join(lines) + "\n"


def _subtask_row(sub: Subtask) -> tuple[str, ...]:
    return (
        sub.id,
        sub.status.value,
        sub.name,
        sub.desc,
        "subtask",
        ", ".join(sub.deps),
    )
