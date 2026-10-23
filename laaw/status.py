"""Status and Action enums for the LAAW task state machine.

Transition legality lives in can_transition; this module only names the states
and actions so every other module imports one shared vocabulary.
"""

from enum import Enum


class Status(Enum):
    NOT_PLANNED = "not-planned"
    PLANNING = "planning"
    IN_PROGRESS = "in-progress"
    PROPAGATING_CONTEXT = "propagating-context"
    CANCELLED = "cancelled"
    DONE = "done"

    @property
    def terminal(self) -> bool:
        return self in (Status.DONE, Status.CANCELLED)


class Action(Enum):
    REGISTER = "register"
    PLAN = "plan"
    IMPLEMENT = "implement"
    PROPAGATE = "propagate"
    DONE = "done"
    CANCEL = "cancel"
