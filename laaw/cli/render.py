"""Controller: `laaw task render`."""

import argparse

from ..core import render_cmd


def run(args: argparse.Namespace) -> tuple[str, int]:
    return render_cmd.render()
