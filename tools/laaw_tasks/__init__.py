"""laaw_tasks — the LAAW tasks CLI implementation.

Layered so persistence, business logic, and presentation never tangle:

  cli.py          CLI: argument parsing, root discovery, command wiring
  state.py        State + Task: the state.json document model + the §2 status machine
  scaffold.py     Slugifier + TaskTemplate: pure content generation (slugs, task-file templates)
  report.py       BoardRenderer + NextOutput + NextGuidance: pure rendering (board, next)
  persistence.py  Store: the ONLY module that reads/writes files
  errors.py       TaskError

Dependency rule: persistence knows nothing about tasks; state/scaffold/report
know nothing about the disk except through an injected Store; cli wires the
rest. That is what lets tools/tests/ exercise the whole machine in memory.

Public API
----------
- State, Task, STATUSES, DONE, TRANSITIONS, apply_status, legal_targets, require_draft (from state.py)
- Store (from persistence.py)
- CLI (from cli.py)
- Slugifier, TaskTemplate (from scaffold.py)
- BoardRenderer, NextOutput, NextGuidance (from report.py)
- TaskError (from errors.py)
"""

from .state import (
    State,
    Task,
    STATUSES,
    DONE,
    TRANSITIONS,
    apply_status,
    legal_targets,
    require_draft,
)
from .persistence import Store
from .scaffold import Slugifier, TaskTemplate
from .report import BoardRenderer, NextOutput, NextGuidance
from .errors import TaskError
from .cli import CLI

__all__ = [
    "State",
    "Task",
    "STATUSES",
    "DONE",
    "TRANSITIONS",
    "apply_status",
    "legal_targets",
    "require_draft",
    "Store",
    "CLI",
    "Slugifier",
    "TaskTemplate",
    "BoardRenderer",
    "NextOutput",
    "NextGuidance",
    "TaskError",
]
