"""Controller: `laaw task cancel`."""

import argparse

from ..core import lifecycle


def run(args: argparse.Namespace) -> tuple[str, int]:
    return lifecycle.cancel(task_id=args.id)
