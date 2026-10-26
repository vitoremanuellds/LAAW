"""Controller: `laaw file check <path>`."""

import argparse

from ..core import file_check


def run(args: argparse.Namespace) -> tuple[str, int]:
    return file_check.check(path=args.path)
