"""The status state machine.

1. state.TRANSITIONS matches the single-writer table in workflow.md §2
   (the two sources of truth must not drift).
2. Shape rules: super-tasks never reach impl-review; subtasks never reach
   ctx-review; super-task ctx-review requires all subtasks done; a done
   task never changes status. Exercised in memory over Task objects via
   laaw_tasks.state — no filesystem involved.
"""

import unittest
from pathlib import Path

import laaw_tasks.state as state
from laaw_tasks.errors import TaskError
from laaw_tasks.state import Task

WORKFLOW = Path(__file__).resolve().parents[2] / "workflow.md"


def parse_workflow_table():
    """(from, to, writer) triples from the §2 table in workflow.md."""
    text = WORKFLOW.read_text()
    sec = text.split("## 2.", 1)[1].split("## 3.", 1)[0]
    out = set()
    for line in sec.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4:
            continue
        if cells[0] == "From" or set(cells[0]) <= set("-: "):
            continue
        frm = cells[0].replace("`", "").strip()
        if frm == "—":
            frm = "none"
        to = cells[1].replace("`", "").strip()
        writer = cells[2].replace("`", "").strip()
        out.add((frm, to, writer))
    return out


class TestTransitionTable(unittest.TestCase):
    def test_matches_workflow_md(self):
        got = {(k[0], k[1], v) for k, v in state.TRANSITIONS.items()}
        want = parse_workflow_table()
        only_doc = sorted(want - got)
        only_cli = sorted(got - want)
        self.assertEqual(
            got,
            want,
            f"workflow.md §2 and state.TRANSITIONS disagree.\n"
            f"  only in workflow.md: {only_doc}\n  only in state.py:   {only_cli}",
        )

    def test_every_transition_name_a_real_status(self):
        for (frm, to), writer in state.TRANSITIONS.items():
            self.assertIn(to, state.STATUSES, f"{to!r} is not a known status")
            self.assertTrue(writer, "every transition names its writer skill")


def leaf(**over):
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
    t = Task(id="t2", name="Super", status="draft", file="t2_super/task.md", is_super=True, children=children)
    for k, v in over.items():
        setattr(t, k, v)
    return t


class TestStatusMachine(unittest.TestCase):
    def set(self, task, parent, status):
        return state.apply_status(task, parent, status)

    def test_leaf_full_path(self):
        t = leaf()
        self.assertEqual(self.set(t, None, "in-progress"), "draft")
        self.set(t, None, "impl-review")
        self.set(t, None, "ctx-review")
        self.set(t, None, "done")
        self.assertEqual(t.status, "done")

    def test_done_is_terminal(self):
        t = leaf(status="done")
        with self.assertRaises(TaskError) as ctx:
            self.set(t, None, "draft")
        self.assertIn("never changes status again", str(ctx.exception))

    def test_illegal_draft_to_impl_review(self):
        t = leaf()
        with self.assertRaises(TaskError) as ctx:
            self.set(t, None, "impl-review")
        self.assertIn("illegal transition draft → impl-review", str(ctx.exception))

    def test_root_leaf_cannot_skip_context_gate(self):
        """impl-review → done is "subtasks only" (workflow.md §2): a root task
        with Steps must pass through ctx-review first."""
        t = leaf(status="impl-review")
        with self.assertRaises(TaskError) as ctx:
            self.set(t, None, "done")
        self.assertIn("illegal transition impl-review → done", str(ctx.exception))
        self.assertEqual(t.status, "impl-review")
        # …but the context path is open:
        self.set(t, None, "ctx-review")
        self.set(t, None, "done")
        self.assertEqual(t.status, "done")

    def test_unknown_status(self):
        t = leaf()
        with self.assertRaises(TaskError) as ctx:
            self.set(t, None, "shipped")
        self.assertIn("unknown status", str(ctx.exception))

    # -- super-task shape ---------------------------------------------------

    def test_super_task_never_reaches_impl_review(self):
        t = super_task(status="in-progress", children=[child()])
        with self.assertRaises(TaskError) as ctx:
            self.set(t, None, "impl-review")
        self.assertIn("illegal transition in-progress → impl-review", str(ctx.exception))

    def test_super_task_ctx_review_requires_all_subtasks_done(self):
        t = super_task(status="in-progress", children=[child()])
        with self.assertRaises(TaskError) as ctx:
            self.set(t, None, "ctx-review")
        self.assertIn("all subtasks must be done", str(ctx.exception))
        t.children[0].status = "done"
        self.set(t, None, "ctx-review")
        self.set(t, None, "done")
        self.assertEqual(t.status, "done")

    def test_super_task_draft_path(self):
        t = super_task()
        self.set(t, None, "in-progress")
        self.assertEqual(t.status, "in-progress")

    def test_super_task_without_subtasks_cannot_reach_ctx_review(self):
        """"All subtasks done" is a vacuous truth for a childless super-task."""
        t = super_task(status="in-progress", children=[])
        with self.assertRaises(TaskError) as ctx:
            self.set(t, None, "ctx-review")
        self.assertIn("no subtasks exist yet", str(ctx.exception))
        self.assertEqual(t.status, "in-progress")


class TestSubtaskShape(unittest.TestCase):
    def set(self, task, parent, status):
        return state.apply_status(task, parent, status)

    def test_subtask_full_path(self):
        t = child()
        parent = Task(id="t2", name="Super", status="in-progress")
        self.set(t, parent, "in-progress")
        self.set(t, parent, "impl-review")
        self.set(t, parent, "done")
        self.assertEqual(t.status, "done")

    def test_subtask_never_reaches_ctx_review(self):
        t = child(status="impl-review")
        parent = Task(id="t2", name="Super", status="in-progress")
        with self.assertRaises(TaskError) as ctx:
            self.set(t, parent, "ctx-review")
        self.assertIn("illegal transition impl-review → ctx-review", str(ctx.exception))

    def test_subtask_in_progress_cannot_jump_to_ctx_review(self):
        t = child(status="in-progress")
        parent = Task(id="t2", name="Super", status="in-progress")
        with self.assertRaises(TaskError):
            self.set(t, parent, "ctx-review")

    def test_require_draft_blocks_non_draft(self):
        t = leaf(status="in-progress")
        with self.assertRaises(TaskError) as ctx:
            state.require_draft(t, "rename")
        self.assertIn("t1 is not draft", str(ctx.exception))

    def test_require_draft_blocks_non_draft_children(self):
        t = super_task(children=[child(status="in-progress")])
        with self.assertRaises(TaskError) as ctx:
            state.require_draft(t, "rename")
        self.assertIn("child t2.1 is not draft", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
