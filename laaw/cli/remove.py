"""Controller: `laaw task remove`."""

import argparse

from ..core import lifecycle


def run(args: argparse.Namespace) -> tuple[str, int]:
    return lifecycle.remove(task_id=args.id)
