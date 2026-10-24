"""Controller: `laaw task dep-add`."""

import argparse

from ..core import metadata


def run(args: argparse.Namespace) -> tuple[str, int]:
    return metadata.dep_add(task_id=args.id, dep_id=args.dep)
