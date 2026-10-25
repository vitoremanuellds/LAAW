"""CLI package: argparse tree + dispatch. Presentation only — no state logic."""

import argparse
import importlib

from ..core.base import Refuse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="laaw")
    sub = parser.add_subparsers(dest="group", required=True)

    task_parser = sub.add_parser("task")
    cmd = task_parser.add_subparsers(dest="command", required=True)

    p = cmd.add_parser("register")
    p.add_argument("--name", required=True)
    p.add_argument("--desc", default="")
    p.add_argument("--deps", nargs="*", default=[])
    p.add_argument("--subtask-of", default=None, metavar="PARENT_ID")
    p.set_defaults(func=_dispatch("register"))

    for name in ("plan", "implement", "propagate", "done", "cancel", "remove"):
        p = cmd.add_parser(name)
        p.add_argument("id")
        p.set_defaults(func=_dispatch(name))

    p = cmd.add_parser("rename")
    p.add_argument("id")
    p.add_argument("--name", required=True)
    p.set_defaults(func=_dispatch("rename"))

    p = cmd.add_parser("promote")
    p.add_argument("id")
    p.set_defaults(func=_dispatch("promote"))

    p = cmd.add_parser("desc")
    p.add_argument("id")
    p.add_argument("--desc", required=True)
    p.set_defaults(func=_dispatch("desc"))

    p = cmd.add_parser("dep-add")
    p.add_argument("id")
    p.add_argument("dep")
    p.set_defaults(func=_dispatch("dep_add"))

    p = cmd.add_parser("dep-remove")
    p.add_argument("id")
    p.add_argument("dep")
    p.set_defaults(func=_dispatch("dep_remove"))

    p = cmd.add_parser("note")
    p.add_argument("id")
    p.add_argument("--tag", required=True)
    p.add_argument("--text", required=True)
    p.set_defaults(func=_dispatch("note"))

    for name in ("deps", "dependents"):
        p = cmd.add_parser(name)
        p.add_argument("id")
        p.add_argument("--json", action="store_true")
        p.set_defaults(func=_dispatch(name))

    p = cmd.add_parser("check")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_dispatch("check"))

    p = cmd.add_parser("render")
    p.set_defaults(func=_dispatch("render"))

    sync_parser = sub.add_parser("sync")
    sync_cmd = sync_parser.add_subparsers(dest="command", required=True)

    p = sync_cmd.add_parser("workflow")
    p.add_argument("path", nargs="?", default=".")
    p.set_defaults(func=_dispatch("sync_workflow"))

    p = sync_cmd.add_parser("skills")
    p.add_argument("path")
    p.set_defaults(func=_dispatch("sync_skills"))

    args = parser.parse_args(argv)
    return args.func(args)


def _dispatch(command: str):
    def wrapper(args: argparse.Namespace) -> int:
        module = importlib.import_module(f".{command.replace('-', '_')}", package=__name__)
        try:
            message, code = module.run(args)
        except Refuse as e:
            print(f"refused: {e}")
            return 1
        print(message)
        return code

    return wrapper
