"""Dataclasses for the LAAW task model. Pure — no filesystem access."""

from dataclasses import dataclass, field
from typing import Any

from ..domain.status import Status
from .note import Note


@dataclass
class Subtask:
    id: str
    name: str
    desc: str
    status: Status
    deps: list[str] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "status": self.status.value,
            "deps": list(self.deps),
        }
        if self.notes:
            data["notes"] = [n.to_dict() for n in self.notes]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Subtask":
        raw_notes = data.get("notes", [])
        assert isinstance(raw_notes, list)
        notes = [Note.from_dict(n) for n in raw_notes]
        return cls(
            id=data["id"],
            name=data["name"],
            desc=data.get("desc", ""),
            status=Status(data["status"]),
            deps=list(data.get("deps", [])),
            notes=notes,
        )
