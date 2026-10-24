"""Controller: `laaw task desc`."""

import argparse

from ..core import metadata


def run(args: argparse.Namespace) -> tuple[str, int]:
    return metadata.desc(task_id=args.id, text=args.desc)
