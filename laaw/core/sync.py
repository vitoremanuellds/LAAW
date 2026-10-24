"""Core sync orchestrators: sync workflow files and skills into a project."""

import shutil
from pathlib import Path

from .. import persistence

LAAW_ROOT = Path(__file__).resolve().parents[2]

WORKFLOW_FILES = ("workflow.md",)

TASKS_INDEX_TEMPLATE = """# Task index

| ID | Status | Name | Description | Type | Dependencies |
|---|---|---|---|---|---|
"""

CONTEXT_INDEX_TEMPLATE = """# Context index

| Name | Description | Status |
|---|---|---|
"""

GITIGNORE_ENTRIES = (".ai/tasks/", ".ai/workflow/")


def sync_workflow(target: str) -> tuple[str, int]:
    target = str(Path(target).expanduser().resolve())
    if not Path(target).is_dir():
        return f"error: {target} is not a directory", 1

    dest = Path(target) / ".ai" / "workflow"
    persistence.ensure_dir(str(dest))
    for name in WORKFLOW_FILES:
        src = LAAW_ROOT / name
        if not src.is_file():
            return f"error: {src} not found in the LAAW checkout", 1
        shutil.copy2(src, dest / name)

    created = []
    for rel, template in (
        ("tasks", TASKS_INDEX_TEMPLATE),
        ("context", CONTEXT_INDEX_TEMPLATE),
    ):
        folder = Path(target) / ".ai" / rel
        persistence.ensure_dir(str(folder))
        index = folder / "index.md"
        if not index.is_file():
            persistence.save_text(str(index), template)
            created.append(str(index))

    added = _ensure_gitignore_entries(target)
    return (
        f"workflow synced into {target}"
        + (f"; created {', '.join(created)}" if created else "")
        + (f"; gitignore + {' '.join(added)}" if added else ""),
        0,
    )


def _ensure_gitignore_entries(target: str) -> list[str]:
    gitignore = Path(target) / ".gitignore"
    content = persistence.load_text(str(gitignore)) if gitignore.is_file() else ""
    if content and not content.endswith("\n"):
        content += "\n"
    added = [e for e in GITIGNORE_ENTRIES if e.rstrip("/") not in content]
    if added:
        persistence.save_text(str(gitignore), content + "".join(e + "\n" for e in added))
    return added


def sync_skills(dest: str) -> tuple[str, int]:
    dest = str(Path(dest).expanduser().resolve())
    src = LAAW_ROOT / "skills"
    if not src.is_dir():
        return f"error: {src} not found in the LAAW checkout", 1

    skills = sorted(p for p in src.iterdir() if p.is_dir())
    if not skills:
        return f"error: no skills found in {src}", 1

    persistence.ensure_dir(dest)
    for skill in skills:
        shutil.copytree(skill, Path(dest) / skill.name, dirs_exist_ok=True)
    return f"{len(skills)} skill(s) synced into {dest}", 0
