"""Tests for laaw.core.sync (sync_workflow, sync_skills)."""

import tempfile
import unittest
from pathlib import Path


class SyncWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.target = str(Path(self.tmp.name) / "proj")
        Path(self.target).mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_fresh_project_when_sync_workflow_then_workflow_copied(self) -> None:
        from laaw.core.sync import sync_workflow

        message, code = sync_workflow(self.target)
        self.assertEqual(code, 0)
        dest = Path(self.target) / ".ai" / "workflow" / "workflow.md"
        self.assertTrue(dest.is_file())
        self.assertIn("synced", message)

    def test_given_existing_project_when_sync_workflow_then_indexes_kept(self) -> None:
        from laaw.core.sync import sync_workflow

        tasks_index = Path(self.target) / ".ai" / "tasks" / "index.md"
        tasks_index.parent.mkdir(parents=True)
        tasks_index.write_text("# Task index\n\n| ID | Status |\n", encoding="utf-8")
        message, code = sync_workflow(self.target)
        self.assertEqual(code, 0)
        self.assertEqual(
            tasks_index.read_text(encoding="utf-8"),
            "# Task index\n\n| ID | Status |\n",
        )

    def test_given_missing_gitignore_when_sync_workflow_then_entries_added(self) -> None:
        from laaw.core.sync import sync_workflow

        sync_workflow(self.target)
        gitignore = Path(self.target) / ".gitignore"
        content = gitignore.read_text(encoding="utf-8")
        self.assertIn(".ai/tasks/", content)
        self.assertIn(".ai/workflow/", content)

    def test_given_gitignore_with_entries_when_sync_workflow_then_no_duplicates(self) -> None:
        from laaw.core.sync import sync_workflow

        gitignore = Path(self.target) / ".gitignore"
        gitignore.write_text(".ai/tasks/\n", encoding="utf-8")
        message, code = sync_workflow(self.target)
        self.assertEqual(code, 0)
        content = gitignore.read_text(encoding="utf-8")
        self.assertEqual(content.count(".ai/tasks/"), 1)

    def test_given_no_agents_md_when_sync_workflow_then_created_with_workflow_section(self) -> None:
        from laaw.core.sync import sync_workflow

        message, code = sync_workflow(self.target)
        self.assertEqual(code, 0)
        agents = Path(self.target) / "AGENTS.md"
        self.assertTrue(agents.is_file())
        content = agents.read_text(encoding="utf-8")
        self.assertIn("## Workflow", content)
        self.assertIn("This project uses LAAW.", content)
        self.assertIn("AGENTS.md created", message)

    def test_given_agents_md_without_workflow_when_sync_workflow_then_section_appended(self) -> None:
        from laaw.core.sync import sync_workflow

        agents = Path(self.target) / "AGENTS.md"
        agents.write_text("# Agents\n\nOther content.\n", encoding="utf-8")
        message, code = sync_workflow(self.target)
        self.assertEqual(code, 0)
        content = agents.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("# Agents"))
        self.assertIn("## Workflow", content)
        self.assertIn("AGENTS.md appended", message)

    def test_given_agents_md_with_workflow_when_sync_workflow_then_untouched(self) -> None:
        from laaw.core.sync import sync_workflow

        agents = Path(self.target) / "AGENTS.md"
        original = "# Agents\n\n## Workflow\n\nThis project uses LAAW. Custom extra line.\n"
        agents.write_text(original, encoding="utf-8")
        message, code = sync_workflow(self.target)
        self.assertEqual(code, 0)
        self.assertEqual(agents.read_text(encoding="utf-8"), original)
        self.assertNotIn("AGENTS.md", message)

    def test_given_agents_md_when_sync_workflow_twice_then_no_duplicate_section(self) -> None:
        from laaw.core.sync import sync_workflow

        sync_workflow(self.target)
        sync_workflow(self.target)
        content = (Path(self.target) / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(content.count("## Workflow"), 1)

    def test_given_non_directory_when_sync_workflow_then_refused(self) -> None:
        from laaw.core.sync import sync_workflow

        message, code = sync_workflow(str(Path(self.tmp.name) / "nope"))
        self.assertEqual(code, 1)
        self.assertIn("not a directory", message)


class SyncSkillsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dest = str(Path(self.tmp.name) / "skills")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_given_skills_folder_when_sync_skills_then_all_copied(self) -> None:
        from laaw.core.sync import sync_skills

        message, code = sync_skills(self.dest)
        self.assertEqual(code, 0)
        for skill in ("plan-task", "implement-task", "propagate-context"):
            self.assertTrue((Path(self.dest) / skill).is_dir())

    def test_given_existing_dest_when_sync_skills_then_overwritten(self) -> None:
        from laaw.core.sync import sync_skills

        existing = Path(self.dest) / "plan-task"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("stale", encoding="utf-8")
        message, code = sync_skills(self.dest)
        self.assertEqual(code, 0)
        content = (existing / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotEqual(content, "stale")

    def test_given_empty_dest_when_sync_skills_then_copied_into_new_dir(self) -> None:
        from laaw.core.sync import sync_skills

        message, code = sync_skills(str(Path(self.tmp.name) / "deep" / "skills"))
        self.assertEqual(code, 0)
        self.assertTrue((Path(self.tmp.name) / "deep" / "skills").is_dir())


if __name__ == "__main__":
    unittest.main()
