"""Task dataclass (simple or supertask). Pure — no filesystem access."""

from dataclasses import dataclass, field
from typing import Any

from ..status import Status
from .subtask import Subtask


@dataclass
class Task:
    id: str
    name: str
    desc: str
    type: str  # "simple" or "supertask"
    status: Status
    deps: list[str] = field(default_factory=list)
    subtasks: list[Subtask] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "type": self.type,
            "status": self.status.value,
            "deps": list(self.deps),
        }
        if self.subtasks:
            data["subtasks"] = [s.to_dict() for s in self.subtasks]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        raw_subtasks = data.get("subtasks", [])
        assert isinstance(raw_subtasks, list)
        subtasks = [Subtask.from_dict(s) for s in raw_subtasks]
        return cls(
            id=data["id"],
            name=data["name"],
            desc=data.get("desc", ""),
            type=data["type"],
            status=Status(data["status"]),
            deps=list(data.get("deps", [])),
            subtasks=subtasks,
        )
