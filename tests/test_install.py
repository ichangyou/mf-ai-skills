from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install.py"
NAMES = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}


class InstallTests(unittest.TestCase):
    def run_install(self, project, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--scope", "project", "--project", str(project), *arguments],
            capture_output=True, text=True,
        )

    def test_both_platforms_receive_every_skill_and_links_are_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            result = self.run_install(project)
            self.assertEqual(result.returncode, 0, result.stderr)
            for platform in (".agents", ".claude"):
                directory = project / platform / "skills"
                self.assertEqual({p.name for p in directory.iterdir()}, NAMES)
                for name in NAMES:
                    self.assertEqual((directory / name).resolve(), ROOT / "skills" / name)
            before = (project / ".agents/skills/mufeng-book-notes").lstat().st_mtime_ns
            self.assertEqual(self.run_install(project).returncode, 0)
            self.assertEqual((project / ".agents/skills/mufeng-book-notes").lstat().st_mtime_ns, before)
            # Copy mode must not silently retain a link or overwrite the install.
            self.assertNotEqual(self.run_install(project, "--mode", "copy", "--skill", "mufeng-book-notes").returncode, 0)
            self.assertTrue((project / ".agents/skills/mufeng-book-notes").is_symlink())

    def test_conflict_does_not_overwrite_or_partially_install_other_platform(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            existing = project / ".claude/skills/mufeng-book-notes"
            existing.mkdir(parents=True)
            marker = existing / "user-content.md"
            marker.write_text("keep my local skill")
            result = self.run_install(project, "--skill", "mufeng-book-notes")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(), "keep my local skill")
            self.assertFalse((project / ".agents").exists())

    def test_copy_mode_has_independent_resources_and_only_selected_platform(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            result = self.run_install(project, "--platform", "claude", "--skill", "mufeng-ios-visual-regression", "--mode", "copy")
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = project / ".claude/skills/mufeng-ios-visual-regression"
            self.assertFalse(installed.is_symlink())
            self.assertEqual((installed / "scripts/run.sh").read_bytes(), (ROOT / "skills/mufeng-ios-visual-regression/scripts/run.sh").read_bytes())
            self.assertTrue((installed / "assets/templates/config.template.json").is_file())
            self.assertFalse((project / ".agents").exists())

    def test_unknown_skill_and_dry_run_leave_target_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.assertNotEqual(self.run_install(project, "--skill", "../unknown").returncode, 0)
            self.assertEqual(self.run_install(project, "--dry-run").returncode, 0)
            self.assertEqual(list(project.iterdir()), [])

    def test_relocating_repository_keeps_repo_links_valid(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            (source / "skills/example").mkdir(parents=True)
            (source / "skills/example/SKILL.md").write_text("---\nname: example\ndescription: A task.\n---\n")
            (source / "scripts").mkdir()
            installer = source / "scripts/install.py"
            installer.write_bytes(SCRIPT.read_bytes())
            result = subprocess.run([sys.executable, str(installer), "--scope", "project", "--project", str(source)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            moved = base / "moved"
            source.rename(moved)
            for platform in (".agents", ".claude"):
                self.assertEqual((moved / platform / "skills/example").resolve(), (moved / "skills/example").resolve())


if __name__ == "__main__":
    unittest.main()
