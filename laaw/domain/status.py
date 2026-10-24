"""Status and Action enums plus the transition table for the LAAW task state machine."""

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


# Maps each action to {status it is legal from: status it results in}.
# None as a key means "no current status" (only register uses it).
TRANSITIONS: dict[Action, dict[Status | None, Status]] = {
    Action.REGISTER: {None: Status.NOT_PLANNED},
    Action.PLAN: {
        Status.NOT_PLANNED: Status.PLANNING,
        Status.IN_PROGRESS: Status.PLANNING,
        Status.PROPAGATING_CONTEXT: Status.PLANNING,
    },
    Action.IMPLEMENT: {
        Status.PLANNING: Status.IN_PROGRESS,
        Status.PROPAGATING_CONTEXT: Status.IN_PROGRESS,
    },
    Action.PROPAGATE: {Status.IN_PROGRESS: Status.PROPAGATING_CONTEXT},
    Action.DONE: {Status.PROPAGATING_CONTEXT: Status.DONE},
    Action.CANCEL: {
        Status.NOT_PLANNED: Status.CANCELLED,
        Status.PLANNING: Status.CANCELLED,
        Status.IN_PROGRESS: Status.CANCELLED,
        Status.PROPAGATING_CONTEXT: Status.CANCELLED,
    },
}


def can_transition(current: Status | None, action: Action) -> bool:
    return current in TRANSITIONS[action]


def resulting_status(current: Status | None, action: Action) -> Status:
    try:
        return TRANSITIONS[action][current]
    except KeyError:
        raise ValueError(f"illegal transition: {action.value} from {current}")
