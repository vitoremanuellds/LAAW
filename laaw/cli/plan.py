"""Controller: `laaw task plan`."""

import argparse

from ..core import lifecycle


def run(args: argparse.Namespace) -> tuple[str, int]:
    return lifecycle.plan(task_id=args.id)
