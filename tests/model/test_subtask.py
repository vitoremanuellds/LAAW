"""Tests for laaw.model.subtask."""

import unittest

from laaw.model.subtask import Subtask
from laaw.domain.status import Status


class SubtaskTest(unittest.TestCase):
    def test_given_subtask_dict_when_from_dict_then_fields_match(self):
        # arrange
        data = {
            "id": "t07.1",
            "name": "jwt-service",
            "desc": "Build the JWT service",
            "status": "planning",
            "deps": ["t07.0"],
        }
        # act
        sub = Subtask.from_dict(data)
        # assert
        self.assertEqual(sub.id, "t07.1")
        self.assertEqual(sub.name, "jwt-service")
        self.assertEqual(sub.desc, "Build the JWT service")
        self.assertIs(sub.status, Status.PLANNING)
        self.assertEqual(sub.deps, ["t07.0"])

    def test_given_subtask_when_to_dict_then_round_trips(self):
        # arrange
        sub = Subtask(
            id="t07.2",
            name="user-model",
            desc="Model the user",
            status=Status.IN_PROGRESS,
            deps=[],
        )
        # act
        restored = Subtask.from_dict(sub.to_dict())
        # assert
        self.assertEqual(restored, sub)

    def test_given_subtask_dict_without_deps_when_from_dict_then_deps_empty(self):
        # arrange
        data = {"id": "t07.1", "name": "x", "desc": "", "status": "done"}
        # act
        sub = Subtask.from_dict(data)
        # assert
        self.assertEqual(sub.deps, [])


if __name__ == "__main__":
    unittest.main()
