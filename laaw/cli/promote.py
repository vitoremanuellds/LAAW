"""Controller: `laaw task promote`."""

import argparse

from ..core import metadata


def run(args: argparse.Namespace) -> tuple[str, int]:
    return metadata.promote(task_id=args.id)
