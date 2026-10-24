"""CLI package: argparse tree + dispatch for the LAAW task commands."""

import argparse
import importlib


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="laaw")
    sub = parser.add_subparsers(dest="group", required=True)

    task_parser = sub.add_parser("task")
    cmd = task_parser.add_subparsers(dest="command", required=True)

    p = cmd.add_parser("register")
    p.add_argument("--name", required=True)
    p.add_argument("--desc", default="")
    p.add_argument("--deps", nargs="*", default=[])
    p.set_defaults(func=_dispatch("register"))

    for name in ("plan", "implement", "propagate", "done", "cancel"):
        p = cmd.add_parser(name)
        p.add_argument("id")
        p.set_defaults(func=_dispatch(name))

    args = parser.parse_args(argv)
    return args.func(args)


def _dispatch(command: str):
    def wrapper(args: argparse.Namespace) -> int:
        module = importlib.import_module(f".{command}", package=__name__)
        return module.run(args)

    return wrapper
