"""Tests for laaw.render (pure table rendering)."""

import unittest

from laaw import render
from laaw.constants import GENERATED_HEADER
from laaw.model.state import ProjectState
from laaw.model.subtask import Subtask
from laaw.model.task import Task
from laaw.status import Status


def simple_task(
    id: str = "t01",
    name: str = "Add login",
    desc: str = "Adds a login endpoint.",
    status: Status = Status.PLANNING,
    deps: list[str] | None = None,
) -> Task:
    return Task(id=id, name=name, desc=desc, type="simple", status=status, deps=deps or [])


def subtask(
    id: str = "t02.1",
    name: str = "JWT service",
    desc: str = "JWT issuing service.",
    status: Status = Status.DONE,
    deps: list[str] | None = None,
) -> Subtask:
    return Subtask(id=id, name=name, desc=desc, status=status, deps=deps or [])


class RenderTasksMdTest(unittest.TestCase):
    def test_given_empty_state_when_render_tasks_md_then_header_and_empty_table(self):
        # arrange
        state = ProjectState()
        # act
        out = render.render_tasks_md(state)
        # assert
        self.assertTrue(out.startswith(GENERATED_HEADER))
        self.assertIn("| ID | Status | Name | Description | Type | Dependencies |", out)
        self.assertNotIn("t01", out)

    def test_given_state_when_render_tasks_md_then_one_row_per_top_level_task(self):
        # arrange
        state = ProjectState(
            tasks=[
                simple_task("t01", "Add login", "Adds a login endpoint."),
                simple_task("t02", "Add auth", "Full authentication module.", deps=["t01"]),
            ]
        )
        # act
        out = render.render_tasks_md(state)
        # assert
        self.assertIn("| t01 | planning | Add login | Adds a login endpoint. | simple |  |", out)
        self.assertIn("| t02 | planning | Add auth | Full authentication module. | simple | t01 |", out)

    def test_given_supertask_when_render_tasks_md_then_subtask_rows_excluded(self):
        # arrange
        state = ProjectState(
            tasks=[
                Task(
                    id="t02",
                    name="Add auth",
                    desc="Full authentication module.",
                    type="supertask",
                    status=Status.IN_PROGRESS,
                    subtasks=[subtask()],
                )
            ]
        )
        # act
        out = render.render_tasks_md(state)
        # assert
        self.assertIn("| t02 | in-progress | Add auth | Full authentication module. | supertask |  |", out)
        self.assertNotIn("t02.1", out)

    def test_given_deps_when_render_tasks_md_then_comma_joined_dep_ids(self):
        # arrange
        state = ProjectState(tasks=[simple_task("t03", "Docs", "Update docs.", deps=["t01", "t02"])])
        # act
        out = render.render_tasks_md(state)
        # assert
        self.assertIn("| t03 | planning | Docs | Update docs. | simple | t01, t02 |", out)

    def test_given_same_state_when_render_twice_then_identical_output(self):
        # arrange
        state = ProjectState(
            tasks=[
                simple_task("t01", "Add login", "Adds a login endpoint."),
                Task(
                    id="t02",
                    name="Add auth",
                    desc="Full authentication module.",
                    type="supertask",
                    status=Status.IN_PROGRESS,
                    subtasks=[subtask()],
                ),
            ]
        )
        # act
        first = render.render_tasks_md(state)
        second = render.render_tasks_md(state)
        # assert
        self.assertEqual(first, second)


class RenderSubtasksMdTest(unittest.TestCase):
    def test_given_supertask_when_render_subtasks_md_then_one_row_per_subtask(self):
        # arrange
        task = Task(
            id="t02",
            name="Add auth",
            desc="Full authentication module.",
            type="supertask",
            status=Status.IN_PROGRESS,
            subtasks=[
                subtask("t02.1", "JWT service", "JWT issuing service."),
                subtask("t02.2", "User model", "User persistence model.", deps=["t02.1"]),
            ],
        )
        # act
        out = render.render_subtasks_md(task)
        # assert
        self.assertTrue(out.startswith(GENERATED_HEADER))
        self.assertIn("| t02.1 | done | JWT service | JWT issuing service. | subtask |  |", out)
        self.assertIn(
            "| t02.2 | done | User model | User persistence model. | subtask | t02.1 |",
            out,
        )

    def test_given_subtasks_when_render_twice_then_identical_output(self):
        # arrange
        task = Task(
            id="t02",
            name="Add auth",
            desc="Full authentication module.",
            type="supertask",
            status=Status.IN_PROGRESS,
            subtasks=[subtask("t02.1", "JWT service", "JWT issuing service.")],
        )
        # act
        first = render.render_subtasks_md(task)
        second = render.render_subtasks_md(task)
        # assert
        self.assertEqual(first, second)

    def test_given_supertask_without_subtasks_when_render_subtasks_md_then_empty_marker(self):
        # arrange
        task = Task(
            id="t02",
            name="Add auth",
            desc="Full authentication module.",
            type="supertask",
            status=Status.PLANNING,
        )
        # act
        out = render.render_subtasks_md(task)
        # assert
        self.assertTrue(out.startswith(GENERATED_HEADER))
        self.assertIn("(no subtasks)", out)
        self.assertNotIn("| ID |", out)


if __name__ == "__main__":
    unittest.main()
