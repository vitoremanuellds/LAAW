"""Note dataclass: a single tagged observation. Pure — no filesystem access."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Note:
    tag: str
    text: str

    def word_count(self) -> int:
        return len(self.text.split())

    def to_dict(self) -> dict[str, Any]:
        return {"tag": self.tag, "text": self.text}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Note":
        return cls(tag=data["tag"], text=data["text"])
