"""Tests for laaw.deps (pure, operates on a ProjectState)."""

import unittest

from laaw import deps
from laaw.model.state import ProjectState
from laaw.model.subtask import Subtask
from laaw.model.task import Task
from laaw.status import Status


def make_task(tid: str, status: Status = Status.DONE, dep: str | None = None,
              subtasks: list[Subtask] | None = None) -> Task:
    return Task(id=tid, name=tid, desc="", type="supertask" if subtasks else "simple",
                status=status, deps=[dep] if dep else [], subtasks=subtasks or [])


class CanDependTest(unittest.TestCase):
    def test_given_sibling_top_tasks_when_can_depend_then_true(self):
        # arrange
        state = ProjectState(tasks=[make_task("t01"), make_task("t02")])
        # act
        result = deps.can_depend(state, "t01", "t02")
        # assert
        self.assertTrue(result)

    def test_given_sibling_subtasks_when_can_depend_then_true(self):
        # arrange
        state = ProjectState(tasks=[make_task("t07", subtasks=[
            Subtask(id="t07.1", name="a", desc="", status=Status.DONE),
            Subtask(id="t07.2", name="b", desc="", status=Status.PLANNING),
        ])])
        # act
        result = deps.can_depend(state, "t07.1", "t07.2")
        # assert
        self.assertTrue(result)

    def test_given_cross_scope_when_can_depend_then_false(self):
        # arrange: top task t01 and subtask t07.1 are different scopes
        state = ProjectState(tasks=[
            make_task("t01"),
            make_task("t07", subtasks=[Subtask(id="t07.1", name="a", desc="", status=Status.DONE)]),
        ])
        # act
        result = deps.can_depend(state, "t01", "t07.1")
        # assert
        self.assertFalse(result)

    def test_given_subtasks_of_different_parents_when_can_depend_then_false(self):
        # arrange
        state = ProjectState(tasks=[
            make_task("t07", subtasks=[Subtask(id="t07.1", name="a", desc="", status=Status.DONE)]),
            make_task("t08", subtasks=[Subtask(id="t08.1", name="b", desc="", status=Status.DONE)]),
        ])
        # act
        result = deps.can_depend(state, "t07.1", "t08.1")
        # assert
        self.assertFalse(result)

    def test_given_same_id_when_can_depend_then_false(self):
        # arrange
        state = ProjectState(tasks=[make_task("t01")])
        # act
        result = deps.can_depend(state, "t01", "t01")
        # assert
        self.assertFalse(result)

    def test_given_missing_id_when_can_depend_then_false(self):
        # arrange
        state = ProjectState(tasks=[make_task("t01")])
        # act
        result = deps.can_depend(state, "t01", "t99")
        # assert
        self.assertFalse(result)


class CycleTest(unittest.TestCase):
    def test_given_dag_when_would_create_cycle_then_false(self):
        # arrange: t02 -> t01 (t02 depends on t01); adding t01 -> t03 is fine
        state = ProjectState(tasks=[make_task("t01"), make_task("t02", dep="t01"), make_task("t03")])
        # act
        result = deps.would_create_cycle(state, "t01", "t03")
        # assert
        self.assertFalse(result)

    def test_given_direct_back_edge_when_would_create_cycle_then_true(self):
        # arrange: t02 -> t01; adding t01 -> t02 closes a cycle
        state = ProjectState(tasks=[make_task("t01"), make_task("t02", dep="t01")])
        # act
        result = deps.would_create_cycle(state, "t01", "t02")
        # assert
        self.assertTrue(result)

    def test_given_transitive_back_edge_when_would_create_cycle_then_true(self):
        # arrange: t03 -> t02 -> t01; adding t01 -> t03 closes a transitive cycle
        state = ProjectState(tasks=[
            make_task("t01"),
            make_task("t02", dep="t01"),
            make_task("t03", dep="t02"),
        ])
        # act
        result = deps.would_create_cycle(state, "t01", "t03")
        # assert
        self.assertTrue(result)


class ImplementableTest(unittest.TestCase):
    def test_given_all_deps_done_when_is_implementable_then_true(self):
        # arrange
        state = ProjectState(tasks=[make_task("t01"), make_task("t02", dep="t01")])
        # act
        result = deps.is_implementable(state, "t02")
        # assert
        self.assertTrue(result)

    def test_given_unsatisfied_dep_when_is_implementable_then_false(self):
        # arrange: t01 not done
        state = ProjectState(tasks=[make_task("t01", status=Status.PLANNING), make_task("t02", dep="t01")])
        # act
        result = deps.is_implementable(state, "t02")
        # assert
        self.assertFalse(result)

    def test_given_no_deps_when_is_implementable_then_true(self):
        # arrange
        state = ProjectState(tasks=[make_task("t01")])
        # act
        result = deps.is_implementable(state, "t01")
        # assert
        self.assertTrue(result)

    def test_given_unsatisfied_dep_when_unsatisfied_deps_then_lists_it(self):
        # arrange
        state = ProjectState(tasks=[make_task("t01", status=Status.IN_PROGRESS), make_task("t02", dep="t01")])
        # act
        result = deps.unsatisfied_deps(state, "t02")
        # assert
        self.assertEqual(result, ["t01"])


class DependentsTest(unittest.TestCase):
    def test_given_task_with_dependents_when_dependents_then_lists_them(self):
        # arrange: t02 and t03 both depend on t01
        state = ProjectState(tasks=[
            make_task("t01"),
            make_task("t02", dep="t01"),
            make_task("t03", dep="t01"),
        ])
        # act
        result = deps.dependents(state, "t01")
        # assert
        self.assertEqual(result, ["t02", "t03"])

    def test_given_subtask_dependent_when_dependents_then_includes_it(self):
        # arrange: subtask t07.2 depends on top-level? No — subtasks only depend on siblings.
        # Use a subtask depending on its sibling, then query the sibling.
        state = ProjectState(tasks=[make_task("t07", subtasks=[
            Subtask(id="t07.1", name="a", desc="", status=Status.DONE),
            Subtask(id="t07.2", name="b", desc="", status=Status.PLANNING, deps=["t07.1"]),
        ])])
        # act
        result = deps.dependents(state, "t07.1")
        # assert
        self.assertEqual(result, ["t07.2"])

    def test_given_task_with_no_dependents_when_dependents_then_empty(self):
        # arrange
        state = ProjectState(tasks=[make_task("t01"), make_task("t02")])
        # act
        result = deps.dependents(state, "t01")
        # assert
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
