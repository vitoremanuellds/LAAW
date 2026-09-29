#!/usr/bin/env python3
"""LAAW CLI — bootstrap the LAAW workflow into a project.

Subcommands:
  sync workflow [path]  Copy the workflow files into .ai/workflow/ of the
                        target project. `path` defaults to the current
                        directory. Also creates the .ai/tasks/ and
                        .ai/context/ skeleton with their indexes, and makes
                        sure .ai/tasks/ and .ai/workflow/ are git-ignored.
  sync skills <path>    Copy the skills from the LAAW skills/ folder into the
                        given path.
"""

import argparse
import shutil
import sys
from pathlib import Path

LAAW_ROOT = Path(__file__).resolve().parent

WORKFLOW_FILES = ("workflow.md",)

TASKS_INDEX_TEMPLATE = """# Task index

| ID | Status | Name | Description | Type | Dependencies |
|---|---|---|---|---|---|
"""

CONTEXT_INDEX_TEMPLATE = """# Context index

| Name | Description | Status |
|---|---|---|
"""


def sync_workflow(target: Path) -> None:
    if not target.is_dir():
        sys.exit(f"error: {target} is not a directory")

    dest = target / ".ai" / "workflow"
    dest.mkdir(parents=True, exist_ok=True)
    for name in WORKFLOW_FILES:
        src = LAAW_ROOT / name
        if not src.is_file():
            sys.exit(f"error: {src} not found in the LAAW checkout")
        shutil.copy2(src, dest / name)
        print(f"copied  {name} -> {dest / name}")

    # Skeleton: tasks/ and context/ with their indexes.
    for rel, template in (
        ("tasks", TASKS_INDEX_TEMPLATE),
        ("context", CONTEXT_INDEX_TEMPLATE),
    ):
        folder = target / ".ai" / rel
        folder.mkdir(parents=True, exist_ok=True)
        index = folder / "index.md"
        if index.exists():
            print(f"kept    {index}")
        else:
            index.write_text(template)
            print(f"created {index}")

    # Keep per-user folders (tasks, workflow copies) out of the repo by default.
    gitignore = target / ".gitignore"
    entries = [".ai/tasks/", ".ai/workflow/"]
    content = gitignore.read_text() if gitignore.exists() else ""
    if content and not content.endswith("\n"):
        content += "\n"
    added = [e for e in entries if e.rstrip("/") not in content]
    if added:
        gitignore.write_text(content + "".join(e + "\n" for e in added))
        print(f"updated {gitignore} (+ {' '.join(added)})")

    print(f"workflow synced into {target}")


def sync_skills(dest: Path) -> None:
    src = LAAW_ROOT / "skills"
    if not src.is_dir():
        sys.exit(f"error: {src} not found in the LAAW checkout")

    skills = sorted(p for p in src.iterdir() if p.is_dir())
    if not skills:
        sys.exit(f"error: no skills found in {src}")

    dest.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        shutil.copytree(skill, dest / skill.name, dirs_exist_ok=True)
        print(f"copied  {skill.name} -> {dest / skill.name}")

    print(f"{len(skills)} skill(s) synced into {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="laaw.py",
        description="Bootstrap the LAAW workflow into a project.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_sync = sub.add_parser("sync", help="sync workflow files or skills")
    sync_sub = p_sync.add_subparsers(dest="action", required=True)

    p_workflow = sync_sub.add_parser(
        "workflow",
        help="copy the workflow files into .ai/workflow/ of a project",
    )
    p_workflow.add_argument(
        "path",
        nargs="?",
        default=".",
        help="path to the project to bootstrap (default: current directory)",
    )

    p_skills = sync_sub.add_parser("skills", help="copy the skills into a path")
    p_skills.add_argument(
        "path",
        help="path to copy the skills into (e.g. .agents/skills or ~/.agents/skills)",
    )

    args = parser.parse_args()

    if args.command == "sync" and args.action == "workflow":
        sync_workflow(Path(args.path).expanduser().resolve())
    elif args.command == "sync" and args.action == "skills":
        sync_skills(Path(args.path).expanduser().resolve())


if __name__ == "__main__":
    main()
