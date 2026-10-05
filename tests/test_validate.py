import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_skills", ROOT / "scripts/validate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ValidationTests(unittest.TestCase):
    def fixture(self, root):
        skill = root / "skills/example"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: example\ndescription: An example task.\n---\n\nDo the task.\n")
        (skill / "README.md").write_text("# Example\n")
        (root / "README.md").write_text("[Example](skills/example/README.md)\n")
        (root / "CONTRIBUTING.md").write_text("# Contribute\n")
        for platform in (".agents", ".claude"):
            directory = root / platform / "skills"
            directory.mkdir(parents=True)
            (directory / "example").symlink_to("../../skills/example", target_is_directory=True)
        return skill

    def test_valid_fixture_and_real_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            self.assertEqual(MODULE.validate(root), [])
        self.assertEqual(MODULE.validate(ROOT), [])

    def test_invalid_multiline_yaml_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = self.fixture(root)
            (skill / "SKILL.md").write_text("---\nname: example\ndescription: Use when debugging\n  fails. Triggers: errors\n---\n")
            self.assertTrue(any("invalid YAML" in error for error in MODULE.validate(root)))

    def test_new_skill_requires_both_entries_and_catalog(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            new = root / "skills/new-task"
            new.mkdir()
            (new / "SKILL.md").write_text("---\nname: new-task\ndescription: A new task.\n---\n")
            (new / "README.md").write_text("# New task\n")
            errors = MODULE.validate(root)
            self.assertTrue(any(".agents/skills" in error and "new-task" in error for error in errors))
            self.assertTrue(any(".claude/skills" in error and "new-task" in error for error in errors))
            self.assertTrue(any("missing catalog link" in error for error in errors))

    def test_broken_reference_and_personal_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = self.fixture(root)
            (skill / "README.md").write_text("[Missing](references/missing.md)\n\nUse `/Users/example/private/tool.py`.\n")
            errors = MODULE.validate(root)
            self.assertTrue(any("broken local link" in error for error in errors))
            self.assertTrue(any("personal absolute path" in error for error in errors))

    def test_platform_specific_fields_and_outdated_count_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = self.fixture(root)
            (skill / "SKILL.md").write_text("---\nname: example\ndescription: A task.\ncontext: fork\n---\n")
            (root / "README.md").write_text("共 15 个\n\n[Example](skills/example/README.md)\n")
            errors = MODULE.validate(root)
            self.assertTrue(any("non-portable frontmatter fields" in error for error in errors))
            self.assertTrue(any("declared count" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
