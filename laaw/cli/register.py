"""Controller: `laaw task register`."""

import argparse

from ..core import lifecycle


def run(args: argparse.Namespace) -> tuple[str, int]:
    return lifecycle.register(name=args.name, desc=args.desc, deps=args.deps)
