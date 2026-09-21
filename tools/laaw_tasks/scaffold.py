"""Pure content generation: slugs and task-file template rendering.

Nothing in this module writes files — deciding what goes into a task file
is business logic; the actual write is the persistence layer's job
(Store.write, called by the State lifecycle operations).
"""

import re
from pathlib import Path

from .errors import TaskError

# templates/ is a sibling of the tools/ directory that holds this package
# (repo root in this checkout, .ai/workflow/ in an installed project).
TEMPLATES = Path(__file__).resolve().parents[2] / "templates"

DESCRIPTION_DEFAULT = "<what this task is and why — one short paragraph>"


class Slugifier:
    """Generate URL-safe slugs from task names."""

    MAX_LENGTH = 30

    @classmethod
    def slugify(cls, name):
        s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(s) > cls.MAX_LENGTH:
            s = s[:cls.MAX_LENGTH].rsplit("-", 1)[0].rstrip("-")
        return s or "task"


class TaskTemplate:
    """Render task file templates from the templates/ directory."""

    TEMPLATES_DIR = TEMPLATES
    DESCRIPTION_DEFAULT = DESCRIPTION_DEFAULT

    def __init__(self, template_dir=None):
        self.template_dir = Path(template_dir) if template_dir else self.TEMPLATES_DIR

    def render(self, tid, name, desc=None, is_super=False):
        """Render the task template for task tid into a markdown string."""
        tmpl_name = "super-task-template.md" if is_super else "task-template.md"
        tmpl_path = self.template_dir / tmpl_name
        if not tmpl_path.exists():
            raise TaskError(f"missing template {tmpl_path}. Re-sync .ai/workflow/ (tools/sync-workflow.py).")
        body = tmpl_path.read_text().replace("t{N}", tid)
        body = body.replace("{name}", name)
        body = body.replace("{description}", desc if desc else self.DESCRIPTION_DEFAULT)
        return body

    def render_from_task(self, task):
        """Render a template from a Task object."""
        return self.render(task.id, task.name, task.description, task.is_super)
