import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "preview.py"
SPEC = importlib.util.spec_from_file_location("app_icon_preview", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PreviewTests(unittest.TestCase):
    def test_transparent_input_composites_on_each_background_without_changing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / "source.png", Path(tmp) / "review" / "preview.png"
            image = Image.new("RGBA", (256, 256), (255, 0, 0, 0))
            image.putpixel((128, 128), (255, 0, 0, 255))
            image.save(source)
            original = source.read_bytes()
            result = MODULE.generate_preview(source, output)
            self.assertTrue(result["has_transparency"])
            self.assertFalse(result["preview_upscaled"])
            self.assertEqual(result["source_size_px"], [256, 256])
            self.assertEqual(source.read_bytes(), original)
            with Image.open(output) as sheet:
                self.assertEqual(sheet.size, (1020, 696))
                for row, (_, gray) in enumerate(MODULE.BACKGROUNDS):
                    # Transparent corner of the 180px preview must reveal the row background.
                    self.assertEqual(sheet.getpixel((4 * 204 + 12, row * 232 + 38)), (gray,) * 3)

    def test_opaque_alpha_channel_is_not_reported_as_transparency_and_small_input_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / "small.png", Path(tmp) / "preview.png"
            Image.new("RGBA", (32, 32), (20, 80, 140, 255)).save(source)
            result = MODULE.generate_preview(source, output)
            self.assertFalse(result["has_transparency"])
            self.assertTrue(result["preview_upscaled"])
            with Image.open(output) as sheet:
                self.assertEqual(sheet.getpixel((102, 128)), (20, 80, 140))

    def test_invalid_shape_and_existing_output_leave_files_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / "source.png", Path(tmp) / "preview.png"
            Image.new("RGB", (64, 32)).save(source)
            with self.assertRaises(ValueError):
                MODULE.generate_preview(source, output)
            self.assertFalse(output.exists())
            Image.new("RGB", (64, 64)).save(source)
            output.write_bytes(b"existing review")
            with self.assertRaises(FileExistsError):
                MODULE.generate_preview(source, output)
            self.assertEqual(output.read_bytes(), b"existing review")
            with self.assertRaises(FileExistsError):
                MODULE.generate_preview(source, source)

    def test_cli_rejects_corrupt_input_without_claiming_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / "broken.png", Path(tmp) / "preview.png"
            source.write_bytes(b"not an image")
            result = subprocess.run([sys.executable, str(SCRIPT), str(source), "--output", str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Preview failed", result.stderr)
            self.assertFalse(output.exists())

    def test_cli_accepts_jpeg_and_webp_and_reports_real_output(self):
        import json

        with tempfile.TemporaryDirectory() as tmp:
            for suffix in ("jpg", "webp"):
                with self.subTest(suffix=suffix):
                    source = Path(tmp) / f"source.{suffix}"
                    output = Path(tmp) / f"preview-{suffix}.png"
                    Image.new("RGB", (256, 256), (20, 80, 140)).save(source)
                    result = subprocess.run([sys.executable, str(SCRIPT), str(source), "--output", str(output)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    report = json.loads(result.stdout)
                    self.assertFalse(report["has_transparency"])
                    self.assertEqual(Path(report["output"]), output.resolve())
                    with Image.open(output) as sheet:
                        sheet.verify()

    def test_animated_input_is_rejected_without_creating_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / "animated.png", Path(tmp) / "preview.png"
            Image.new("RGB", (32, 32), "red").save(
                source, save_all=True,
                append_images=[Image.new("RGB", (32, 32), "blue")], duration=100,
            )
            with self.assertRaises(ValueError):
                MODULE.generate_preview(source, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
