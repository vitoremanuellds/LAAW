"""Controller: `laaw task propagate`."""

import argparse

from ..core import lifecycle


def run(args: argparse.Namespace) -> tuple[str, int]:
    return lifecycle.propagate(task_id=args.id)
