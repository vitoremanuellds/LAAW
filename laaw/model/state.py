"""ProjectState: the in-memory aggregate over all tasks. Pure — no filesystem.

Holds an ordered list of Task, and owns ID generation, slug generation with
collision auto-suffix, and add/find operations. Serialization to/from the
tasks.json document shape lives here; actual file IO is persistence.py (t07.2).
"""

from dataclasses import dataclass, field
from typing import Any

from ..constants import SLUG_SEPARATOR, ZERO_PAD_WIDTH
from .subtask import Subtask
from .task import Task


@dataclass
class ProjectState:
    version: int = 1
    tasks: list[Task] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"version": self.version, "tasks": [t.to_dict() for t in self.tasks]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectState":
        raw_tasks = data.get("tasks", [])
        assert isinstance(raw_tasks, list)
        return cls(
            version=data.get("version", 1),
            tasks=[Task.from_dict(t) for t in raw_tasks],
        )

    # --- lookup -------------------------------------------------------------

    def find_task(self, task_id: str) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"no task with id {task_id}")

    def find_subtask(self, parent_id: str, subtask_id: str) -> Subtask:
        parent = self.find_task(parent_id)
        for sub in parent.subtasks:
            if sub.id == subtask_id:
                return sub
        raise KeyError(f"no subtask {subtask_id} under {parent_id}")

    # --- id generation ------------------------------------------------------

    def next_top_level_id(self) -> str:
        highest = max((_number(t.id) for t in self.tasks), default=0)
        return format_number(highest + 1)

    def next_subtask_id(self, parent_id: str) -> str:
        parent = self.find_task(parent_id)
        highest = max((_sub_number(s.id) for s in parent.subtasks), default=0)
        return f"{parent_id}.{highest + 1}"

    # --- slug ---------------------------------------------------------------

    def slug(self, name: str, taken: set[str] | None = None) -> str:
        base = kebab(name)
        taken = taken or set()
        candidate = base
        suffix = 2
        while candidate in taken:
            candidate = f"{base}{SLUG_SEPARATOR}{suffix}"
            suffix += 1
        return candidate

    # --- mutation -----------------------------------------------------------

    def add_task(self, task: Task) -> None:
        if self.find_task_or_none(task.id):
            raise ValueError(f"task id {task.id} already exists")
        self.tasks.append(task)

    def find_task_or_none(self, task_id: str) -> Task | None:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None


def _number(task_id: str) -> int:
    return int(task_id.lstrip("t"))


def _sub_number(subtask_id: str) -> int:
    return int(subtask_id.rsplit(".", 1)[1])


def format_number(n: int) -> str:
    width = max(ZERO_PAD_WIDTH, len(str(n)))
    return f"t{n:0{width}d}"


def kebab(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif not out or out[-1] != SLUG_SEPARATOR:
            out.append(SLUG_SEPARATOR)
    return "".join(out).strip(SLUG_SEPARATOR)
