"""Shared helpers for core orchestrator tests."""

import json
from pathlib import Path

from laaw.model.state import ProjectState


def write_state(tmp: str, state: ProjectState) -> None:
    path = Path(tmp) / "tasks.json"
    path.write_text(json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8")


def read_state(tmp: str) -> ProjectState:
    from laaw.persistence import load_state

    return load_state(str(Path(tmp) / "tasks.json"))


def state_json_bytes(tmp: str) -> bytes:
    return (Path(tmp) / "tasks.json").read_bytes()


def run_in_dir(func, tmp: str, *args, **kwargs):
    """Run a core function with tasks_dir patched to `tmp`."""
    from laaw.core import base

    original = base.tasks_dir
    base.tasks_dir = lambda: tmp
    try:
        return func(*args, **kwargs)
    finally:
        base.tasks_dir = original
