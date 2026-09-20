#!/usr/bin/env python3
"""LAAW tasks CLI — the single writer of .ai/tasks/state.json.

Task state (ids, names, statuses, file paths) lives in ONE file:
.ai/tasks/state.json. It is written only by this CLI, never by hand.
Markdown task files hold content only (Description, Steps, Validations,
Context updates, Notes) — no status is ever written to a markdown file.

The CLI enforces the status state machine from workflow.md §2: every
set-status call is validated, and illegal transitions are refused with an
instructional error. tools/test_tasks.py keeps this table in sync with
workflow.md.

Commands (run from the project root, or pass --root /path/to/project):
  init                          create .ai/tasks/ (state.json, .gitignore) and .ai/context/ (index.md)
  new <name> [--super] [--desc T]   scaffold a root task as draft
  subtask <root-id> <name> [--desc T]  scaffold a child of a super-task as draft
  rename <id> <new-name>        rename a draft task and its file(s)
  remove <id>                   delete a draft task (and draft children) and its file(s)
  set-status <id> <status>      flip a status; validates the transition (workflow.md §2)
  status [id]                   one task's status line, or the whole board
  board                         the whole board as a markdown table
  next                          print the active task and the exact next action/question
  check                         report state/file consistency problems
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

STATUSES = ("draft", "in-progress", "impl-review", "ctx-review", "done")
DONE = "done"

# (from, to) -> only writer skill. workflow.md §2 is the source of truth;
# tools/test_tasks.py keeps this table in sync with it.
TRANSITIONS = {
    ("none", "draft"): "plan-task",
    ("draft", "in-progress"): "implement-task",
    ("impl-review", "in-progress"): "implement-task",
    ("in-progress", "impl-review"): "implement-task",
    ("impl-review", "done"): "implement-task",
    ("impl-review", "ctx-review"): "propagate-context",
    ("in-progress", "ctx-review"): "propagate-context",
    ("ctx-review", "done"): "propagate-context",
}

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

DESCRIPTION_DEFAULT = "<what this task is and why — one short paragraph>"


def die(msg, code=1):
    print(f"tasks: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------- paths/state

def tasks_dir(root):
    return root / ".ai" / "tasks"


def state_path(root):
    return tasks_dir(root) / "state.json"


def load_state(root):
    p = state_path(root)
    if not p.exists():
        die(
            f"no state file at {p} — project not bootstrapped. "
            'Run the route skill with "bootstrap" (it runs: tasks.py init).'
        )
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as e:
        die(
            f"state file {p} is corrupt ({e}). Do not hand-edit state.json; "
            "report to the human instead of guessing."
        )


def save_state(root, st):
    td = tasks_dir(root)
    td.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(td), prefix=".state-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(st, f, indent=2)
            f.write("\n")
        os.replace(tmp, state_path(root))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def find_root(args, cmd):
    root = getattr(args, "root", None)
    if root:
        return Path(root).resolve()
    if cmd == "init":
        return Path.cwd().resolve()
    cwd = Path.cwd()
    ai_root = None
    for p in [cwd, *cwd.parents]:
        if (p / ".ai" / "tasks" / "state.json").exists():
            return p
        if ai_root is None and (p / ".ai").is_dir():
            ai_root = p
    if ai_root is not None:
        die(
            f"found .ai/ at {ai_root / '.ai'} but no .ai/tasks/state.json — "
            'not bootstrapped. Run the route skill with "bootstrap" from the project root.'
        )
    die(
        "could not find a project root (no .ai/ directory above the current directory). "
        "cd into the project or pass --root /path/to/project."
    )


def find_task(st, tid):
    for r in st["roots"]:
        if r["id"] == tid:
            return r, None
        for c in r.get("children", []):
            if c["id"] == tid:
                return c, r
    return None, None


# ---------------------------------------------------------------- helpers

def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if len(s) > 30:
        s = s[:30].rsplit("-", 1)[0].rstrip("-")
    return s or "task"


def scaffold_file(root, rel, tid, name, desc, is_super):
    tmpl_name = "super-task-template.md" if is_super else "task-template.md"
    tmpl_path = TEMPLATES / tmpl_name
    if not tmpl_path.exists():
        die(f"missing template {tmpl_path}. Re-sync .ai/workflow/ (tools/sync-workflow.py).")
    body = tmpl_path.read_text().replace("t{N}", tid)
    body = body.replace("{name}", name)
    body = body.replace("{description}", desc if desc else DESCRIPTION_DEFAULT)
    f = tasks_dir(root) / rel
    if f.exists():
        die(f"{f} already exists — refusing to overwrite.")
    if f.parent != tasks_dir(root):
        f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(body)


def legal_targets(task, is_root):
    """Statuses task may legally move to right now (shape-aware subset of §2)."""
    cur = task["status"]
    has_children = "children" in task
    allowed = set()
    if cur == "draft":
        allowed.add("in-progress")
    elif cur == "in-progress":
        if has_children:
            allowed.add("ctx-review")  # super-task: all subtasks done -> context gate
        else:
            allowed.add("impl-review")
    elif cur == "impl-review":
        if is_root:
            allowed.update(("in-progress", "ctx-review"))  # leaf root: fix / context gate
        else:
            allowed.update(("in-progress", "done"))  # subtask: fix / approved
    elif cur == "ctx-review":
        allowed.add("done")
    return allowed


def next_guidance(task, parent):
    tid, st = task["id"], task["status"]
    if st == "draft":
        return f"{tid} is draft — ask plan approval (plan-task), or work it if the human already approved."
    if st == "in-progress":
        if parent is not None:
            return f"Work {tid}'s Steps like a leaf task (implement-task), then: tasks.py set-status {tid} impl-review."
        if "children" in task:
            return f"{tid} stays in-progress while its subtasks are worked — implement-task walks them in ID order."
        return f"Work {tid}'s Steps (implement-task), then: tasks.py set-status {tid} impl-review."
    if st == "impl-review":
        return f'Now ask the human: "Approve implementation of {tid}?" — show the diff summary and validation results, then stop.'
    if st == "ctx-review":
        return f'Now ask the human: "Approve context changes for {tid}?" — show the exact context edits, then stop.'
    if st == DONE:
        if parent is not None:
            return f"{tid} is done. Continue to the next subtask of {parent['id']} (implement-task)."
        return f"{tid} is done."
    return ""


def render_board(st):
    lines = ["| id | name | status |", "|---|---|---|"]
    for r in st["roots"]:
        lines.append(f"| {r['id']} | {r['name']} | {r['status']} |")
        for c in r.get("children", []):
            lines.append(f"| {c['id']} | {c['name']} | {c['status']} |")
    return "\n".join(lines)


def require_draft(task, verb):
    if task["status"] != "draft":
        die(f"{task['id']} is not draft (it is {task['status']}) — only draft tasks may be {verb} on re-plan.")
    for c in task.get("children", []):
        if c["status"] != "draft":
            die(f"child {c['id']} is not draft (it is {c['status']}) — cannot {verb} {task['id']}.")


# ---------------------------------------------------------------- commands

def cmd_init(args, root):
    td = root / ".ai" / "tasks"
    if (td / "state.json").exists():
        die(f"already initialized — {td / 'state.json'} exists. Not touching it.")
    td.mkdir(parents=True, exist_ok=True)
    (td / ".gitignore").write_text("*\n")
    save_state(root, {"roots": []})
    cd = root / ".ai" / "context"
    cd.mkdir(parents=True, exist_ok=True)
    idx = cd / "index.md"
    if not idx.exists():
        idx.write_text("# Context index\n\n| file | summary |\n|---|---|\n")
    print(f"Initialized {td} (state.json) and {cd} (index.md).")


def cmd_new(args, root):
    st = load_state(root)
    n = max((int(r["id"][1:]) for r in st["roots"]), default=0) + 1
    tid = f"t{n}"
    slug = slugify(args.name)
    td = tasks_dir(root)
    if args.super:
        rel = f"{tid}_{slug}/task.md"
    else:
        rel = f"{tid}_{slug}.md"
    scaffold_file(root, rel, tid, args.name, args.desc, args.super)
    entry = {"id": tid, "name": args.name, "status": "draft", "file": rel}
    if args.super:
        entry["children"] = []
    st["roots"].append(entry)
    save_state(root, st)
    print(f"Created {tid} ({rel}) as draft.")
    if args.super:
        print(f"Next: add children with: tasks.py subtask {tid} <child name>, then fill the task files (plan-task).")
    else:
        print(f"Next: fill the task file sections (Context, Steps, Validations, Context updates) and ask plan approval (plan-task).")


def cmd_subtask(args, root):
    st = load_state(root)
    parent, _ = find_task(st, args.root_id)
    if parent is None or "children" not in parent:
        die(f"{args.root_id} is not a super-task (or not found). Create one with: tasks.py new <name> --super")
    k = max((int(c["id"].rsplit(".", 1)[1]) for c in parent["children"]), default=0) + 1
    cid = f"{args.root_id}.{k}"
    parent_file = tasks_dir(root) / parent["file"]
    folder = parent_file.parent
    rel = f"{folder.name}/{cid}_{slugify(args.name)}.md"
    scaffold_file(root, rel, cid, args.name, args.desc, False)
    parent["children"].append({"id": cid, "name": args.name, "status": "draft", "file": rel})
    save_state(root, st)
    print(f"Created {cid} ({rel}) as draft under {parent['id']}.")
    print("Next: fill the child task file, and add a line to the parent's Subtasks list (plan-task).")


def cmd_rename(args, root):
    st = load_state(root)
    task, parent = find_task(st, args.id)
    if task is None:
        die(f"no task with id {args.id}. See: tasks.py board")
    require_draft(task, "renamed")
    old_name = task["name"]
    new_slug = slugify(args.new_name)
    td = tasks_dir(root)
    if parent is None and "children" in task:
        old_dir = td / task["file"].rsplit("/", 1)[0]
        new_dir = old_dir.parent / f"{task['id']}_{new_slug}"
        if new_dir.exists():
            die(f"{new_dir} already exists.")
        os.rename(old_dir, new_dir)
        for c in task["children"]:
            c["file"] = c["file"].replace(old_dir.name + "/", new_dir.name + "/", 1)
        task["file"] = f"{new_dir.name}/task.md"
        header_file = new_dir / "task.md"
    else:
        old_file = td / task["file"]
        new_file = old_file.parent / f"{task['id']}_{new_slug}.md"
        if new_file.exists():
            die(f"{new_file} already exists.")
        os.rename(old_file, new_file)
        task["file"] = str(new_file.relative_to(td))
        header_file = new_file
    body = header_file.read_text().replace(f"# {task['id']} — {old_name}", f"# {task['id']} — {args.new_name}", 1)
    header_file.write_text(body)
    task["name"] = args.new_name
    save_state(root, st)
    print(f"Renamed {task['id']} to '{args.new_name}' ({task['file']}).")


def cmd_remove(args, root):
    st = load_state(root)
    task, parent = find_task(st, args.id)
    if task is None:
        die(f"no task with id {args.id}. See: tasks.py board")
    require_draft(task, "removed")
    td = tasks_dir(root)
    if parent is None and "children" in task:
        shutil.rmtree(td / task["file"].rsplit("/", 1)[0])
    else:
        (td / task["file"]).unlink()
    if parent is not None:
        parent["children"].remove(task)
    else:
        st["roots"].remove(task)
    save_state(root, st)
    print(f"Removed {task['id']} and its file(s).")


def cmd_set_status(args, root):
    st = load_state(root)
    task, parent = find_task(st, args.id)
    if task is None:
        die(f"no task with id {args.id}. See: tasks.py board")
    if args.status not in STATUSES:
        die(f"unknown status '{args.status}'. Known statuses: {', '.join(STATUSES)} (workflow.md §2).")
    cur = task["status"]
    is_root = parent is None
    if cur == DONE:
        die(f"{task['id']} is done — a done task never changes status again. If the work was wrong, plan a new task (plan-task).")
    allowed = legal_targets(task, is_root)
    if args.status not in allowed:
        die(
            f"illegal transition {cur} → {args.status} for {task['id']}. "
            f"Allowed from {cur}: {', '.join(sorted(allowed)) or 'none'}. "
            "See workflow.md §2 — report any mismatch instead of forcing a status."
        )
    task["status"] = args.status
    save_state(root, st)
    print(f"OK: {task['id']} {cur} → {args.status}.")
    g = next_guidance(task, parent)
    if g:
        print(f"Next: {g}")


def cmd_status(args, root):
    st = load_state(root)
    if getattr(args, "id", None):
        task, parent = find_task(st, args.id)
        if task is None:
            die(f"no task with id {args.id}. See: tasks.py board")
        kind = "child of " + parent["id"] if parent else "root"
        print(f"{task['id']} | {task['name']} | {task['status']} | {kind} | file: {task['file']}")
        return
    print(render_board(st))


def cmd_next(args, root):
    st = load_state(root)
    roots = [r for r in st["roots"] if r["status"] != DONE]
    if not roots:
        print("No active tasks. Offer plan-task for new work (workflow.md §7).")
        return
    if len(roots) > 1:
        print("Multiple active roots — ask the human which one to work (workflow.md §7):")
        for r in sorted(roots, key=lambda r: int(r["id"][1:])):
            print(f"  {r['id']} — {r['name']} ({r['status']})")
        return
    r = min(roots, key=lambda r: int(r["id"][1:]))
    tid, stt, f = r["id"], r["status"], r["file"]
    if stt == "draft":
        print(f'Ask the human: "Approve plan for {tid}?" — show {f} first. On approval, hand off to implement-task.')
    elif stt == "in-progress":
        if "children" in r:
            live = [c for c in r["children"] if c["status"] != DONE]
            if not live:
                print(f"All subtasks of {tid} are done. Run the parent's Validations, aggregate its Context updates, then hand off to propagate-context (workflow.md §7).")
            else:
                print(f"Hand off to implement-task. Next subtask of {tid}: {live[0]['id']} — {live[0]['name']}.")
        else:
            print(f"Hand off to implement-task for {tid} (file: {f}).")
    elif stt == "impl-review":
        print(f'Ask the human: "Approve implementation of {tid}?" — show the diff summary and validation results. On approval, hand off to propagate-context.')
    elif stt == "ctx-review":
        print(f'Ask the human: "Approve context changes for {tid}?" — show the exact context edits. On approval, propagate-context records/commits done.')


def cmd_check(args, root):
    problems = []
    warnings = []
    st_path = state_path(root)
    if not st_path.exists():
        die(f"no state file at {st_path} — run tasks.py init.")
    try:
        st = json.loads(st_path.read_text())
    except json.JSONDecodeError as e:
        die(f"state file is corrupt: {e}")
    td = tasks_dir(root)
    seen_root = set()
    root_num = 0
    for r in st["roots"]:
        rid = r["id"]
        try:
            root_num = max(root_num, int(rid[1:]))
        except (ValueError, IndexError):
            problems.append(f"root id '{rid}' does not match t<N>.")
            continue
        if rid in seen_root:
            problems.append(f"duplicate root id {rid}.")
        seen_root.add(rid)
        check_entry(r, td, problems)
        for c in r.get("children", []):
            check_entry(c, td, problems)
            cid = c["id"]
            if not cid.startswith(rid + "."):
                problems.append(f"child id {cid} is not under root {rid}.")
    if len(seen_root) != root_num:
        warnings.append(f"root ids are not contiguous 1..{root_num} (removed drafts leave gaps — usually fine).")
    # context index (prose-maintained, so warnings only)
    cd = root / ".ai" / "context"
    idx = cd / "index.md"
    if idx.exists():
        listed = set()
        for line in idx.read_text().splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 2 and cells[0] not in ("file", "") and not set(cells[0]) <= set("-: "):
                listed.add(cells[0])
        on_disk = {p.name for p in cd.iterdir() if p.is_file() and p.name != "index.md"}
        for f in sorted(on_disk - listed):
            warnings.append(f"context file {f} has no row in .ai/context/index.md.")
        for f in sorted(listed - on_disk):
            warnings.append(f"context index lists {f} but the file does not exist.")
    for w in warnings:
        print(f"warning: {w}")
    if problems:
        for p in problems:
            print(f"PROBLEM: {p}", file=sys.stderr)
        die(f"check found {len(problems)} problem(s). Fix via tasks.py commands — never by hand-editing state.json.")
    print("check: state and files are consistent.")


def check_entry(task, td, problems):
    tid, rel, status = task["id"], task["file"], task["status"]
    if status not in STATUSES:
        problems.append(f"{tid}: unknown status '{status}'.")
    f = td / rel
    if not f.exists():
        problems.append(f"{tid}: file {rel} listed in state.json does not exist.")
        return
    base = f.name
    if not base.startswith(tid + "_") and base != "task.md":
        problems.append(f"{tid}: file {rel} is not named by its id (expected prefix '{tid}_' or 'task.md').")


def main(argv=None):
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
    p = sub.add_parser("status", parents=[common], help="one task's status line, or the board")
    p.add_argument("id", nargs="?")
    sub.add_parser("board", parents=[common], help="the whole board as a markdown table")
    sub.add_parser("next", parents=[common], help="active task + exact next action/question")
    sub.add_parser("check", parents=[common], help="state/file consistency report")

    args = ap.parse_args(argv)
    root = find_root(args, args.cmd)
    {
        "init": cmd_init,
        "new": cmd_new,
        "subtask": cmd_subtask,
        "rename": cmd_rename,
        "remove": cmd_remove,
        "set-status": cmd_set_status,
        "status": cmd_status,
        "board": cmd_status,
        "next": cmd_next,
        "check": cmd_check,
    }[args.cmd](args, root)


if __name__ == "__main__":
    main()
