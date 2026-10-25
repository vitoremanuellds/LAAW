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

AGENTS_WORKFLOW_SECTION = """## Workflow

This project uses LAAW. Before doing any task work, read `.ai/workflow/workflow.md` and follow it. For planning, implementation, and context propagation, use the `plan-task`, `implement-task`, and `propagate-context` skills.
"""

AGENTS_WORKFLOW_MARKER = "## Workflow\n\nThis project uses LAAW."


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

    agents = _ensure_agents_md(target)
    added = _ensure_gitignore_entries(target)
    return (
        f"workflow synced into {target}"
        + (f"; created {', '.join(created)}" if created else "")
        + (f"; AGENTS.md {agents}" if agents else "")
        + (f"; gitignore + {' '.join(added)}" if added else ""),
        0,
    )


def _ensure_agents_md(target: str) -> str:
    """Ensure <target>/AGENTS.md has the Workflow section. Returns 'created'/'appended'/''."""
    agents = Path(target) / "AGENTS.md"
    if not agents.is_file():
        persistence.save_text(str(agents), AGENTS_WORKFLOW_SECTION)
        return "created"
    content = persistence.load_text(str(agents))
    if AGENTS_WORKFLOW_MARKER in content:
        return ""
    if content and not content.endswith("\n"):
        content += "\n"
    persistence.save_text(str(agents), content + "\n" + AGENTS_WORKFLOW_SECTION)
    return "appended"


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
