"""Dataclasses for the LAAW task model. Pure — no filesystem access."""

from dataclasses import dataclass, field
from typing import List

from ..status import Status


@dataclass
class Subtask:
    id: str
    name: str
    desc: str
    status: Status
    deps: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "status": self.status.value,
            "deps": list(self.deps),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Subtask":
        return cls(
            id=data["id"],
            name=data["name"],
            desc=data.get("desc", ""),
            status=Status(data["status"]),
            deps=list(data.get("deps", [])),
        )
