#!/usr/bin/env python3
"""Mirrors this repo's skills/ into <project-root>/.agents/skills/.

For harnesses that auto-discover skills there instead of (or in addition
to) following workflow.md's explicit skill lookup table.

Adds any skill not already present; overwrites any that already
exist with the current version. Does NOT remove skills that were
deleted upstream — check manually after a workflow update if that
matters to you.

Usage:
    python tools/sync-skills.py                    # assumes standard .ai/workflow/ mount
    python tools/sync-skills.py /path/to/.agents/skills  # explicit destination
"""

import shutil
import sys
from pathlib import Path


def die(message):
    print(f"sync-skills: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    # Parse arguments
    if len(sys.argv) > 1:
        skills_dest = Path(sys.argv[1])
    else:
        # Standard mount point is .ai/workflow/ — project root is two
        # levels up from the skills directory.
        script_dir = Path(__file__).resolve().parent
        workflow_dir = script_dir.parent  # .ai/workflow/
        if not workflow_dir.is_dir():
            die(f"no .ai/workflow/ found at {workflow_dir}")
        project_root = workflow_dir.parent.parent  # two levels up
        skills_dest = project_root / ".agents" / "skills"
        print("No destination given — assuming standard mount point.")
        print(f"Project root resolved to: {project_root}")

    # Source skills directory
    script_dir = Path(__file__).resolve().parent
    skills_src = script_dir.parent / "skills"

    if not skills_src.is_dir():
        die(f"no skills/ found at {skills_src}")

    # Create destination
    skills_dest.mkdir(parents=True, exist_ok=True)

    added = 0
    updated = 0

    for skill_dir in sorted(skills_src.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_name = skill_dir.name
        dest = skills_dest / skill_name

        if dest.exists():
            print(f"  updating  {skill_name}")
            updated += 1
        else:
            print(f"  adding    {skill_name}")
            added += 1

        # Remove existing and copy fresh
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(skill_dir, dest)

    print()
    print(f"Done: {added} added, {updated} updated. Synced to {skills_dest}")
    print("Remember to re-run this after every workflow update —")
    print("these are copies, not links, and will silently go stale otherwise.")


if __name__ == "__main__":
    main()
