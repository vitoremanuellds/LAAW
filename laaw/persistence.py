"""Filesystem access for the LAAW CLI. The only module that touches disk."""

import json
from pathlib import Path


def save_text(path: str, content: str) -> None:
    target = Path(path)
    ensure_dir(str(target.parent))
    target.write_text(content, encoding="utf-8")


def load_text(path: str) -> str:
    target = Path(path)
    if not target.is_file():
        raise FileNotFoundError(f"no file at {path}")
    return target.read_text(encoding="utf-8")


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def list_files(directory: str) -> list:
    root = Path(directory)
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_file())


def save_state(state, path: str) -> None:
    document = json.dumps(state.to_dict(), indent=2) + "\n"
    save_text(path, document)


def load_state(path: str):
    from .model.state import ProjectState

    return ProjectState.from_dict(json.loads(load_text(path)))
