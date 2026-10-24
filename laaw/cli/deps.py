"""Controller: `laaw task deps`."""

import argparse

from ..core import query


def run(args: argparse.Namespace) -> tuple[str, int]:
    return query.deps(task_id=args.id, as_json=args.json)
