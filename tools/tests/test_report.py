"""Board / next rendering over in-memory Task objects, plus State.check()
(no CLI; a temp dir for check()'s file probes).
"""

import tempfile
import unittest
from pathlib import Path

from laaw_tasks.persistence import Store
from laaw_tasks.report import BoardRenderer, NextGuidance, NextOutput
from laaw_tasks.state import State, Task

DONE = "done"


def root(**over):
    t = Task(id="t1", name="Leaf", status="draft", file="t1_leaf.md")
    for k, v in over.items():
        setattr(t, k, v)
    return t


def child(**over):
    t = Task(id="t2.1", name="Child", status="draft", file="t2_super/t2.1_child.md")
    for k, v in over.items():
        setattr(t, k, v)
    return t


def super_task(children=None, **over):
    t = Task(id="t2", name="Super", status="in-progress", file="t2_super/task.md", is_super=True, children=children if children is not None else [child()])
    for k, v in over.items():
        setattr(t, k, v)
    return t


class TestNextOutput(unittest.TestCase):
    def show(self, *roots):
        return NextOutput().get_output(list(roots))

    def test_no_roots(self):
        out = self.show()
        self.assertIn("No active tasks", out)
        self.assertIn("plan-task", out)

    def test_draft_asks_plan_approval(self):
        out = self.show(root())
        self.assertIn('Ask the human: "Approve plan for t1?"', out)
        self.assertIn("t1_leaf.md", out)

    def test_in_progress_leaf(self):
        out = self.show(root(status="in-progress"))
        self.assertIn("Hand off to implement-task for t1", out)

    def test_in_progress_super_with_live_subtask(self):
        out = self.show(super_task())
        self.assertIn("Next subtask of t2: t2.1 — Child", out)

    def test_in_progress_super_all_done(self):
        out = self.show(super_task(children=[child(status=DONE)]))
        self.assertIn("All subtasks of t2 are done", out)
        self.assertIn("propagate-context", out)

    def test_in_progress_super_without_subtasks(self):
        out = self.show(super_task(children=[]))
        self.assertIn("no subtasks yet", out)
        self.assertIn("subtask t2", out)

    def test_impl_review_asks_impl_approval(self):
        out = self.show(root(status="impl-review"))
        self.assertIn('Ask the human: "Approve implementation of t1?"', out)

    def test_ctx_review_asks_context_approval(self):
        out = self.show(root(status="ctx-review"))
        self.assertIn('Ask the human: "Approve context changes for t1?"', out)

    def test_done_root_is_not_active(self):
        out = self.show(root(status=DONE))
        self.assertIn("No active tasks", out)

    def test_multiple_roots_lists_all(self):
        out = self.show(root(status="draft"), super_task())
        self.assertIn("Multiple active roots", out)
        self.assertIn("t1 — Leaf (draft)", out)
        self.assertIn("t2 — Super (in-progress)", out)


class TestNextGuidance(unittest.TestCase):
    def guidance(self, task, parent=None):
        return NextGuidance().get_guidance(task, parent)

    def test_child_points_to_impl_review(self):
        g = self.guidance(child(status="in-progress"), Task(id="t2", name="Super"))
        self.assertIn("t2.1", g)
        self.assertIn("impl-review", g)

    def test_done_child_points_to_next_subtask(self):
        done = child(id="t2.1", status=DONE)
        parent = Task(id="t2", name="Super", children=[done, child(id="t2.2")])
        g = self.guidance(done, parent)
        self.assertIn("t2.2", g)

    def test_last_done_child_points_to_propagate(self):
        """After the final subtask is done, the guidance must match `next`
        (context pass), not promise another subtask."""
        done = child(id="t2.1", status=DONE)
        parent = Task(id="t2", name="Super", children=[done, child(id="t2.2", status=DONE)])
        g = self.guidance(done, parent)
        self.assertNotIn("next subtask", g)
        self.assertIn("propagate-context", g)

    def test_done_root(self):
        g = self.guidance(root(status=DONE))
        self.assertEqual(g, "t1 is done.")

    def test_super_all_done_points_to_ctx_review(self):
        g = self.guidance(super_task(children=[child(status=DONE)]))
        self.assertIn("t2 ctx-review", g)

    def test_super_live_kept_in_progress(self):
        g = self.guidance(super_task())
        self.assertIn("stays in-progress", g)


class TestBoard(unittest.TestCase):
    def test_board_lists_all_rows(self):
        board = BoardRenderer().render([root(status="draft"), super_task()])
        self.assertIn("| id | name | status |", board)
        self.assertIn("| t1 | Leaf | draft |", board)
        self.assertIn("| t2 | Super | in-progress |", board)
        self.assertIn("| t2.1 | Child | draft |", board)


class TestCheck(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.store = Store(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def consistent_state(self):
        st = State(self.store, [root()])
        self.store.write("t1_leaf.md", "# t1 — Leaf\n")
        cd = self.root / ".ai" / "context"
        cd.mkdir(parents=True, exist_ok=True)
        (cd / "index.md").write_text("# Context index\n\n| file | summary |\n|---|---|\n")
        return st

    def test_consistent_state(self):
        problems, warnings = self.consistent_state().check()
        self.assertEqual(problems, [])
        self.assertEqual(warnings, [])

    def test_missing_file_is_a_problem(self):
        st = self.consistent_state()
        (self.root / ".ai" / "tasks" / "t1_leaf.md").unlink()
        problems, _ = st.check()
        self.assertTrue(any("t1_leaf.md" in p for p in problems))

    def test_bad_status_is_a_problem(self):
        st = self.consistent_state()
        st.roots[0].status = "shipped"
        problems, _ = st.check()
        self.assertTrue(any("unknown status" in p for p in problems))

    def test_child_id_must_be_under_root(self):
        st = self.consistent_state()
        st.roots[0].children.append(Task(id="t9.1", name="X", status="draft", file="t9_x.md"))
        problems, _ = st.check()
        self.assertTrue(any("not under root t1" in p for p in problems))

    def test_context_index_warnings(self):
        st = self.consistent_state()
        (self.root / ".ai" / "context" / "api.md").write_text("# api\n")
        problems, warnings = st.check()
        self.assertEqual(problems, [])
        self.assertTrue(any("api.md" in w and "no row" in w for w in warnings))
        # ghost row
        idx = self.root / ".ai" / "context" / "index.md"
        idx.write_text(idx.read_text() + "| ghost.md | missing |\n")
        _, warnings = st.check()
        self.assertTrue(any("ghost.md" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
