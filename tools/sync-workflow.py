#!/usr/bin/env python3
"""Installs or re-syncs this repo's workflow content into a target project.

Copies workflow.md, skills/, templates/, reference/, README.md, and tools/
into a target project's .ai/workflow/ — the copy-based replacement for
`git submodule add`/`git submodule update --remote`.

First run against a target with no .ai/workflow/ yet: fresh install.
Any later run against the same target: re-sync — .ai/workflow/'s
content is wholesale-replaced with the source's current state. There
is no partial-merge logic: .ai/workflow/ is never supposed to be
hand-edited (workflow.md §3), so there is nothing local to preserve.

Every run also (re)writes a version-stamp file, .ai/workflow-version,
as a SIBLING of .ai/workflow/ (never inside it, so .ai/workflow/
stays a byte-for-byte mirror of the source).

Usage:
    python tools/sync-workflow.py                          # source = this script's checkout, target = current directory
    python tools/sync-workflow.py /path/to/LAAW-checkout     # explicit source, target = current directory
    python tools/sync-workflow.py /path/to/LAAW-checkout /path/to/your-project  # explicit source and target
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def die(message):
    print(f"sync-workflow: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    # Parse arguments
    if len(sys.argv) > 1:
        source_dir = Path(sys.argv[1])
    else:
        source_dir = Path(__file__).resolve().parent.parent

    if len(sys.argv) > 2:
        target_root = Path(sys.argv[2])
    else:
        target_root = Path.cwd()

    # Validate source
    if not (source_dir / "workflow.md").exists():
        die(
            f"{source_dir} doesn't look like a LAAW checkout "
            "(no workflow.md found there)."
        )

    dest = target_root / ".ai" / "workflow"
    stamp = target_root / ".ai" / "workflow-version"

    # Check if dest already exists (re-sync vs fresh install)
    was_existing = dest.exists()
    if was_existing:
        shutil.rmtree(dest)

    # Create destination
    dest.mkdir(parents=True, exist_ok=True)

    # Copy files and directories from source to dest
    items_to_copy = [
        "workflow.md",
        "skills",
        "templates",
        "reference",
        "README.md",
        "tools",
    ]

    for item in items_to_copy:
        src = source_dir / item
        dst = dest / item
        if src.is_dir():
            shutil.copytree(src, dst)
        elif src.is_file():
            shutil.copy2(src, dst)

    # Version stamp
    stamp.parent.mkdir(parents=True, exist_ok=True)

    # Get commit SHA (tolerate absent git)
    try:
        result = subprocess.run(
            ["git", "-C", str(source_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        sha = result.stdout.strip() if result.returncode == 0 else "unknown"
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        sha = "unknown"

    # Get source label
    try:
        result = subprocess.run(
            ["git", "-C", str(source_dir), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        source_label = result.stdout.strip() if result.returncode == 0 else str(source_dir)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        source_label = str(source_dir)

    if sha == "unknown":
        print(
            f"Warning: {source_dir} isn't a git checkout — "
            f'recording commit as "unknown".',
            file=sys.stderr,
        )

    now_utc = datetime.now(timezone.utc)
    stamp_content = (
        f"source={source_label}\n"
        f"commit={sha}\n"
        f"date={now_utc.strftime('%Y-%m-%d')}\n"
    )

    with open(stamp, "w") as f:
        f.write(stamp_content)

    # Print result
    if was_existing:
        print(f"Re-synced .ai/workflow/ at {target_root}")
    else:
        print(f"Installed .ai/workflow/ at {target_root}")
    print(f"Stamped commit: {sha}")


if __name__ == "__main__":
    main()
