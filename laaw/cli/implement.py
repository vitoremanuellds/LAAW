"""Controller: `laaw task implement`."""

import argparse

from ..core import lifecycle


def run(args: argparse.Namespace) -> tuple[str, int]:
    return lifecycle.implement(task_id=args.id)
