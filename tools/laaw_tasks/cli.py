"""Argument parsing + command wiring for the LAAW tasks CLI.

Commands are thin orchestration only: discover the root, build a Store, load
the State, perform the one business operation, save, print. No workflow rules
and no file paths live here. main(argv) returns an exit code and never raises
for expected failures — TaskError (and raw OSError from the disk) becomes the
documented 'tasks: …' stderr message and exit 1.
"""

import argparse
import sys
from pathlib import Path

from .errors import TaskError
from .persistence import Store
from .report import BoardRenderer, NextGuidance, NextOutput
from .state import State, STATUSES

# .ai/context/index.md content created by `init` (kept minimal; the
# propagate-context skill maintains it from then on).
CONTEXT_INDEX_SEED = "# Context index\n\n| file | summary |\n|---|---|\n"


class CLI:
    """CLI command dispatcher. Each command is a method that receives
    parsed args and a Store instance.
    """

    def __init__(self, root):
        self.store = Store(root)

    # ---- root discovery

    @classmethod
    def discover_root(cls, args, cmd):
        root = getattr(args, "root", None)
        if root:
            return Path(root).resolve()
        if cmd == "init":
            return Path.cwd().resolve()
        cwd = Path.cwd()
        ai_root = None
        for p in [cwd, *cwd.parents]:
            if (p / ".ai").is_dir():
                if ai_root is None:
                    ai_root = p
                if Store(p).state_path.exists():
                    return p
        if ai_root is not None:
            raise TaskError(
                f"found .ai/ at {ai_root / '.ai'} but no .ai/tasks/state.json — "
                'not bootstrapped. Run the route skill with "bootstrap" from the project root.'
            )
        raise TaskError(
            "could not find a project root (no .ai/ directory above the current directory). "
            "cd into the project or pass --root /path/to/project."
        )

    # ---- commands

    def cmd_init(self, args):
        if self.store.exists("state.json"):
            raise TaskError(f"already initialized — {self.store.state_path} exists. Not touching it.")
        State(self.store, {"roots": []}).save()
        self.store.write(".gitignore", "*\n")
        if self.store.context_index() is None:
            self.store.write_context_index(CONTEXT_INDEX_SEED)
        print(f"Initialized {self.store.tasks_dir} (state.json) and {self.store.context_dir} (index.md).")

    def cmd_new(self, args):
        st = State.load(self.store)
        task, rel = st.add_root(args.name, args.desc, args.super)
        st.save()
        print(f"Created {task.id} ({rel}) as draft.")
        if args.super:
            print(f"Next: add children with: tasks.py subtask {task.id} <child name>, then fill the task files (plan-task).")
        else:
            print("Next: fill the task file sections (Context, Steps, Validations, Context updates) and ask plan approval (plan-task).")

    def cmd_subtask(self, args):
        st = State.load(self.store)
        task, rel = st.add_subtask(args.root_id, args.name, args.desc)
        st.save()
        print(f"Created {task.id} ({rel}) as draft under {args.root_id}.")
        print("Next: fill the child task file, and add a line to the parent's Subtasks list (plan-task).")

    def cmd_rename(self, args):
        st = State.load(self.store)
        task = st.rename(args.id, args.new_name)
        st.save()
        print(f"Renamed {task.id} to '{task.name}' ({task.file}).")

    def cmd_remove(self, args):
        st = State.load(self.store)
        task = st.remove(args.id)
        st.save()
        print(f"Removed {task.id} and its file(s).")

    def cmd_set_status(self, args):
        st = State.load(self.store)
        cur = st.set_status(args.id, args.status)
        st.save()
        task, parent = st.find(args.id)
        print(f"OK: {task.id} {cur} → {args.status}.")
        statuses = {t.id: t.status for t, _ in st.all_tasks()}
        g = NextGuidance().get_guidance(task, parent, statuses)
        if g:
            print(f"Next: {g}")

    def cmd_depends(self, args):
        if not args.dep_ids and not args.clear:
            raise TaskError("give one or more dep ids, or --clear.")
        st = State.load(self.store)
        task = st.set_depends(args.id, [] if args.clear else args.dep_ids)
        st.save()
        if task.depends:
            print(f"OK: {task.id} now depends on {', '.join(task.depends)}.")
        else:
            print(f"OK: {task.id} has no depends-on.")

    def cmd_status(self, args):
        st = State.load(self.store)
        tid = getattr(args, "id", None)
        if tid:
            task, parent = st.find(tid)
            if task is None:
                raise TaskError(f"no task with id {tid}. See: tasks.py board")
            kind = "child of " + parent.id if parent else "root"
            line = f"{task.id} | {task.name} | {task.status} | {kind} | file: {task.file}"
            if task.depends:
                line += f" | depends: {', '.join(task.depends)}"
            print(line)
            return
        print(BoardRenderer().render(st.roots))

    def cmd_next(self, args):
        st = State.load(self.store)
        print(NextOutput().get_output(st.roots))

    def cmd_check(self, args):
        st = State.load(self.store)
        problems, warnings = st.check()
        for w in warnings:
            print(f"warning: {w}")
        if problems:
            for p in problems:
                print(f"PROBLEM: {p}", file=sys.stderr)
            raise TaskError(
                f"check found {len(problems)} problem(s). Fix via tasks.py commands — never by hand-editing state.json."
            )
        print("check: state and files are consistent.")

    # ---- dispatch table

    COMMANDS = {
        "init": "cmd_init",
        "new": "cmd_new",
        "subtask": "cmd_subtask",
        "rename": "cmd_rename",
        "remove": "cmd_remove",
        "set-status": "cmd_set_status",
        "depends": "cmd_depends",
        "status": "cmd_status",
        "board": "cmd_status",
        "next": "cmd_next",
        "check": "cmd_check",
    }

    def run(self, args):
        """Dispatch to the appropriate command method."""
        method_name = self.COMMANDS[args.cmd]
        method = getattr(self, method_name)
        method(args)


# ---------------------------------------------------------------- parser

def build_parser():
    # --root is accepted both before and after the subcommand. The subparser
    # default is SUPPRESS so a missing sub-level --root does not clobber the
    # main-level value.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        default=argparse.SUPPRESS,
        help="project root (default: discovered by walking up from the current directory)",
    )
    ap = argparse.ArgumentParser(description="LAAW tasks CLI — single writer of .ai/tasks/state.json.")
    ap.add_argument("--root", default=None, help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", parents=[common], help="create .ai/tasks/ and .ai/context/ scaffolding")
    p = sub.add_parser("new", parents=[common], help="scaffold a root task as draft")
    p.add_argument("name")
    p.add_argument("--super", action="store_true", help="super-task (folder + task.md, gets subtasks)")
    p.add_argument("--desc", default=None, help="fill the Description line")
    p = sub.add_parser("subtask", parents=[common], help="scaffold a child of a super-task as draft")
    p.add_argument("root_id")
    p.add_argument("name")
    p.add_argument("--desc", default=None)
    p = sub.add_parser("rename", parents=[common], help="rename a draft task and its file(s)")
    p.add_argument("id")
    p.add_argument("new_name")
    p = sub.add_parser("remove", parents=[common], help="delete a draft task and its file(s)")
    p.add_argument("id")
    p = sub.add_parser("set-status", parents=[common], help="flip a status (validated against workflow.md §2)")
    p.add_argument("id")
    p.add_argument("status", choices=STATUSES)
    p = sub.add_parser("depends", parents=[common], help="set a task's depends-on list (draft tasks only, replaces it)")
    p.add_argument("id")
    p.add_argument("dep_ids", nargs="*", help="task ids this task depends on")
    p.add_argument("--clear", action="store_true", help="remove all depends-on entries")
    p = sub.add_parser("status", parents=[common], help="one task's status line, or the board")
    p.add_argument("id", nargs="?")
    sub.add_parser("board", parents=[common], help="the whole board as a markdown table")
    sub.add_parser("next", parents=[common], help="active task + exact next action/question")
    sub.add_parser("check", parents=[common], help="state/file consistency report")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        root = CLI.discover_root(args, args.cmd)
        cli = CLI(root)
        cli.run(args)
    except TaskError as e:
        print(f"tasks: {e}", file=sys.stderr)
        return 1
    except OSError as e:  # disk/permission failures that escaped the Store
        print(f"tasks: file system error: {e}", file=sys.stderr)
        return 1
    return 0
