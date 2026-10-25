"""Tests for laaw.model.state (ProjectState and helpers)."""

import unittest

from laaw.model.state import ProjectState, format_number, kebab
from laaw.model.task import Task
from laaw.domain.status import Status


class FormatNumberTest(unittest.TestCase):
    def test_given_small_number_when_format_then_zero_padded_to_two(self):
        # arrange / act
        result = format_number(1)
        # assert
        self.assertEqual(result, "t01")

    def test_given_number_over_99_when_format_then_widens_without_padding(self):
        # arrange / act
        result = format_number(100)
        # assert
        self.assertEqual(result, "t100")


class KebabTest(unittest.TestCase):
    def test_given_name_with_spaces_when_kebab_then_hyphenated_lowercase(self):
        # arrange / act
        result = kebab("Add Login Flow")
        # assert
        self.assertEqual(result, "add-login-flow")

    def test_given_name_with_punctuation_when_kebab_then_collapses_separators(self):
        # arrange / act
        result = kebab("JWT  service!!")
        # assert
        self.assertEqual(result, "jwt-service")


class ProjectStateIdTest(unittest.TestCase):
    def test_given_empty_state_when_next_top_level_id_then_t01(self):
        # arrange
        state = ProjectState()
        # act
        result = state.next_top_level_id()
        # assert
        self.assertEqual(result, "t01")

    def test_given_existing_tasks_when_next_top_level_id_then_max_plus_one(self):
        # arrange
        state = ProjectState(tasks=[
            Task(id="t01", name="a", desc="", type="simple", status=Status.DONE),
            Task(id="t03", name="c", desc="", type="simple", status=Status.DONE),
        ])
        # act
        result = state.next_top_level_id()
        # assert
        self.assertEqual(result, "t04")

    def test_given_supertask_with_subtasks_when_next_subtask_id_then_parent_dot_n(self):
        # arrange
        from laaw.model.subtask import Subtask
        state = ProjectState(tasks=[
            Task(id="t07", name="auth", desc="", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t07.1", name="a", desc="", status=Status.DONE)]),
        ])
        # act
        result = state.next_subtask_id("t07")
        # assert
        self.assertEqual(result, "t07.2")


class ProjectStateSlugTest(unittest.TestCase):
    def test_given_name_when_slug_then_kebab(self):
        # arrange
        state = ProjectState()
        # act
        result = state.slug("Add Auth", taken=set())
        # assert
        self.assertEqual(result, "add-auth")

    def test_given_taken_base_when_slug_then_auto_suffix(self):
        # arrange
        state = ProjectState()
        # act
        result = state.slug("Add Auth", taken={"add-auth"})
        # assert
        self.assertEqual(result, "add-auth-2")

    def test_given_two_taken_when_slug_then_suffix_three(self):
        # arrange
        state = ProjectState()
        # act
        result = state.slug("Add Auth", taken={"add-auth", "add-auth-2"})
        # assert
        self.assertEqual(result, "add-auth-3")


class ProjectStateFindAnyTest(unittest.TestCase):
    def test_given_top_level_id_when_find_any_then_resolves_top(self):
        # arrange
        task = Task(id="t01", name="a", desc="", type="simple", status=Status.DONE)
        state = ProjectState(tasks=[task])
        # act
        result = state.find_any("t01")
        # assert
        self.assertEqual(result.kind, "top")
        self.assertIsNone(result.parent_id)
        self.assertEqual(result.id, "t01")
        self.assertEqual(result.name, "a")
        self.assertEqual(result.status, Status.DONE)

    def test_given_subtask_id_when_find_any_then_resolves_sub_with_parent(self):
        # arrange
        from laaw.model.subtask import Subtask
        state = ProjectState(tasks=[
            Task(id="t07", name="auth", desc="", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t07.1", name="a", desc="", status=Status.NOT_PLANNED)]),
        ])
        # act
        result = state.find_any("t07.1")
        # assert
        self.assertEqual(result.kind, "sub")
        self.assertEqual(result.parent_id, "t07")
        self.assertEqual(result.id, "t07.1")
        self.assertEqual(result.name, "a")
        self.assertEqual(result.status, Status.NOT_PLANNED)

    def test_given_missing_id_when_find_any_then_raises_key_error(self):
        # arrange
        state = ProjectState()
        # act / assert
        with self.assertRaises(KeyError):
            state.find_any("t99")


class ProjectStateLookupTest(unittest.TestCase):
    def test_given_task_when_find_then_returns_it(self):
        # arrange
        task = Task(id="t01", name="a", desc="", type="simple", status=Status.DONE)
        state = ProjectState(tasks=[task])
        # act
        result = state.find_task("t01")
        # assert
        self.assertIs(result, task)

    def test_given_missing_id_when_find_then_raises_key_error(self):
        # arrange
        state = ProjectState()
        # act / assert
        with self.assertRaises(KeyError):
            state.find_task("t99")

    def test_given_duplicate_add_when_add_task_then_raises_value_error(self):
        # arrange
        task = Task(id="t01", name="a", desc="", type="simple", status=Status.DONE)
        state = ProjectState(tasks=[task])
        # act / assert
        with self.assertRaises(ValueError):
            state.add_task(task)


class ProjectStateSerializeTest(unittest.TestCase):
    def test_given_state_when_to_dict_then_from_dict_round_trips(self):
        # arrange
        from laaw.model.subtask import Subtask
        state = ProjectState(tasks=[
            Task(id="t07", name="auth", desc="d", type="supertask", status=Status.IN_PROGRESS,
                 subtasks=[Subtask(id="t07.1", name="a", desc="", status=Status.DONE)]),
        ])
        # act
        restored = ProjectState.from_dict(state.to_dict())
        # assert
        self.assertEqual(restored, state)


if __name__ == "__main__":
    unittest.main()
