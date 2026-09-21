"""The state.json document model and the status state machine.

This module never touches the disk directly: all file access goes through
the Store injected into State (see persistence.py).

- The pure functions (legal_targets, apply_status, require_draft) are
  workflow.md §2 rules over Task objects — exercised in memory by tests.
- The Task class is an attribute-based model with to_dict() for
  serialization. A super-task is recorded explicitly (is_super) so the
  "children" key survives a save/load round-trip even while empty.
- The State class wraps one state document: validation, lookup, id
  minting, status flips, and the draft-only lifecycle operations
  (add_root / add_subtask / rename / remove), whose file side-effects go
  through the store. Load with State.load(store), mutate in memory,
  persist with save().
"""

from .errors import TaskError
from . import scaffold

STATUSES = ("draft", "in-progress", "impl-review", "ctx-review", "done")
DONE = "done"


class Task:
    """Attribute-based task model. Copy a dict into attributes; call to_dict()
    to serialise back to the shape expected by state.json.
    """

    __slots__ = ("id", "name", "status", "file", "description", "children", "is_super")

    def __init__(self, id, name, status="draft", file=None, description=None, children=None, is_super=None):
        self.id = id
        self.name = name
        self.status = status
        self.file = file
        self.description = description
        self.children = children or []
        # A super-task has (or will get) subtasks. Recorded explicitly, not
        # inferred from children, so it survives a save/load round-trip while
        # the children list is still empty.
        self.is_super = bool(self.children) if is_super is None else is_super

    # ---- factory from a raw dict (deserialization)

    @classmethod
    def from_dict(cls, data):
        """Build a Task from a state.json entry dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            status=data["status"],
            file=data.get("file"),
            description=data.get("description"),
            children=[cls.from_dict(c) for c in data.get("children", [])],
            is_super="children" in data,
        )

    # ---- serialisation

    def to_dict(self):
        d = {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "file": self.file,
        }
        if self.description:
            d["description"] = self.description
        if self.is_super or self.children:
            d["children"] = [c.to_dict() for c in self.children]
        return d

    # ---- shape helpers

    @property
    def is_leaf(self):
        return not self.children

    @property
    def is_done(self):
        return self.status == DONE

    # ---- repr

    def __repr__(self):
        return f"Task(id={self.id!r}, name={self.name!r}, status={self.status!r})"

# (from, to) -> only writer skill. workflow.md §2 is the source of truth;
# tools/tests/ keeps this table in sync with it.
# Note: this table is the single enforcement source — apply_status validates
# against it, shape-aware via legal_targets (super-tasks never reach
# impl-review; subtasks never reach ctx-review or root done).
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


# ---------------------------------------------------------------- pure rules
# All three operate on Task objects (parent is a Task or None).


def legal_targets(task, is_root):
    """Statuses task may legally move to right now (shape-aware subset of §2).

    Derived from TRANSITIONS, so the §2 table is the single enforcement
    source. Shape rules on top of the table:
      - subtasks (have a parent): impl-review → done, never ctx-review/root done
      - root tasks with Steps: impl-review → ctx-review → done, never
        impl-review → done (that row in §2 is "subtasks only")
      - super-tasks: in-progress → ctx-review only, and only
        once at least one subtask exists and every subtask is done (§2 trigger);
        never impl-review
    """
    cur = task.status
    allowed = {to for (frm, to) in TRANSITIONS if frm == cur}
    if not is_root:
        allowed.discard("ctx-review")  # subtasks have no context gate
    if is_root and cur == "impl-review":
        allowed.discard("done")  # root tasks must pass through the context gate
    if task.is_super and cur == "in-progress":
        # Super-task: no impl-review gate of its own — straight to the
        # context gate, and only once at least one subtask exists and
        # every subtask is done (§2 trigger).
        allowed = set()
        if task.children and all(c.status == DONE for c in task.children):
            allowed.add("ctx-review")
    return allowed


def apply_status(task, parent, status):
    """Validate and apply a status change to task. Returns the previous status.

    Raises TaskError for unknown statuses, done tasks, and any transition
    not in TRANSITIONS (shape-checked via legal_targets).
    """
    if status not in STATUSES:
        raise TaskError(f"unknown status '{status}'. Known statuses: {', '.join(STATUSES)} (workflow.md §2).")
    cur = task.status
    if cur == DONE:
        raise TaskError(
            f"{task.id} is done — a done task never changes status again. "
            "If the work was wrong, plan a new task (plan-task)."
        )
    allowed = legal_targets(task, parent is None)
    if status not in allowed:
        extra = ""
        if cur == "in-progress" and task.is_super:
            extra = (
                " (no subtasks exist yet — plan-task must add them before the context gate; workflow.md §2)"
                if not task.children
                else " (all subtasks must be done before ctx-review — workflow.md §2)"
            )
        raise TaskError(
            f"illegal transition {cur} → {status} for {task.id}. "
            f"Allowed from {cur}: {', '.join(sorted(allowed)) or 'none'}{extra}. "
            "See workflow.md §2 — report any mismatch instead of forcing a status."
        )
    task.status = status
    return cur


def require_draft(task, verb):
    """Refuse a shape change unless task (and every child of it) is still draft.

    verb is the base form ("rename"/"remove") — it is conjugated in the
    messages. workflow.md §4: a task's shape is fixed at plan time.
    """
    if task.status != "draft":
        raise TaskError(f"{task.id} is not draft (it is {task.status}) — only draft tasks may be {verb}ed on re-plan (workflow.md §4).")
    for c in task.children:
        if c.status != "draft":
            raise TaskError(f"child {c.id} is not draft (it is {c.status}) — cannot {verb} {task.id} (workflow.md §4).")


# ---------------------------------------------------------------- the model

class State:
    """In-memory model of one .ai/tasks/state.json.

    Build with State.load(store) for a real project, or State(store, data)
    over an existing dict (what the tests do). All mutations happen in
    memory; call save() to persist. The lifecycle operations below also
    touch the task files through the store, because "create/rename/remove a
    task" is one operation with a file side-effect.
    """

    def __init__(self, store, data):
        self.store = store
        self._roots = self._validate(data)

    @classmethod
    def load(cls, store):
        """Load and validate the project's state.json via the store."""
        return cls(store, store.load_state())

    def save(self):
        """Persist the current state to disk."""
        self.store.save_state(self.to_dict())

    def to_dict(self):
        """Serialise the internal Task objects back to the raw dict shape."""
        return {
            "roots": [root.to_dict() for root in self._roots],
        }

    @staticmethod
    def _validate(data):
        """Accept either the raw state.json dict or a list of root Task objects."""
        if isinstance(data, dict):
            if not isinstance(data.get("roots"), list):
                raise TaskError(
                    "state.json is not a valid LAAW state (expected {'roots': [...]}) — "
                    "do not hand-edit it; report to the human instead of guessing."
                )
            return [Task.from_dict(r) for r in data["roots"]]
        if isinstance(data, list) and all(isinstance(r, Task) for r in data):
            return list(data)
        raise TaskError(
            "state is not a valid LAAW state (expected {'roots': [...]} or a list of Task) — "
            "do not hand-edit it; report to the human instead of guessing."
        )

    # ------------------------------------------------------------ access

    @property
    def roots(self):
        """Root Task objects."""
        return list(self._roots)

    def find(self, tid):
        """(Task, parent_Task) for id tid, or (None, None)."""
        for root in self._roots:
            if root.id == tid:
                return root, None
            for child in root.children:
                if child.id == tid:
                    return child, root
        return None, None

    def all_tasks(self):
        """Yield (Task, parent_Task) for every root and child, in order."""
        for root in self._roots:
            yield root, None
            for child in root.children:
                yield child, root

    def next_root_id(self):
        nums = []
        for r in self._roots:
            try:
                nums.append(int(r.id[1:]))
            except ValueError:
                raise TaskError(
                    f"root id '{r.id}' does not match t<N> — state.json looks corrupt; run tasks.py check."
                ) from None
        return f"t{max(nums, default=0) + 1}"

    def next_child_id(self, root):
        try:
            k = max((int(c.id.rsplit(".", 1)[1]) for c in root.children), default=0)
        except ValueError:
            raise TaskError(
                f"a child id under {root.id} does not match t<N>.k — state.json looks corrupt; run tasks.py check."
            ) from None
        return f"{root.id}.{k + 1}"

    # ------------------------------------------------------------ statuses

    def set_status(self, tid, status):
        """Validate and apply a status change; returns the previous status."""
        task, parent = self.find(tid)
        if task is None:
            raise TaskError(f"no task with id {tid}. See: tasks.py board")
        return apply_status(task, parent, status)

    # ------------------------------------------------------------ lifecycle
    # draft-only; file side-effects go through the store

    def add_root(self, name, desc=None, is_super=False):
        """Scaffold a new root task file and register it. Returns (Task, rel)."""
        tid = self.next_root_id()
        slug = scaffold.Slugifier.slugify(name)
        rel = f"{tid}_{slug}/task.md" if is_super else f"{tid}_{slug}.md"
        self._scaffold_file(rel, tid, name, desc, is_super)
        task = Task(id=tid, name=name, status="draft", file=rel, description=desc, is_super=is_super)
        self._roots.append(task)
        return task, rel

    def add_subtask(self, root_id, name, desc=None):
        """Scaffold a new child of a super-task and register it. Returns (Task, rel)."""
        root, _ = self.find(root_id)
        if root is None:
            raise TaskError(f"no task with id {root_id}. See: tasks.py board")
        if not root.is_super:
            raise TaskError(f"{root_id} is not a super-task. Create one with: tasks.py new <name> --super")
        if root.status != "draft":
            raise TaskError(
                f"{root.id} left draft (it is {root.status}) — its shape is fixed; "
                "subtasks can only be added while it is draft (workflow.md §4)."
            )
        cid = self.next_child_id(root)
        folder = root.file.rsplit("/", 1)[0]
        rel = f"{folder}/{cid}_{scaffold.Slugifier.slugify(name)}.md"
        self._scaffold_file(rel, cid, name, desc, False)
        child = Task(id=cid, name=name, status="draft", file=rel, description=desc)
        root.children.append(child)
        return child, rel

    def _scaffold_file(self, rel, tid, name, desc, is_super):
        if self.store.exists(rel):
            raise TaskError(f"{self.store.task_path(rel)} already exists — refusing to overwrite.")
        self.store.write(rel, scaffold.TaskTemplate().render(tid, name, desc, is_super))

    def rename(self, tid, new_name):
        """Rename a draft task; its file (or folder) and header follow."""
        task, parent = self.find(tid)
        if task is None:
            raise TaskError(f"no task with id {tid}. See: tasks.py board")
        if parent is not None:
            require_draft(parent, "rename")  # parent + every sibling must still be draft
        else:
            require_draft(task, "rename")
        old_name = task.name
        new_slug = scaffold.Slugifier.slugify(new_name)
        if not parent and task.is_super:
            old_dir = task.file.rsplit("/", 1)[0]
            new_dir = f"{task.id}_{new_slug}"
            if self.store.exists(new_dir):
                raise TaskError(f"{self.store.task_path(new_dir)} already exists.")
            self.store.move(old_dir, new_dir)
            for child in task.children:
                child.file = child.file.replace(old_dir + "/", new_dir + "/", 1)
            task.file = f"{new_dir}/task.md"
            header_rel = task.file
        else:
            folder = f"{parent.file.rsplit('/', 1)[0]}/" if parent else ""
            new_rel = f"{folder}{task.id}_{new_slug}.md"
            if self.store.exists(new_rel):
                raise TaskError(f"{self.store.task_path(new_rel)} already exists.")
            self.store.move(task.file, new_rel)
            task.file = new_rel
            header_rel = new_rel
        body = self.store.read(header_rel).replace(f"# {task.id} — {old_name}", f"# {task.id} — {new_name}", 1)
        self.store.write(header_rel, body)
        task.name = new_name
        return task

    def remove(self, tid):
        """Remove a draft task and its file(s)."""
        task, parent = self.find(tid)
        if task is None:
            raise TaskError(f"no task with id {tid}. See: tasks.py board")
        if parent is not None:
            require_draft(parent, "remove")  # parent + every sibling must still be draft
        else:
            require_draft(task, "remove")
        if not parent and task.is_super:
            self.store.remove_tree(task.file.rsplit("/", 1)[0])
        else:
            self.store.remove(task.file)
        if parent:
            parent.children.remove(task)
        else:
            self._roots.remove(task)
        return task

    # ------------------------------------------------------------ consistency

    def check(self):
        """State/file consistency report. Returns (problems, warnings)."""
        problems = []
        warnings = []
        seen_root = set()
        root_num = 0
        for root in self._roots:
            rid = root.id
            try:
                root_num = max(root_num, int(rid[1:]))
            except (ValueError, IndexError):
                problems.append(f"root id '{rid}' does not match t<N>.")
                continue
            if rid in seen_root:
                problems.append(f"duplicate root id {rid}.")
            seen_root.add(rid)
            self._check_entry(root, problems)
            for child in root.children:
                self._check_entry(child, problems)
                if not child.id.startswith(rid + "."):
                    problems.append(f"child id {child.id} is not under root {rid}.")
        if len(seen_root) != root_num:
            warnings.append(f"root ids are not contiguous 1..{root_num} (removed drafts leave gaps — usually fine).")
        # context index (prose-maintained, so warnings only)
        index = self.store.context_index()
        if index is not None:
            listed = set()
            for line in index.splitlines():
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) == 2 and cells[0] not in ("file", "") and not set(cells[0]) <= set("-: "):
                    listed.add(cells[0])
            on_disk = self.store.context_files()
            for f in sorted(on_disk - listed):
                warnings.append(f"context file {f} has no row in .ai/context/index.md.")
            for f in sorted(listed - on_disk):
                warnings.append(f"context index lists {f} but the file does not exist.")
        return problems, warnings

    def _check_entry(self, task, problems):
        tid, rel, status = task.id, task.file, task.status
        if status not in STATUSES:
            problems.append(f"{tid}: unknown status '{status}'.")
        if not self.store.exists(rel):
            problems.append(f"{tid}: file {rel} listed in state.json does not exist.")
            return
        base = self.store.task_path(rel).name
        if not base.startswith(tid + "_") and base != "task.md":
            problems.append(f"{tid}: file {rel} is not named by its id (expected prefix '{tid}_' or 'task.md').")

