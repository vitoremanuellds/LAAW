"""Tests for laaw.model.task."""

import unittest

from laaw.model.subtask import Subtask
from laaw.model.task import Task
from laaw.status import Status


class TaskTest(unittest.TestCase):
    def test_given_simple_task_when_to_dict_then_no_subtasks_key(self):
        # arrange
        task = Task(
            id="t08", name="Add login", desc="d", type="simple", status=Status.NOT_PLANNED
        )
        # act
        data = task.to_dict()
        # assert
        self.assertNotIn("subtasks", data)
        self.assertEqual(data["type"], "simple")

    def test_given_supertask_when_to_dict_then_includes_subtasks(self):
        # arrange
        sub = Subtask(id="t07.1", name="a", desc="", status=Status.DONE, deps=[])
        task = Task(
            id="t07", name="Add auth", desc="d", type="supertask",
            status=Status.IN_PROGRESS, deps=["t03"], subtasks=[sub],
        )
        # act
        data = task.to_dict()
        # assert
        self.assertEqual(data["subtasks"], [sub.to_dict()])

    def test_given_task_dict_when_from_dict_then_round_trips(self):
        # arrange
        sub = Subtask(id="t07.1", name="a", desc="", status=Status.PLANNING, deps=["t07.0"])
        task = Task(
            id="t07", name="Add auth", desc="d", type="supertask",
            status=Status.IN_PROGRESS, deps=[], subtasks=[sub],
        )
        # act
        restored = Task.from_dict(task.to_dict())
        # assert
        self.assertEqual(restored, task)

    def test_given_task_dict_without_desc_when_from_dict_then_desc_empty(self):
        # arrange
        data = {"id": "t08", "name": "x", "type": "simple", "status": "not-planned"}
        # act
        task = Task.from_dict(data)
        # assert
        self.assertEqual(task.desc, "")


if __name__ == "__main__":
    unittest.main()
