import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


STORY = load_module("storybook_compatibility", "skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py")
HISTORY = load_module("history_compatibility", "skills/mufeng-weread-x-writing/scripts/history.py")


class CompatibilityTests(unittest.TestCase):
    def test_external_image_root_imports_into_project_and_rejects_unrelated_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            output = root / "project/build"
            generated = root / "configured-provider/call-01"
            generated.mkdir(parents=True)
            source = generated / "image.png"
            Image.new("RGB", (64, 48), (20, 80, 140)).save(source)
            scene = STORY.Scene(1, "故事", "Story", "", "旁白", "Narration", "", "prompt")
            STORY.finalize_scenes([scene])
            STORY.write_outputs([], [scene], output, "Story", {"mode": "manual", "selected": 1}, "draft")
            plan = STORY.write_generation_plan(output, [scene], STORY.inspect_scene_images([scene], output / "images"), "draft", 1, "per-call-path")
            task_id = plan["tasks"][0]["task_id"]
            with patch.dict(os.environ, {"MUFENG_IMAGE_ROOT": str(root / "unrelated-provider")}):
                with self.assertRaisesRegex(RuntimeError, "outside the configured"):
                    STORY.import_generated_image(output, task_id, source)
            with patch.dict(os.environ, {"MUFENG_IMAGE_ROOT": str(root / "configured-provider")}):
                imported = STORY.import_generated_image(output, task_id, source)
                project_image = Path(imported.image_path)
                self.assertEqual(project_image.read_bytes(), source.read_bytes())
                self.assertTrue(project_image.is_relative_to(output))
                source.unlink()
                self.assertTrue(STORY.inspect_png(project_image)[0])

    def test_image_root_defaults_to_codex_and_rejects_broad_roots(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.dict(os.environ, {"CODEX_HOME": temporary, "MUFENG_IMAGE_ROOT": ""}):
                self.assertEqual(STORY.generation_root(), (Path(temporary) / "generated_images").resolve())
        for root in (str(Path.home()), str(Path.cwd().anchor)):
            with patch.dict(os.environ, {"MUFENG_IMAGE_ROOT": root}):
                with self.assertRaisesRegex(RuntimeError, "dedicated image-output"):
                    STORY.generation_root()

    def test_history_preserves_legacy_records_and_allows_explicit_location(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            legacy = root / "legacy/history.jsonl"
            current = root / "shared/history.jsonl"
            legacy.parent.mkdir()
            legacy.write_text('{"text":"existing"}\n')
            with patch.object(HISTORY, "LEGACY_HISTORY", legacy), patch.object(HISTORY, "DEFAULT_HISTORY", current), patch.dict(os.environ, {"MUFENG_WEREAD_X_HOME": ""}):
                self.assertEqual(HISTORY.history_path(None), legacy)
                current.parent.mkdir()
                current.touch()
                self.assertEqual(HISTORY.history_path(None), current)
                self.assertEqual(HISTORY.history_path(str(root / "explicit.jsonl")), root / "explicit.jsonl")
                with patch.dict(os.environ, {"MUFENG_WEREAD_X_HOME": str(root / "custom")}):
                    self.assertEqual(HISTORY.history_path(None), root / "custom/history.jsonl")
            self.assertEqual(legacy.read_text(), '{"text":"existing"}\n')


if __name__ == "__main__":
    unittest.main()
