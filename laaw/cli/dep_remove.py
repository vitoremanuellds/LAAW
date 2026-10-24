"""Controller: `laaw task dep-remove`."""

import argparse

from ..core import metadata


def run(args: argparse.Namespace) -> tuple[str, int]:
    return metadata.dep_remove(task_id=args.id, dep_id=args.dep)
