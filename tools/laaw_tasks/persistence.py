"""Persistence layer: the only module in laaw_tasks that touches the disk.

Store is bound to a project root and exposes plain file primitives —
loading state.json, saving it atomically, reading/writing/moving/removing
task files, and a few helpers for the .ai/context/ directory. It does not
know about tasks, statuses, or workflow rules: all policy (validating the
state document, checking statuses, naming files) lives in the business
layers (state.py, scaffold.py), which reach the disk only through a Store.

Everything else in the package can therefore be tested with an in-memory
state dict, or against a temp-dir Store.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path

from .errors import TaskError


class Store:
    """File access for one project's .ai/ tree.

    Path layout lives here and only here — no other module builds .ai/
    paths. Task-file methods take paths relative to .ai/tasks/.
    """

    def __init__(self, root):
        self.root = Path(root)

    # ------------------------------------------------------------ paths

    @property
    def tasks_dir(self):
        return self.root / ".ai" / "tasks"

    @property
    def state_path(self):
        return self.tasks_dir / "state.json"

    @property
    def context_dir(self):
        return self.root / ".ai" / "context"

    def task_path(self, rel):
        return self.tasks_dir / rel

    # ------------------------------------------------------------ state.json

    def load_state(self):
        """Read state.json and return the raw parsed JSON.

        Raises TaskError if the file is missing or not valid JSON. Shape
        validation (is this a LAAW state?) is the business layer's job —
        see state.State.
        """
        p = self.state_path
        if not p.exists():
            raise TaskError(
                f"no state file at {p} — project not bootstrapped. "
                'Run the route skill with "bootstrap" (it runs: tasks.py init).'
            )
        try:
            return json.loads(p.read_text())
        except json.JSONDecodeError as e:
            raise TaskError(
                f"state file {p} is corrupt ({e}). Do not hand-edit state.json; "
                "report to the human instead of guessing."
            ) from e

    def save_state(self, data):
        """Atomically write data to state.json (temp file in the same dir, then rename)."""
        td = self.tasks_dir
        td.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(td), prefix=".state-")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
            os.replace(tmp, self.state_path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    # ------------------------------------------------------------ task files

    def exists(self, rel):
        return self.task_path(rel).exists()

    def read(self, rel):
        p = self.task_path(rel)
        try:
            return p.read_text()
        except FileNotFoundError:
            raise TaskError(f"task file {p} does not exist — state/file mismatch; run tasks.py check.") from None

    def write(self, rel, content):
        """Write content to the task file rel, creating parent dirs. Unconditional."""
        p = self.task_path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return p

    def remove(self, rel):
        p = self.task_path(rel)
        try:
            p.unlink()
        except FileNotFoundError:
            raise TaskError(f"task file {p} does not exist (already deleted?).") from None

    def remove_tree(self, rel):
        p = self.task_path(rel)
        try:
            shutil.rmtree(p)
        except (FileNotFoundError, OSError):
            raise TaskError(f"{p} does not exist or could not be removed.") from None

    def move(self, src_rel, dst_rel):
        """Rename a task file or a super-task folder."""
        src, dst = self.task_path(src_rel), self.task_path(dst_rel)
        try:
            os.rename(src, dst)
        except FileNotFoundError:
            raise TaskError(f"{src} does not exist — cannot move it to {dst}.") from None

    # ------------------------------------------------------------ .ai/context/

    def context_index(self):
        """The .ai/context/index.md content, or None if it does not exist yet."""
        idx = self.context_dir / "index.md"
        if not idx.exists():
            return None
        return idx.read_text()

    def write_context_index(self, content):
        self.context_dir.mkdir(parents=True, exist_ok=True)
        (self.context_dir / "index.md").write_text(content)

    def context_files(self):
        """Names of the context files on disk (index.md itself excluded)."""
        if not self.context_dir.is_dir():
            return set()
        return {p.name for p in self.context_dir.iterdir() if p.is_file() and p.name != "index.md"}
