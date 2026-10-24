"""Controller: `laaw task note`."""

import argparse

from ..core import notes


def run(args: argparse.Namespace) -> tuple[str, int]:
    return notes.add_note(task_id=args.id, tag=args.tag, text=args.text)
