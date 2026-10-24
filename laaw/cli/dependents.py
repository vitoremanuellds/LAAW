"""Controller: `laaw task dependents`."""

import argparse

from ..core import query


def run(args: argparse.Namespace) -> tuple[str, int]:
    return query.dependents(task_id=args.id, as_json=args.json)
