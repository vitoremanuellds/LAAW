"""Tests for laaw.status transition table (table-driven)."""

import unittest

from laaw.domain.status import Action, Status, can_transition, resulting_status


# Every (current, action) -> expected legality, per the spec. None = no current status.
LEGAL_CASES = [
    (None, Action.REGISTER, True),
    (Status.NOT_PLANNED, Action.PLAN, True),
    (Status.IN_PROGRESS, Action.PLAN, True),          # re-plan
    (Status.PROPAGATING_CONTEXT, Action.PLAN, True),  # re-plan
    (Status.PLANNING, Action.IMPLEMENT, True),
    (Status.PROPAGATING_CONTEXT, Action.IMPLEMENT, True),  # resume
    (Status.IN_PROGRESS, Action.PROPAGATE, True),
    (Status.PROPAGATING_CONTEXT, Action.DONE, True),
    (Status.NOT_PLANNED, Action.CANCEL, True),
    (Status.PLANNING, Action.CANCEL, True),
    (Status.IN_PROGRESS, Action.CANCEL, True),
    (Status.PROPAGATING_CONTEXT, Action.CANCEL, True),
]

ILLEGAL_CASES = [
    (None, Action.PLAN, False),
    (None, Action.IMPLEMENT, False),
    (None, Action.PROPAGATE, False),
    (None, Action.DONE, False),
    (None, Action.CANCEL, False),
    (Status.NOT_PLANNED, Action.REGISTER, False),
    (Status.PLANNING, Action.REGISTER, False),
    (Status.NOT_PLANNED, Action.IMPLEMENT, False),
    (Status.NOT_PLANNED, Action.PROPAGATE, False),
    (Status.NOT_PLANNED, Action.DONE, False),
    (Status.PLANNING, Action.PROPAGATE, False),
    (Status.PLANNING, Action.DONE, False),
    (Status.IN_PROGRESS, Action.REGISTER, False),
    (Status.IN_PROGRESS, Action.DONE, False),
    (Status.PROPAGATING_CONTEXT, Action.REGISTER, False),
    (Status.DONE, Action.PLAN, False),        # terminal wall
    (Status.DONE, Action.IMPLEMENT, False),
    (Status.DONE, Action.PROPAGATE, False),
    (Status.DONE, Action.DONE, False),
    (Status.DONE, Action.CANCEL, False),
    (Status.CANCELLED, Action.PLAN, False),   # terminal wall
    (Status.CANCELLED, Action.IMPLEMENT, False),
    (Status.CANCELLED, Action.PROPAGATE, False),
    (Status.CANCELLED, Action.DONE, False),
    (Status.CANCELLED, Action.CANCEL, False),
]

EXPECTED_RESULT = {
    (None, Action.REGISTER): Status.NOT_PLANNED,
    (Status.NOT_PLANNED, Action.PLAN): Status.PLANNING,
    (Status.IN_PROGRESS, Action.PLAN): Status.PLANNING,
    (Status.PROPAGATING_CONTEXT, Action.PLAN): Status.PLANNING,
    (Status.PLANNING, Action.IMPLEMENT): Status.IN_PROGRESS,
    (Status.PROPAGATING_CONTEXT, Action.IMPLEMENT): Status.IN_PROGRESS,
    (Status.IN_PROGRESS, Action.PROPAGATE): Status.PROPAGATING_CONTEXT,
    (Status.PROPAGATING_CONTEXT, Action.DONE): Status.DONE,
    (Status.NOT_PLANNED, Action.CANCEL): Status.CANCELLED,
    (Status.PLANNING, Action.CANCEL): Status.CANCELLED,
    (Status.IN_PROGRESS, Action.CANCEL): Status.CANCELLED,
    (Status.PROPAGATING_CONTEXT, Action.CANCEL): Status.CANCELLED,
}


class CanTransitionTest(unittest.TestCase):
    def test_given_legal_pairs_when_can_transition_then_true(self):
        # arrange / act / assert (table-driven)
        for current, action, expected in LEGAL_CASES:
            with self.subTest(current=current, action=action):
                self.assertEqual(can_transition(current, action), expected)

    def test_given_illegal_pairs_when_can_transition_then_false(self):
        # arrange / act / assert (table-driven)
        for current, action, expected in ILLEGAL_CASES:
            with self.subTest(current=current, action=action):
                self.assertEqual(can_transition(current, action), expected)

    def test_given_terminal_statuses_when_any_action_then_rejected(self):
        # arrange
        terminals = [Status.DONE, Status.CANCELLED]
        actions = list(Action)
        # act / assert
        for status in terminals:
            for action in actions:
                with self.subTest(status=status, action=action):
                    self.assertFalse(can_transition(status, action))


class ResultingStatusTest(unittest.TestCase):
    def test_given_legal_move_when_resulting_status_then_returns_new_status(self):
        # arrange / act / assert (table-driven)
        for (current, action), expected in EXPECTED_RESULT.items():
            with self.subTest(current=current, action=action):
                self.assertIs(resulting_status(current, action), expected)

    def test_given_illegal_move_when_resulting_status_then_raises_value_error(self):
        # arrange
        current, action = Status.DONE, Action.PLAN
        # act / assert
        with self.assertRaises(ValueError):
            resulting_status(current, action)


if __name__ == "__main__":
    unittest.main()
