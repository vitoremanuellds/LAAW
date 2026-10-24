"""Controller: `laaw sync workflow`."""

import argparse
from pathlib import Path

from ..core import sync


def run(args: argparse.Namespace) -> tuple[str, int]:
    return sync.sync_workflow(str(Path(args.path).expanduser().resolve()))
