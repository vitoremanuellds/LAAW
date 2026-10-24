"""Controller: `laaw task rename`."""

import argparse

from ..core import metadata


def run(args: argparse.Namespace) -> tuple[str, int]:
    return metadata.rename(task_id=args.id, name=args.name)
