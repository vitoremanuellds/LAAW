"""Core render orchestrator: regenerate all generated files from state."""

from .base import load_or_empty, save_and_render, tasks_dir


def render() -> tuple[str, int]:
    directory = tasks_dir()
    state = load_or_empty(directory)
    save_and_render(state, directory)
    return "rendered all generated files", 0
