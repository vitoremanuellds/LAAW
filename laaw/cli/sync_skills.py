"""Controller: `laaw sync skills`."""

import argparse
from pathlib import Path

from ..core import sync


def run(args: argparse.Namespace) -> tuple[str, int]:
    return sync.sync_skills(str(Path(args.path).expanduser().resolve()))
