"""Controller: `laaw task done`."""

import argparse

from ..core import lifecycle


def run(args: argparse.Namespace) -> tuple[str, int]:
    return lifecycle.done(task_id=args.id)
