#!/usr/bin/env python3
"""LAAW tasks CLI — single-file, object-oriented task state manager.

Task state (ids, names, statuses, file paths) lives in ONE file:
.ai/tasks/state.json. It is written only by this CLI — never by hand.

This file replaces the multi-file laaw_tasks/ package. Every concern is
separated into its own class or method group:

    TaskError          — exception type
    Slugifier          — slug generation (pure function)
    Task               — recursive task model (has children)
    StateMachine       — status transitions, validation rules
    State              — in-memory model, CRUD operations
    TaskFileRenderer   — builds task markdown (no external templates)
    BoardRenderer      — board table output
    NextOutput         — next-guidance output
    Persistence        — disk I/O (load/save state.json, task files, context)
    LAAWCLI            — CLI entry point (only module-level code outside classes)

Usage:
    python laaw.py <state.json> init
    python laaw.py <state.json> new <name> [--super] [--desc T]
    python laaw.py <state.json> subtask <root-id> <name> [--desc T]
    python laaw.py <state.json> rename <id> <new-name>
    python laaw.py <state.json> remove <id>
    python laaw.py <state.json> set-status <id> <status>
    python laaw.py <state.json> depends <id> <dep-id>… [--clear]
    python laaw.py <state.json> status [id]
    python laaw.py <state.json> board
    python laaw.py <state.json> next
    python laaw.py <state.json> check
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterator


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class TaskError(Exception):
    """Recoverable error: print 'laaw: <msg>' to stderr, exit 1."""


# ---------------------------------------------------------------------------
# Slugifier (pure function — no class needed for a stateless utility)
# ---------------------------------------------------------------------------

def _slugify(name: str) -> str:
    """Generate a URL-safe slug from a task name."""
    MAX_LENGTH = 30
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if len(s) > MAX_LENGTH:
        s = s[:MAX_LENGTH].rsplit("-", 1)[0].rstrip("-")
    return s or "task"


# ---------------------------------------------------------------------------
# Task — the recursive model
# ---------------------------------------------------------------------------

class Task:
    """Recursive task model. Children are nested Task objects.

    JSON is a serialization format for this class — not the other way around.
    The Task class is the source of truth.
    """

    STATUSES = ("created", "planning", "in-progress", "contextualizing", "done")
    DONE = "done"

    __slots__ = ("id", "name", "status", "file", "description",
                 "children", "depends", "is_super")

    def __init__(
        self,
        id: str,
        name: str,
        status: str = "created",
        file: str | None = None,
        description: str | None = None,
        children: list["Task"] | None = None,
        depends: list[str] | None = None,
        is_super: bool = False,
    ):
        self.id = id
        self.name = name
        self.status = status
        self.file = file
        self.description = description
        self.children = list(children) if children else []
        self.depends = list(depends) if depends else []
        # Explicit so it survives serialization even with no children yet.
        self.is_super = is_super

    # ---- serialization

    @classmethod
    def from_json(cls, data: dict) -> "Task":
        """Deserialize a Task from a JSON dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            status=data["status"],
            file=data.get("file"),
            description=data.get("description"),
            children=[cls.from_json(c) for c in data.get("children", [])],
            depends=data.get("depends", []),
            is_super="children" in data,
        )

    def to_json(self) -> dict:
        """Serialize this Task to a JSON-compatible dict."""
        d: dict = {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "file": self.file,
        }
        if self.description:
            d["description"] = self.description
        if self.is_super or self.children:
            d["children"] = [c.to_json() for c in self.children]
        if self.depends:
            d["depends"] = list(self.depends)
        return d

    # ---- shape helpers

    @property
    def is_leaf(self) -> bool:
        return not self.children

    @property
    def is_done(self) -> bool:
        return self.status == self.DONE

    # ---- iteration

    def _iter_all(self) -> Iterator[tuple["Task", "Task | None"]]:
        """Yield (self, parent) and recursively yield all descendants."""
        yield self, None
        for child in self.children:
            yield from child._iter_descendants(self)

    def _iter_descendants(self, parent: "Task") -> Iterator[tuple["Task", "Task"]]:
        """Yield (child, parent) for all descendants of self."""
        for child in self.children:
            yield child, parent
            yield from child._iter_descendants(child)

    def find_child(self, child_id: str) -> "Task | None":
        """Find a direct child by ID (recursive through siblings)."""
        for child in self.children:
            if child.id == child_id:
                return child
            found = child.find_child(child_id)
            if found:
                return found
        return None

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, name={self.name!r}, status={self.status!r})"


# ---------------------------------------------------------------------------
# StateMachine — pure validation logic
# ---------------------------------------------------------------------------

class StateMachine:
    """Pure validation rules for task status transitions.

    Never mutates Task objects — only validates and returns the previous
    status (or raises TaskError). Mirrors workflow.md §2.
    """

    # (from, to) → allowed skill
    TRANSITIONS: dict[tuple[str, str], str] = {
        ("created", "planning"): "plan-task",
        ("planning", "in-progress"): "implement-task",
        ("in-progress", "contextualizing"): "propagate-context",
        ("contextualizing", "done"): "propagate-context",
    }

    @classmethod
    def can_transition(cls, task: Task, parent: Task | None, new_status: str) -> str:
        """Validate transition and return previous status.

        Raises TaskError if the transition is illegal.
        """
        if new_status not in Task.STATUSES:
            raise TaskError(
                f"unknown status '{new_status}'. Known statuses: "
                f"{', '.join(Task.STATUSES)} (workflow.md §2)."
            )
        if task.status == Task.DONE:
            raise TaskError(
                f"{task.id} is done — a done task never changes status again. "
                "If the work was wrong, plan a new task (plan-task)."
            )

        allowed = cls.get_allowed_statuses(task, parent)
        if new_status not in allowed:
            raise TaskError(
                f"illegal transition {task.status} → {new_status} for {task.id}. "
                f"Allowed from {task.status}: "
                f"{', '.join(sorted(allowed)) or 'none'}. "
                "See workflow.md §2 — report any mismatch instead of forcing a status."
            )

        prev = task.status
        task.status = new_status
        return prev

    @classmethod
    def get_allowed_statuses(cls, task: Task, parent: Task | None) -> set[str]:
        """Return the set of statuses task can legally move to."""
        cur = task.status
        return {to for (frm, to) in cls.TRANSITIONS if frm == cur}

    @staticmethod
    def require_created(task: Task, verb: str) -> None:
        """Raise if task is not created."""
        if task.status != "created":
            raise TaskError(
                f"{task.id} is not created (it is {task.status}) — only created tasks "
                f"may be {verb} (workflow.md §2)."
            )

    @staticmethod
    def require_planning(task: Task, verb: str) -> None:
        """Raise if task is not planning."""
        if task.status != "planning":
            raise TaskError(
                f"{task.id} is not planning (it is {task.status}) — only planning tasks "
                f"may be {verb} (workflow.md §2)."
            )

    @staticmethod
    def require_in_progress(task: Task, verb: str) -> None:
        """Raise if task is not in-progress."""
        if task.status != "in-progress":
            raise TaskError(
                f"{task.id} is not in-progress (it is {task.status}) — only in-progress "
                f"tasks may be {verb} (workflow.md §2)."
            )

    @staticmethod
    def require_contextualizing(task: Task, verb: str) -> None:
        """Raise if task is not contextualizing."""
        if task.status != "contextualizing":
            raise TaskError(
                f"{task.id} is not contextualizing (it is {task.status}) — only "
                f"contextualizing tasks may be {verb} (workflow.md §2)."
            )

    @staticmethod
    def require_replannable(task: Task, parent: Task, verb: str) -> None:
        """Raise if task is not created or parent is past the planning gate."""
        if task.status != "created":
            raise TaskError(
                f"{task.id} is not created (it is {task.status}) — only created tasks "
                f"may be {verb} on re-plan (workflow.md §4)."
            )
        if parent.status not in ("created", "planning"):
            raise TaskError(
                f"{task.id} cannot be {verb} — parent {parent.id} is {parent.status} "
                "(re-planning ends at the planning gate; workflow.md §4)."
            )

    @staticmethod
    def find_blocking(task: Task, statuses: dict[str, str]) -> list[tuple[str, str | None]]:
        """Return unmet dependencies as [(dep_id, status), ...]."""
        return [(d, statuses.get(d)) for d in task.depends if statuses.get(d) != Task.DONE]


# ---------------------------------------------------------------------------
# Persistence — disk I/O layer
# ---------------------------------------------------------------------------

class Persistence:
    """File access for one project's .ai/ tree.

    Path layout lives here and only here. All other modules reach the disk
    through this class.

    The root is derived from the state file path: the state file is expected
    at <root>/.ai/tasks/state.json, so root = state_path.parent.parent.parent.
    """

    def __init__(self, state_path: Path):
        # state_path is expected to be <root>/.ai/tasks/state.json
        self._state_path = state_path.resolve()
        # <root>/.ai/tasks/state.json
        # parent:       <root>/.ai/tasks
        # parent.parent: <root>/.ai
        # parent.parent.parent: <root> (project root)
        self.root = self._state_path.parent.parent.parent
        self._tasks_dir = self._state_path.parent  # <root>/.ai/tasks

    # ---- paths

    @property
    def tasks_dir(self) -> Path:
        return self._tasks_dir

    @property
    def state_path(self) -> Path:
        return self._state_path

    @property
    def context_dir(self) -> Path:
        return self.root / ".ai" / "context"

    def task_path(self, rel: str) -> Path:
        return self.tasks_dir / rel

    # ---- state.json

    def load_state(self) -> dict:
        """Read and parse state.json. Raises TaskError if missing/corrupt."""
        p = self.state_path
        if not p.exists():
            raise TaskError(
                f"no state file at {p} — project not bootstrapped. "
                'Run laaw.py with "init" first.'
            )
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise TaskError(
                f"state file {p} is corrupt ({e}). Do not hand-edit state.json; "
                "report to the human instead of guessing."
            ) from e

    def save_state(self, data: dict) -> None:
        """Atomically write state.json (temp file + rename)."""
        td = self.tasks_dir
        td.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(td), prefix=".state-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            os.replace(tmp, self.state_path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    # ---- task files

    def exists(self, rel: str) -> bool:
        return self.task_path(rel).exists()

    def read(self, rel: str) -> str:
        p = self.task_path(rel)
        try:
            return p.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise TaskError(
                f"task file {p} does not exist — state/file mismatch; "
                "run: laaw.py <state.json> check"
            ) from None

    def write(self, rel: str, content: str) -> None:
        """Write content to task file rel, creating parent dirs."""
        p = self.task_path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def remove(self, rel: str) -> None:
        p = self.task_path(rel)
        try:
            p.unlink()
        except FileNotFoundError:
            raise TaskError(f"task file {p} does not exist (already deleted?).") from None

    def remove_tree(self, rel: str) -> None:
        p = self.task_path(rel)
        try:
            shutil.rmtree(p)
        except (FileNotFoundError, OSError):
            raise TaskError(f"{p} does not exist or could not be removed.") from None

    def move(self, src_rel: str, dst_rel: str) -> None:
        """Rename a task file or super-task folder."""
        src, dst = self.task_path(src_rel), self.task_path(dst_rel)
        try:
            os.rename(src, dst)
        except FileNotFoundError:
            raise TaskError(f"{src} does not exist — cannot move to {dst}.") from None

    # ---- context

    def load_context_index(self) -> str | None:
        idx = self.context_dir / "index.md"
        if not idx.exists():
            return None
        return idx.read_text(encoding="utf-8")

    def save_context_index(self, content: str) -> None:
        self.context_dir.mkdir(parents=True, exist_ok=True)
        (self.context_dir / "index.md").write_text(content, encoding="utf-8")

    def context_files(self) -> set[str]:
        """Names of context files on disk (index.md excluded)."""
        if not self.context_dir.is_dir():
            return set()
        return {
            p.name for p in self.context_dir.iterdir()
            if p.is_file() and p.name != "index.md"
        }


# ---------------------------------------------------------------------------
# TaskFileRenderer — builds markdown in Python (no external templates)
# ---------------------------------------------------------------------------

class TaskFileRenderer:
    """Build task markdown files from Task objects.

    Replaces external template files with in-Python template generation.
    """

    DESCRIPTION_DEFAULT = "<what this task is and why — one short paragraph>"

    @classmethod
    def render_leaf(cls, task: Task) -> str:
        """Render a leaf task file (flat .md)."""
        desc = task.description or cls.DESCRIPTION_DEFAULT
        return (
            f"# {task.id} — {task.name}\n"
            f"\n"
            f"Status: created\n"
            f"\n"
            f"Description: {desc}\n"
            f"\n"
            f"In scope:\n"
            f"- {desc}\n"
            f"\n"
            f"Out of scope:\n"
            f"- (define at plan time)\n"
            f"\n"
            f"Context:\n"
            f"- (context files to read at plan time)\n"
            f"\n"
            f"Steps:\n"
            f"- [ ] (define at plan time)\n"
            f"\n"
            f"Validations:\n"
            f"- (define at plan time)\n"
            f"\n"
            f"Context updates:\n"
            f"- (define at plan time)\n"
            f"\n"
            f"Notes:\n"
        )

    @classmethod
    def render_super_parent(cls, task: Task) -> str:
        """Render a super-task parent file (task.md inside folder)."""
        desc = task.description or cls.DESCRIPTION_DEFAULT
        children_lines = "- (add subtasks with: laaw.py <state.json> subtask "
        children_lines += f"{task.id} <child name>)" if not task.children else ""
        return (
            f"# {task.id} — {task.name}\n"
            f"\n"
            f"Status: created\n"
            f"\n"
            f"Description: {desc}\n"
            f"\n"
            f"In scope:\n"
            f"- {desc}\n"
            f"\n"
            f"Out of scope:\n"
            f"- (define at plan time)\n"
            f"\n"
            f"Context:\n"
            f"- (context files to read at plan time)\n"
            f"\n"
            f"Subtasks:\n"
            f"{children_lines}\n"
            f"\n"
            f"Validations:\n"
            f"- (define at plan time)\n"
            f"\n"
            f"Context updates:\n"
            f"- (aggregate from subtasks at plan time)\n"
            f"\n"
            f"Notes:\n"
        )

    @classmethod
    def render_child(cls, task: Task) -> str:
        """Render a subtask child file."""
        desc = task.description or cls.DESCRIPTION_DEFAULT
        return (
            f"# {task.id} — {task.name}\n"
            f"\n"
            f"Status: created\n"
            f"\n"
            f"Description: {desc}\n"
            f"\n"
            f"In scope:\n"
            f"- {desc}\n"
            f"\n"
            f"Out of scope:\n"
            f"- (define at plan time)\n"
            f"\n"
            f"Context:\n"
            f"- (context files to read at plan time)\n"
            f"\n"
            f"Steps:\n"
            f"- [ ] (define at plan time)\n"
            f"\n"
            f"Validations:\n"
            f"- (define at plan time)\n"
            f"\n"
            f"Context updates:\n"
            f"- (define at plan time)\n"
            f"\n"
            f"Notes:\n"
        )

    @classmethod
    def render(cls, task: Task) -> str:
        """Dispatch to the correct renderer based on task type."""
        if task.is_super:
            return cls.render_super_parent(task)
        return cls.render_leaf(task)


# ---------------------------------------------------------------------------
# BoardRenderer — board table output
# ---------------------------------------------------------------------------

class BoardRenderer:
    """Render the task board as a markdown table."""

    @staticmethod
    def render(roots: list[Task]) -> str:
        lines = ["| id | name | status | depends |", "|---|---|---|---|"]
        for root in roots:
            lines.append(_task_row(root))
            for child in root.children:
                lines.append(_task_row(child))
        return "\n".join(lines)


def _task_row(task: Task) -> str:
    """Format a single task as a markdown table row."""
    return (
        f"| {task.id} | {task.name} | {task.status} | "
        f"{', '.join(task.depends) or '—'} |"
    )


# ---------------------------------------------------------------------------
# NextOutput — next-action guidance
# ---------------------------------------------------------------------------

class NextOutput:
    """Generate next-action guidance for tasks."""

    @staticmethod
    def get_guidance(
        task: Task,
        parent: Task | None,
        statuses: dict[str, str],
    ) -> str:
        """Get the next guidance string after a status flip."""
        tid, st = task.id, task.status

        if st == "planning":
            return (
                f"{tid} is planning — ask plan approval (plan-task), "
                f"or work it if the human already approved."
            )

        if st == "in-progress":
            if parent is not None:
                return (
                    f"Work {tid}'s Steps like a leaf task (implement-task), "
                    f"then: laaw.py <state.json> set-status {tid} contextualizing. "
                    "When you ask for approval, STOP — the next subtask starts "
                    "only on the human's approval message."
                )
            if task.is_super:
                if not task.children:
                    return (
                        f"{tid} has no subtasks yet — plan-task must add them "
                        f"before work can start: laaw.py <state.json> subtask "
                        f"{tid} <child name>."
                    )
                if all(c.status == Task.DONE for c in task.children):
                    return (
                        f"All subtasks of {tid} are done. Run the parent's Validations, "
                        f"aggregate Context updates, then: laaw.py <state.json> "
                        f"set-status {tid} contextualizing."
                    )
                return (
                    f"{tid} stays in-progress while its subtasks are worked — "
                    f"implement-task walks them in ID order."
                )
            return (
                f"Work {tid}'s Steps (implement-task), then: "
                f"laaw.py <state.json> set-status {tid} contextualizing. "
                "When you ask for approval, STOP — do not start any other work this turn."
            )

        if st == "contextualizing":
            return (
                f'Now ask the human: "Approve context changes for {tid}?" — '
                "show the exact context edits, then stop. Continue only on "
                "the human's answer."
            )

        if st == Task.DONE:
            if parent is not None:
                live = [c for c in parent.children if c.status != Task.DONE]
                if not live:
                    return (
                        f"{tid} is done and every subtask of {parent.id} is done — "
                        "run the parent's Validations, aggregate Context updates, "
                        "then hand off to propagate-context (workflow.md §7)."
                    )
                nxt = live[0]
                blocked = StateMachine.find_blocking(nxt, statuses)
                if blocked:
                    names = ", ".join(
                        f"{d} ({statuses.get(d) or 'unknown'})" for d, _ in blocked
                    )
                    return (
                        f"{tid} is done, but the next subtask {nxt.id} is blocked by "
                        f"{names} — do not start it; ask the human how to proceed."
                    )
                return f"{tid} is done. Continue to {nxt.id} (implement-task)."
            return f"{tid} is done."

        return ""

    @staticmethod
    def get_output(roots: list[Task]) -> str:
        """Generate the 'next' command output (workflow.md §7)."""
        all_roots = list(roots)
        active = [r for r in all_roots if r.status != Task.DONE]
        statuses = {t.id: t.status for t, _ in _iter_all_tasks(roots)}

        if not active:
            return "No active tasks. Offer plan-task for new work (workflow.md §7)."

        if len(active) > 1:
            lines = [
                "Multiple active roots — ask the human which one to work "
                "(workflow.md §7):"
            ]
            for r in sorted(active, key=lambda t: NextOutput._sort_key(t.id)):
                line = f"  {r.id} — {r.name} ({r.status})"
                blocked = StateMachine.find_blocking(r, statuses)
                if blocked:
                    names = ", ".join(
                        f"{d} ({statuses.get(d) or 'unknown'})" for d, _ in blocked
                    )
                    line += f" [BLOCKED by {names}]"
                lines.append(line)
            return "\n".join(lines)

        root = min(active, key=lambda t: NextOutput._sort_key(t.id))
        tid = root.id

        if root.status == "planning":
            blocked = StateMachine.find_blocking(root, statuses)
            if blocked:
                names = ", ".join(
                    f"{d} ({statuses.get(d) or 'unknown'})" for d, _ in blocked
                )
                return (
                    f"{tid} is BLOCKED by {names} — its plan is not ready to approve. "
                    "Resume the blocking task, or ask the human to revise the plan "
                    "(plan-task/plan-project; workflow.md §7)."
                )
            return (
                f'Ask the human: "Approve plan for {tid}?" — show '
                f"{root.file} first. On approval, hand off to implement-task."
            )

        if root.status == "in-progress":
            if root.is_super:
                if not root.children:
                    return (
                        f"{tid} has no subtasks yet — plan-task must add them "
                        f"before work can start: laaw.py <state.json> subtask "
                        f"{tid} <child name>."
                    )
                live = [c for c in root.children if c.status != Task.DONE]
                if not live:
                    return (
                        f"All subtasks of {tid} are done. Run the parent's Validations, "
                        f"aggregate its Context updates, then hand off to propagate-context "
                        f"(workflow.md §7)."
                    )
                first = live[0]
                out = (
                    f"Hand off to implement-task. Next subtask of {tid}: "
                    f"{first.id} — {first.name}."
                )
                blocked = StateMachine.find_blocking(first, statuses)
                if blocked:
                    names = ", ".join(
                        f"{d} ({statuses.get(d) or 'unknown'})" for d, _ in blocked
                    )
                    out += (
                        f"\n  NOTE: {first.id} is BLOCKED by {names} — "
                        "do not start it; ask the human (workflow.md §7)."
                    )
                return out
            return f"Hand off to implement-task for {tid} (file: {root.file})."

        if root.status == "contextualizing":
            return (
                f'Ask the human: "Approve context changes for {tid}?" — show '
                "the exact context edits. On approval, propagate-context "
                "records/commits done."
            )

        return ""

    @staticmethod
    def _sort_key(task_id: str) -> int:
        try:
            return int(task_id[1:])
        except (ValueError, IndexError):
            raise TaskError(
                f"task id '{task_id}' does not match t<N> — state.json looks corrupt; "
                "run: laaw.py <state.json> check"
            ) from None


def _iter_all_tasks(roots: list[Task]) -> Iterator[tuple[Task, Task | None]]:
    """Yield (task, parent) for every root and child."""
    for root in roots:
        yield root, None
        for child in root.children:
            yield child, root


# ---------------------------------------------------------------------------
# State — in-memory model with CRUD
# ---------------------------------------------------------------------------

class State:
    """In-memory model of the task board.

    Holds a list of root Task objects. Delegates status validation to
    StateMachine and file I/O to Persistence.
    """

    def __init__(self, roots: list[Task]):
        self.roots = list(roots)

    # ---- load / save

    @classmethod
    def load(cls, persistence: Persistence) -> "State":
        """Load state from disk via persistence layer."""
        data = persistence.load_state()
        roots = [Task.from_json(r) for r in data["roots"]]
        return cls(roots)

    def save(self, persistence: Persistence) -> None:
        """Persist current state to disk."""
        data = {"roots": [root.to_json() for root in self.roots]}
        persistence.save_state(data)

    # ---- lookup

    def find(self, task_id: str) -> tuple[Task | None, Task | None]:
        """(task, parent) for task_id, or (None, None)."""
        for root in self.roots:
            if root.id == task_id:
                return root, None
            child = root.find_child(task_id)
            if child:
                return child, root
        return None, None

    def all_tasks(self) -> Iterator[tuple[Task, Task | None]]:
        """Yield (task, parent) for every root and child."""
        for root in self.roots:
            yield root, None
            for child in root.children:
                yield child, root

    def status_map(self) -> dict[str, str]:
        """Map every task id to its status."""
        return {tid: st for tid, st in ((t.id, t.status) for t, _ in self.all_tasks())}

    # ---- id generation

    def next_root_id(self) -> str:
        nums = []
        for r in self.roots:
            try:
                nums.append(int(r.id[1:]))
            except (ValueError, IndexError):
                raise TaskError(
                    f"root id '{r.id}' does not match t<N> — "
                    "state.json looks corrupt; run: laaw.py <state.json> check"
                ) from None
        return f"t{max(nums, default=0) + 1}"

    def next_child_id(self, parent: Task) -> str:
        try:
            k = max(
                (int(c.id.rsplit(".", 1)[1]) for c in parent.children),
                default=0,
            )
        except (ValueError, IndexError):
            raise TaskError(
                f"a child id under {parent.id} does not match t<N>.k — "
                "state.json looks corrupt; run: laaw.py <state.json> check"
            ) from None
        return f"{parent.id}.{k + 1}"

    # ---- status transitions

    def set_status(self, task_id: str, new_status: str) -> str:
        """Validate and apply a status change. Returns previous status."""
        task, parent = self.find(task_id)
        if task is None:
            raise TaskError(f"no task with id {task_id}. See: laaw.py <state.json> board")
        self._assert_unblocked(task)
        return StateMachine.can_transition(task, parent, new_status)

    def _assert_unblocked(self, task: Task) -> None:
        """Refuse any flip of a blocked task (depends-on not all done)."""
        if not task.depends:
            return
        statuses = self.status_map()
        blocked = StateMachine.find_blocking(task, statuses)
        if blocked:
            names = ", ".join(
                f"{d} ({statuses.get(d) or 'unknown'})" for d, _ in blocked
            )
            raise TaskError(
                f"{task.id} is blocked by {names} — its depends-on tasks must all "
                f"be done before {task.id} can leave draft (workflow.md §4)."
            )

    # ---- depends-on

    def set_depends(
        self,
        task_id: str,
        dep_ids: list[str],
        clear: bool = False,
    ) -> Task:
        """Replace a task's depends-on list (created or planning tasks only)."""
        task, parent = self.find(task_id)
        if task is None:
            raise TaskError(f"no task with id {task_id}. See: laaw.py <state.json> board")
        if parent is not None:
            StateMachine.require_replannable(task, parent, "re-wired")
        else:
            StateMachine.require_created(task, "re-wired")
        task.depends = list(dict.fromkeys(dep_ids))
        self._validate_depends()
        return task

    def _validate_depends(self) -> None:
        """Check for self-deps, unknown deps, scope, and cycles."""
        by_id = {t.id: t for t, _ in self.all_tasks()}

        # Self-deps, unknown deps, and scope validation
        for task, parent in self.all_tasks():
            for dep_id in task.depends:
                if dep_id == task.id:
                    raise TaskError(f"{task.id} cannot depend on itself.")
                if dep_id not in by_id:
                    raise TaskError(
                        f"{task.id} depends on unknown task '{dep_id}'. "
                        "Use: laaw.py <state.json> board"
                    )
                # Scope: roots depend on roots; subtasks on same-scope subtasks
                dep_task, dep_parent = self.find(dep_id)
                if parent is None:
                    # Root task — dep must also be a root
                    if dep_parent is not None:
                        raise TaskError(
                            f"{task.id} (root) cannot depend on {dep_id} "
                            f"(subtask of {dep_parent.id}). "
                            "Roots depend only on roots."
                        )
                else:
                    # Subtask — dep must be a subtask of the same super-task
                    if dep_parent is None or dep_parent.id != parent.id:
                        if dep_parent is None:
                            raise TaskError(
                                f"{task.id} (subtask of {parent.id}) cannot depend on "
                                f"{dep_id} (root). Subtasks depend only on "
                                "subtasks of the same super-task."
                            )
                        raise TaskError(
                            f"{task.id} (subtask of {parent.id}) cannot depend on "
                            f"{dep_id} (subtask of {dep_parent.id}). "
                            "Subtasks depend only on subtasks of the same super-task."
                        )

        # Cycle detection (DFS with white/grey/black coloring)
        WHITE, GREY, BLACK = 0, 1, 2
        color = {tid: WHITE for tid in by_id}

        def visit(tid: str) -> None:
            color[tid] = GREY
            for dep_id in by_id[tid].depends:
                if color[dep_id] == GREY:
                    raise TaskError(
                        f"depends-on cycle detected ({tid} → {dep_id}). "
                        "Dependencies must form a partial order."
                    )
                if color[dep_id] == WHITE:
                    visit(dep_id)
            color[tid] = BLACK

        for tid in by_id:
            if color[tid] == WHITE:
                visit(tid)

    # ---- lifecycle

    def add_root(
        self,
        name: str,
        description: str | None = None,
        is_super: bool = False,
        depends: list[str] | None = None,
    ) -> tuple[Task, str]:
        """Create root task, register, then scaffold file."""
        task_id = self.next_root_id()
        slug = _slugify(name)
        rel = f"{task_id}_{slug}/task.md" if is_super else f"{task_id}_{slug}.md"

        # Create and register the task in memory first
        task = Task(
            id=task_id,
            name=name,
            status="created",
            file=rel,
            description=description,
            is_super=is_super,
            depends=depends or [],
        )
        self.roots.append(task)

        # Validate dependencies before returning
        if depends:
            self._validate_depends()

        return task, rel

    def add_subtask(
        self,
        parent_id: str,
        name: str,
        description: str | None = None,
        depends: list[str] | None = None,
    ) -> tuple[Task, str]:
        """Create child task, register, then scaffold file."""
        parent, _ = self.find(parent_id)
        if parent is None:
            raise TaskError(f"no task with id {parent_id}. See: laaw.py <state.json> board")
        if not parent.is_super:
            raise TaskError(
                f"{parent_id} is not a super-task. Create one with: "
                f"laaw.py <state.json> new <name> --super"
            )
        if parent.status not in ("created", "in-progress"):
            raise TaskError(
                f"{parent.id} left created (it is {parent.status}) — "
                "its shape is fixed; subtasks can only be added while it is "
                "created or in-progress (workflow.md §4)."
            )

        child_id = self.next_child_id(parent)
        folder = parent.file.rsplit("/", 1)[0]
        rel = f"{folder}/{child_id}_{_slugify(name)}.md"

        # Create and register the child in memory first
        child = Task(
            id=child_id,
            name=name,
            status="created",
            file=rel,
            description=description,
            depends=depends or [],
        )
        parent.children.append(child)

        # Validate dependencies before returning
        if depends:
            self._validate_depends()

        return child, rel

    def _scaffold_file(self, rel: str, task_id: str, name: str,
                       description: str | None, is_super: bool) -> None:
        """Create the task file on disk."""
        if self._persistence.exists(rel):
            raise TaskError(
                f"{self._persistence.task_path(rel)} already exists — "
                "refusing to overwrite."
            )
        task = Task(id=task_id, name=name, description=description, is_super=is_super)
        content = TaskFileRenderer.render(task)
        self._persistence.write(rel, content)

    def draft_task(self, task_id: str) -> tuple[Task, str]:
        """Write the task file template and flip status to planning."""
        task, parent = self.find(task_id)
        if task is None:
            raise TaskError(f"no task with id {task_id}. See: laaw.py <state.json> board")
        StateMachine.require_created(task, "draft")
        if parent is not None:
            StateMachine.require_replannable(task, parent, "draft")

        # Scaffold the file
        self._scaffold_file(task.file, task.id, task.name, task.description, task.is_super)

        # Flip status
        prev = StateMachine.can_transition(task, parent, "planning")
        return task, prev

    def rename(self, task_id: str, new_name: str) -> Task:
        """Rename a created or planning task and its file(s)."""
        task, parent = self.find(task_id)
        if task is None:
            raise TaskError(f"no task with id {task_id}. See: laaw.py <state.json> board")
        if parent is not None:
            StateMachine.require_replannable(task, parent, "renamed")
        else:
            StateMachine.require_created(task, "renamed")

        old_name = task.name
        new_slug = _slugify(new_name)

        if not parent and task.is_super:
            old_dir = task.file.rsplit("/", 1)[0]
            new_dir = f"{task.id}_{new_slug}"
            if self._persistence.exists(new_dir):
                raise TaskError(
                    f"{self._persistence.task_path(new_dir)} already exists."
                )
            self._persistence.move(old_dir, new_dir)
            for child in task.children:
                child.file = child.file.replace(old_dir + "/", new_dir + "/", 1)
            task.file = f"{new_dir}/task.md"
            header_rel = task.file
        else:
            folder = f"{parent.file.rsplit('/', 1)[0]}/" if parent else ""
            new_rel = f"{folder}{task.id}_{new_slug}.md"
            if self._persistence.exists(new_rel):
                raise TaskError(
                    f"{self._persistence.task_path(new_rel)} already exists."
                )
            self._persistence.move(task.file, new_rel)
            task.file = new_rel
            header_rel = new_rel

        body = self._persistence.read(header_rel)
        body = body.replace(
            f"# {task.id} — {old_name}",
            f"# {task.id} — {new_name}",
            1,
        )
        self._persistence.write(header_rel, body)
        task.name = new_name
        return task

    def remove(self, task_id: str) -> Task:
        """Remove a created or planning task and its file(s)."""
        task, parent = self.find(task_id)
        if task is None:
            raise TaskError(f"no task with id {task_id}. See: laaw.py <state.json> board")
        if parent is not None:
            StateMachine.require_replannable(task, parent, "removed")
        else:
            StateMachine.require_created(task, "removed")

        if not parent and task.is_super:
            self._persistence.remove_tree(task.file.rsplit("/", 1)[0])
        else:
            self._persistence.remove(task.file)

        if parent:
            parent.children.remove(task)
        else:
            self.roots.remove(task)
        return task

    # ---- consistency check

    def check(self, persistence: Persistence) -> tuple[list[str], list[str]]:
        """Return (problems, warnings) for state/file consistency."""
        problems: list[str] = []
        warnings: list[str] = []
        seen_root: set[str] = set()
        root_num = 0

        for root in self.roots:
            rid = root.id
            try:
                root_num = max(root_num, int(rid[1:]))
            except (ValueError, IndexError):
                problems.append(f"root id '{rid}' does not match t<N>.")
                continue

            if rid in seen_root:
                problems.append(f"duplicate root id {rid}.")
            seen_root.add(rid)

            self._check_entry(root, problems, persistence)
            for child in root.children:
                self._check_entry(child, problems, persistence)
                if not child.id.startswith(rid + "."):
                    problems.append(f"child id {child.id} is not under root {rid}.")

        if len(seen_root) != root_num:
            warnings.append(
                f"root ids are not contiguous 1..{root_num} "
                "(removed created tasks leave gaps — usually fine)."
            )

        # Check depends-on references
        ids = {t.id for t, _ in self.all_tasks()}
        for task, _ in self.all_tasks():
            for dep_id in task.depends:
                if dep_id not in ids:
                    problems.append(f"{task.id}: depends on unknown task '{dep_id}'.")
                elif dep_id == task.id:
                    problems.append(f"{task.id}: depends on itself.")

        # Context index consistency (warnings only — prose-maintained)
        index = persistence.load_context_index()
        if index is not None:
            listed: set[str] = set()
            for line in index.splitlines():
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if (
                    len(cells) == 2
                    and cells[0] not in ("file", "")
                    and not set(cells[0]) <= set("-: ")
                ):
                    listed.add(cells[0])
            on_disk = persistence.context_files()
            for f in sorted(on_disk - listed):
                warnings.append(f"context file {f} has no row in .ai/context/index.md.")
            for f in sorted(listed - on_disk):
                warnings.append(f"context index lists {f} but the file does not exist.")

        return problems, warnings

    def _check_entry(
        self,
        task: Task,
        problems: list[str],
        persistence: Persistence,
    ) -> None:
        tid, rel, status = task.id, task.file, task.status
        if status not in Task.STATUSES:
            problems.append(f"{tid}: unknown status '{status}'.")
        if not persistence.exists(rel):
            problems.append(f"{tid}: file {rel} listed in state.json does not exist.")
            return
        base = persistence.task_path(rel).name
        if not base.startswith(tid + "_") and base != "task.md":
            problems.append(
                f"{tid}: file {rel} is not named by its id "
                f"(expected prefix '{tid}_' or 'task.md')."
            )

    def attach_persistence(self, persistence: Persistence) -> None:
        """Attach persistence layer for file operations."""
        self._persistence = persistence


# ---------------------------------------------------------------------------
# LAAWCLI — CLI entry point
# ---------------------------------------------------------------------------

class LAAWCLI:
    """CLI command dispatcher.

    For 'init': no state.json needed — discovers root from cwd.
    For all other commands: requires state.json path.
    """

    CONTEXT_INDEX_SEED = "# Context index\n\n| file | summary |\n|---|---|\n"

    def __init__(self, state_path: Path | None, cmd: str):
        if cmd == "init":
            # init has no state.json yet — discover from cwd
            self.persistence = Persistence(Path.cwd() / ".ai" / "tasks" / "state.json")
            self.state = State([])
        else:
            self.persistence = Persistence(state_path)
            self.state = State.load(self.persistence)
            self.state.attach_persistence(self.persistence)

    # ---- commands

    def cmd_init(self, args: argparse.Namespace) -> None:
        if self.persistence.state_path.exists():
            raise TaskError(
                f"already initialized — {self.persistence.state_path} exists. "
                "Not touching it."
            )
        self.state.save(self.persistence)
        self.persistence.write(".gitignore", "*\n")
        if self.persistence.load_context_index() is None:
            self.persistence.save_context_index(self.CONTEXT_INDEX_SEED)
        print(
            f"Initialized {self.persistence.tasks_dir} (state.json) and "
            f"{self.persistence.context_dir} (index.md)."
        )

    def cmd_new(self, args: argparse.Namespace) -> None:
        depends = list(args.depends) if args.depends else None
        task, rel = self.state.add_root(
            args.name,
            description=args.desc,
            is_super=args.super,
            depends=depends,
        )
        self.state.save(self.persistence)
        print(f"Created {task.id} ({rel}) as created.")
        if task.depends:
            print(f"Depends on: {', '.join(task.depends)}")
        if args.super:
            print(
                f"Next: add children with: "
                f"laaw.py <state.json> subtask {task.id} <child name>, "
                f"then draft the task file (draft).")
        else:
            print(
                "Next: draft the task file (draft), fill sections, "
                "and ask plan approval (plan-task)."
            )

    def cmd_subtask(self, args: argparse.Namespace) -> None:
        depends = list(args.depends) if args.depends else None
        task, rel = self.state.add_subtask(
            args.root_id,
            args.name,
            description=args.desc,
            depends=depends,
        )
        self.state.save(self.persistence)
        print(f"Created {task.id} ({rel}) as created under {args.root_id}.")
        if task.depends:
            print(f"Depends on: {', '.join(task.depends)}")
        print(
            "Next: draft the task file (draft), fill sections, "
            "and add a line to the parent's Subtasks list (plan-task)."
        )

    def cmd_draft(self, args: argparse.Namespace) -> None:
        task, prev = self.state.draft_task(args.id)
        self.state.save(self.persistence)
        print(f"Drafted {task.id} ({task.file}) as planning.")
        print(
            f"Next: fill the task file sections (Context, Steps/Validations, "
            f"Context updates), then approve the plan (plan-task)."
        )

    def cmd_rename(self, args: argparse.Namespace) -> None:
        task = self.state.rename(args.id, args.new_name)
        self.state.save(self.persistence)
        print(f"Renamed {task.id} to '{task.name}' ({task.file}).")

    def cmd_remove(self, args: argparse.Namespace) -> None:
        task = self.state.remove(args.id)
        self.state.save(self.persistence)
        print(f"Removed {task.id} and its file(s).")

    def cmd_set_status(self, args: argparse.Namespace) -> None:
        prev = self.state.set_status(args.id, args.status)
        self.state.save(self.persistence)
        task, parent = self.state.find(args.id)
        print(f"OK: {task.id} {prev} → {args.status}.")
        statuses = self.state.status_map()
        guidance = NextOutput.get_guidance(task, parent, statuses)
        if guidance:
            print(f"Next: {guidance}")

    def cmd_depends(self, args: argparse.Namespace) -> None:
        # Support both --depends and positional dep_ids
        dep_ids = args.dep_ids or []
        if args.depends is not None:
            dep_ids = args.depends
        if not dep_ids and not args.clear:
            raise TaskError("give one or more dep ids, or --clear.")
        task = self.state.set_depends(
            args.id,
            [] if args.clear else dep_ids,
            clear=args.clear,
        )
        self.state.save(self.persistence)
        if task.depends:
            print(f"OK: {task.id} now depends on {', '.join(task.depends)}.")
        else:
            print(f"OK: {task.id} has no depends-on.")

    def cmd_status(self, args: argparse.Namespace) -> None:
        task_id = getattr(args, "id", None)
        if task_id:
            task, parent = self.state.find(task_id)
            if task is None:
                raise TaskError(
                    f"no task with id {task_id}. See: laaw.py <state.json> board"
                )
            kind = "child of " + parent.id if parent else "root"
            line = (
                f"{task.id} | {task.name} | {task.status} | {kind} | "
                f"file: {task.file}"
            )
            if task.depends:
                line += f" | depends: {', '.join(task.depends)}"
            print(line)
            return
        print(BoardRenderer.render(self.state.roots))

    def cmd_board(self, args: argparse.Namespace) -> None:
        print(BoardRenderer.render(self.state.roots))

    def cmd_next(self, args: argparse.Namespace) -> None:
        print(NextOutput.get_output(self.state.roots))

    def cmd_check(self, args: argparse.Namespace) -> None:
        problems, warnings = self.state.check(self.persistence)
        for w in warnings:
            print(f"warning: {w}")
        if problems:
            for p in problems:
                print(f"PROBLEM: {p}", file=sys.stderr)
            raise TaskError(
                f"check found {len(problems)} problem(s). Fix via laaw.py commands — "
                "never by hand-editing state.json."
            )
        print("check: state and files are consistent.")

    # ---- dispatch

    COMMANDS = {
        "init": "cmd_init",
        "new": "cmd_new",
        "draft": "cmd_draft",
        "subtask": "cmd_subtask",
        "rename": "cmd_rename",
        "remove": "cmd_remove",
        "set-status": "cmd_set_status",
        "depends": "cmd_depends",
        "status": "cmd_status",
        "board": "cmd_board",
        "next": "cmd_next",
        "check": "cmd_check",
    }

    def run(self, args: argparse.Namespace) -> None:
        method_name = self.COMMANDS[args.cmd]
        method = getattr(self, method_name)
        method(args)

    # ---- parser

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        ap = argparse.ArgumentParser(
            description="LAAW tasks CLI — single writer of state.json.",
        )
        ap.add_argument(
            "state_file",
            nargs="?",
            default=None,
            help="path to .ai/tasks/state.json (required except for 'init')",
        )
        sub = ap.add_subparsers(dest="cmd", required=True)

        # init
        sub.add_parser("init", help="create .ai/tasks/ and .ai/context/ scaffolding")

        # new
        p = sub.add_parser("new", help="register a root task (status=created, no file yet)")
        p.add_argument("name")
        p.add_argument("--super", action="store_true",
                       help="super-task (folder + task.md, gets subtasks)")
        p.add_argument("--desc", default=None, help="fill the Description line")
        p.add_argument("--depends", nargs="*", default=None,
                       help="task ids this task depends on")

        # draft
        p = sub.add_parser("draft", help="write task file template, flip to planning")
        p.add_argument("id")

        # subtask
        p = sub.add_parser("subtask", help="register a child of a super-task (status=created)")
        p.add_argument("root_id")
        p.add_argument("name")
        p.add_argument("--desc", default=None)
        p.add_argument("--depends", nargs="*", default=None,
                       help="task ids this task depends on")

        # rename
        p = sub.add_parser("rename", help="rename a created/planning task and its file(s)")
        p.add_argument("id")
        p.add_argument("new_name")

        # remove
        p = sub.add_parser("remove", help="delete a created/planning task and its file(s)")
        p.add_argument("id")

        # set-status
        p = sub.add_parser(
            "set-status",
            help="flip a status (validated against workflow.md §2)",
        )
        p.add_argument("id")
        p.add_argument("status", choices=Task.STATUSES)

        # depends
        p = sub.add_parser(
            "depends",
            help="set a task's depends-on list (created/planning tasks only)",
        )
        p.add_argument("id")
        p.add_argument("dep_ids", nargs="*", help="task ids this task depends on")
        p.add_argument("--clear", action="store_true",
                       help="remove all depends-on entries")
        p.add_argument("--depends", nargs="*", default=None,
                       help="alias for dep_ids")

        # status
        p = sub.add_parser("status", help="one task's status line, or the board")
        p.add_argument("id", nargs="?")

        # board
        sub.add_parser("board", help="the whole board as a markdown table")

        # next
        sub.add_parser(
            "next",
            help="active task + exact next action/question",
        )

        # check
        sub.add_parser(
            "check",
            help="state/file consistency report",
        )

        return ap


# ---------------------------------------------------------------------------
# main() — the only module-level entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = LAAWCLI.build_parser()
    args = parser.parse_args(argv)

    try:
        # 'init' has no state.json yet — all other commands require it
        if args.cmd == "init":
            cli = LAAWCLI(state_path=None, cmd=args.cmd)
        else:
            if not args.state_file:
                print(
                    "laaw: state.json path is required. "
                    "Usage: laaw.py <state.json> <command>",
                    file=sys.stderr,
                )
                return 1
            cli = LAAWCLI(
                state_path=Path(args.state_file),
                cmd=args.cmd,
            )
        cli.run(args)
    except TaskError as e:
        print(f"laaw: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"laaw: file system error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
