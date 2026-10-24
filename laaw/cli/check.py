"""Controller: `laaw task check`."""

import argparse

from ..core import query


def run(args: argparse.Namespace) -> tuple[str, int]:
    return query.check(as_json=args.json)
