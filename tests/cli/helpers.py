"""Shared helpers for CLI lifecycle command tests."""

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


def run_in_dir(cmd_module, args, tmp: str) -> int:
    """Run a command module with base._tasks_dir patched to `tmp`."""
    from laaw.cli import base

    original = base._tasks_dir
    base._tasks_dir = lambda: tmp
    try:
        return cmd_module.run(args)
    finally:
        base._tasks_dir = original
