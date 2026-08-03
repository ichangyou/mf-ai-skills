import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "mufeng_storybook.py"
)
SPEC = importlib.util.spec_from_file_location("mufeng_storybook_test_module", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_png(path: Path, color=(20, 80, 140)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 48), color).save(path, "PNG")


class MufengStorybookTests(unittest.TestCase):
    def test_markdown_walk_prunes_excluded_and_output_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            (project / "source.md").write_text("source", encoding="utf-8")
            (project / "nested").mkdir()
            (project / "nested" / "story.markdown").write_text("story", encoding="utf-8")
            outside = root / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            (project / "linked.md").symlink_to(outside)
            output = project / "custom-output"
            for directory in (
                project / "build",
                project / "cache",
                project / "vendor",
                project / "node_modules",
                project / ".hidden",
                output,
            ):
                directory.mkdir()
                (directory / "ignored.md").write_text("ignored", encoding="utf-8")

            files = MODULE.markdown_files(project, excluded_paths=[output])
            self.assertEqual(
                [path.relative_to(project).as_posix() for path in files],
                ["nested/story.markdown", "source.md"],
            )

    def test_output_directory_must_be_a_strict_project_child(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / "story.md").write_text(
                "这是一段足够长的故事文本，用来验证输出目录不能和项目目录相同。",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--project-dir",
                    str(project),
                    "--output-dir",
                    str(project),
                    "--prompts-only",
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be a child directory", result.stderr)

    def test_project_guard_rejects_home_and_root(self):
        with self.assertRaisesRegex(RuntimeError, "home directory"):
            MODULE.validate_project_dir(Path.home())
        with self.assertRaisesRegex(RuntimeError, "filesystem root"):
            MODULE.validate_project_dir(Path(Path.home().anchor))
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(
                MODULE.validate_project_dir(Path(temporary)),
                Path(temporary).resolve(),
            )

    def test_draft_auto_and_manual_counts(self):
        short = {"story.md": "一段足够长的儿童故事文字，用来验证六页草稿模式。"}
        long = {"story.md": "山河故事" * 1600}
        self.assertEqual(MODULE.resolve_scene_count("auto", short, draft=True)[0], 6)
        self.assertEqual(MODULE.resolve_scene_count("auto", long, draft=True)[0], 8)
        self.assertEqual(MODULE.resolve_scene_count("8", short, draft=True)[0], 8)
        with self.assertRaisesRegex(RuntimeError, "exactly 6 or 8"):
            MODULE.resolve_scene_count("12", short, draft=True)
        self.assertEqual(MODULE.resolve_scene_count("auto", short, draft=False)[0], 12)

    def test_png_validation_rejects_corrupt_symlink_and_placeholder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            valid = root / "valid.png"
            write_png(valid)
            self.assertTrue(MODULE.inspect_png(valid)[0])

            corrupt = root / "corrupt.png"
            corrupt.write_bytes(b"\x89PNG\r\n\x1a\nbroken")
            self.assertFalse(MODULE.inspect_png(corrupt)[0])

            renamed_jpeg = root / "renamed.png"
            Image.new("RGB", (10, 10)).save(renamed_jpeg, "JPEG")
            self.assertFalse(MODULE.inspect_png(renamed_jpeg)[0])

            symlink = root / "linked.png"
            symlink.symlink_to(valid)
            self.assertFalse(MODULE.inspect_png(symlink)[0])

            placeholder = root / "placeholder.png"
            scene = MODULE.Scene(1, "草稿", "Draft", "", "旁白", "Narration", "", "")
            MODULE.create_placeholder(placeholder, scene, (320, 200))
            self.assertFalse(MODULE.inspect_png(placeholder)[0])
            self.assertTrue(MODULE.inspect_png(placeholder, allow_placeholder=True)[0])

            original_limit = Image.MAX_IMAGE_PIXELS
            Image.MAX_IMAGE_PIXELS = 1
            try:
                valid_result, reason, _details = MODULE.inspect_png(valid)
            finally:
                Image.MAX_IMAGE_PIXELS = original_limit
            self.assertFalse(valid_result)
            self.assertIn("decode failed", reason)

    def test_progress_and_placeholder_writes_reject_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside_progress = root / "outside-progress.txt"
            outside_progress.write_text("keep", encoding="utf-8")
            progress = root / "progress.jsonl"
            progress.symlink_to(outside_progress)
            with self.assertRaisesRegex(RuntimeError, "must not be a symlink"):
                MODULE.append_progress(progress, "test")
            with self.assertRaisesRegex(RuntimeError, "must not be a symlink"):
                MODULE.read_progress(progress)
            self.assertEqual(outside_progress.read_text(encoding="utf-8"), "keep")

            outside_image = root / "outside-image.png"
            write_png(outside_image)
            original_hash = MODULE.sha256_file(outside_image)
            target = root / "placeholder.png"
            target.symlink_to(outside_image)
            scene = MODULE.Scene(1, "草稿", "Draft", "", "", "", "", "")
            with self.assertRaisesRegex(RuntimeError, "must not be a symlink"):
                MODULE.create_placeholder(target, scene, (320, 200))
            self.assertEqual(MODULE.sha256_file(outside_image), original_hash)

    def test_casefolded_image_names_collide(self):
        scenes = [
            MODULE.Scene(1, "一", "One", "", "", "", "", "prompt", expected_image="Page.png"),
            MODULE.Scene(2, "二", "Two", "", "", "", "", "prompt", expected_image="page.png"),
        ]
        with self.assertRaisesRegex(RuntimeError, "Duplicate expected image filename"):
            MODULE.finalize_scenes(scenes)

    def test_manifest_v2_requires_hash_and_legacy_migration_is_explicit(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out"
            scene = MODULE.Scene(1, "一", "One", "", "旁白", "Narration", "", "prompt")
            MODULE.finalize_scenes([scene])
            MODULE.write_outputs(
                [],
                [scene],
                output,
                "Story",
                {"mode": "manual", "selected": 1},
                "final",
            )
            manifest_path = output / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.pop("plan_sha256")
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "v4 is missing"):
                MODULE.load_manifest(manifest_path)

            manifest.pop("manifest_version")
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "migrate-legacy-manifest"):
                MODULE.load_manifest(manifest_path)
            _raw, loaded = MODULE.load_manifest(manifest_path, allow_legacy=True)
            self.assertEqual(len(loaded), 1)

    def test_parallel_shared_directory_diff_is_rejected(self):
        MODULE.validate_generation_config(1, "directory-diff")
        MODULE.validate_generation_config(4, "per-call-path")
        MODULE.validate_generation_config(2, "isolated-worker-dir")
        with self.assertRaisesRegex(RuntimeError, "shared directory diff"):
            MODULE.validate_generation_config(2, "directory-diff")
        with self.assertRaisesRegex(RuntimeError, "between 1 and 4"):
            MODULE.validate_generation_config(5, "per-call-path")

    def test_reference_master_is_hash_locked_and_proxy_is_1024_jpeg(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            source = project / "assets" / "hero.png"
            source.parent.mkdir(parents=True)
            Image.new("RGBA", (2000, 1000), (40, 90, 150, 160)).save(source, "PNG")
            original_bytes = source.read_bytes()
            spec = project / "references.json"
            spec.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "references": [
                            {"id": "hero-master", "path": "assets/hero.png", "role": "master"}
                        ],
                    }
                ),
                encoding="utf-8",
            )

            catalog = MODULE.prepare_project_references(project.resolve(), spec)
            entry = catalog["hero-master"]
            master = project / entry["master_path"]
            upload = project / entry["upload_path"]
            self.assertEqual(master.read_bytes(), original_bytes)
            self.assertEqual(MODULE.sha256_file(master), entry["master_sha256"])
            with Image.open(upload) as image:
                self.assertEqual(image.format, "JPEG")
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(image.size, (1024, 512))
                self.assertNotIn("exif", image.info)
            self.assertLess(upload.stat().st_size, master.stat().st_size)

            repeated = MODULE.prepare_project_references(project.resolve(), spec)
            self.assertEqual(repeated["hero-master"], entry)

            linked_assets = project / "linked-assets"
            linked_assets.symlink_to(source.parent, target_is_directory=True)
            linked_spec = project / "linked-references.json"
            linked_spec.write_text(
                json.dumps(
                    {
                        "references": [
                            {
                                "id": "linked-hero",
                                "path": "linked-assets/hero.png",
                                "role": "continuity",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "project-internal symlinks"):
                MODULE.prepare_project_references(project.resolve(), linked_spec)

            Image.new("RGB", (100, 100), (200, 10, 10)).save(source, "PNG")
            with self.assertRaisesRegex(RuntimeError, "hash-locked"):
                MODULE.prepare_project_references(project.resolve(), spec)

    def test_reference_tasks_are_frozen_limited_and_logged_as_local_payload(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            output = project / "build" / "storybook"
            assets = project / "assets"
            assets.mkdir(parents=True)
            for name, color in (
                ("hero.png", (20, 80, 140)),
                ("sword.png", (130, 100, 40)),
            ):
                write_png(assets / name, color)
            spec = project / "references.json"
            spec.write_text(
                json.dumps(
                    {
                        "references": [
                            {"id": "hero", "path": "assets/hero.png", "role": "master"},
                            {
                                "id": "sword",
                                "path": "assets/sword.png",
                                "role": "continuity",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            catalog = MODULE.prepare_project_references(project.resolve(), spec)
            scene = MODULE.Scene(
                1,
                "相遇",
                "Meeting",
                "",
                "旁白",
                "Narration",
                "",
                "prompt",
                references=["hero", "sword"],
            )
            MODULE.finalize_scenes([scene])
            MODULE.validate_scene_references([scene], catalog)
            frozen_catalog, snapshot_hash = MODULE.write_reference_snapshot(
                output,
                project.resolve(),
                [scene],
                catalog,
            )
            MODULE.write_outputs(
                [],
                [scene],
                output,
                "Story",
                {"mode": "manual", "selected": 1},
                "final",
                snapshot_hash,
            )
            inspections = MODULE.inspect_scene_images([scene], output / "images")
            plan = MODULE.write_generation_plan(
                output,
                [scene],
                inspections,
                "final",
                1,
                "directory-diff",
                frozen_catalog,
                snapshot_hash,
                project.resolve(),
            )
            task = plan["tasks"][0]
            self.assertEqual(task["reference_count"], 2)
            self.assertEqual(
                task["reference_payload_bytes"],
                sum(item["size_bytes"] for item in task["references"]),
            )
            self.assertEqual(
                task["referenced_image_paths"],
                [item["path"] for item in task["references"]],
            )
            self.assertTrue(all(Path(path).is_file() for path in task["referenced_image_paths"]))
            MODULE.load_generation_plan(output)
            MODULE.record_generation_event(
                output,
                "generation_started",
                task["task_id"],
            )
            event = MODULE.read_progress(output / MODULE.PROGRESS_LOG_NAME)[-1]
            self.assertEqual(event["reference_count"], 2)
            self.assertEqual(
                event["local_reference_payload_bytes"],
                task["reference_payload_bytes"],
            )

            changed_catalog = json.loads(json.dumps(frozen_catalog))
            changed_catalog["hero"]["upload_sha256"] = "0" * 64
            with self.assertRaisesRegex(RuntimeError, "different reference bytes"):
                MODULE.write_reference_snapshot(
                    output,
                    project.resolve(),
                    [scene],
                    changed_catalog,
                )

            original_plan_text = (output / MODULE.GENERATION_PLAN_NAME).read_text(
                encoding="utf-8"
            )
            unsafe_parallel = json.loads(original_plan_text)
            unsafe_parallel["concurrency"] = 4
            unsafe_parallel["mapping_mode"] = "directory-diff"
            (output / MODULE.GENERATION_PLAN_NAME).write_text(
                json.dumps(unsafe_parallel, ensure_ascii=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "shared directory diff"):
                MODULE.load_generation_plan(output)

            false_complete = json.loads(original_plan_text)
            false_complete["tasks"][0]["status"] = "complete"
            false_complete["tasks"][0]["image"] = {
                "size_bytes": 1,
                "width": 1,
                "height": 1,
                "sha256": "0" * 64,
            }
            false_complete["summary"]["complete"] = 1
            false_complete["summary"]["pending"] = 0
            false_complete["summary"][
                "planned_reference_payload_bytes_per_pending_pass"
            ] = 0
            (output / MODULE.GENERATION_PLAN_NAME).write_text(
                json.dumps(false_complete, ensure_ascii=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "claims complete"):
                MODULE.load_generation_plan(output)
            (output / MODULE.GENERATION_PLAN_NAME).write_text(
                original_plan_text,
                encoding="utf-8",
            )

            too_many = MODULE.Scene(
                2,
                "过多",
                "Too many",
                "",
                "",
                "",
                "",
                "prompt",
                references=["one", "two", "three", "four"],
            )
            with self.assertRaisesRegex(RuntimeError, "hard limit is 3"):
                MODULE.finalize_scenes([too_many])
            duplicate = MODULE.Scene(
                2,
                "重复",
                "Duplicate",
                "",
                "",
                "",
                "",
                "prompt",
                references=["hero", "hero"],
            )
            with self.assertRaisesRegex(RuntimeError, "repeats reference ID"):
                MODULE.finalize_scenes([duplicate])
            unknown = MODULE.Scene(
                2,
                "未知",
                "Unknown",
                "",
                "",
                "",
                "",
                "prompt",
                references=["unknown"],
            )
            MODULE.finalize_scenes([unknown])
            with self.assertRaisesRegex(RuntimeError, "unknown ID"):
                MODULE.validate_scene_references([unknown], catalog)

    def test_pdf_only_preserves_generation_files_and_rejected_archive_deduplicates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            output = project / "build" / "storybook"
            scene = MODULE.Scene(
                1,
                "原标题",
                "Original title",
                "",
                "原旁白",
                "Original narration",
                "",
                "prompt",
            )
            MODULE.finalize_scenes([scene])
            MODULE.write_outputs(
                [],
                [scene],
                output,
                "Story",
                {"mode": "manual", "selected": 1},
                "final",
            )
            inspections = MODULE.inspect_scene_images([scene], output / "images")
            plan = MODULE.write_generation_plan(
                output,
                [scene],
                inspections,
                "final",
                1,
                "directory-diff",
            )
            write_png(output / "images" / scene.expected_image)
            reference_manifest = output / MODULE.REFERENCE_MANIFEST_NAME
            reference_manifest.write_bytes(b"pdf-only sentinel")
            reference_asset = project / ".mufeng-storybook" / "references" / "upload" / "sentinel.jpg"
            reference_asset.parent.mkdir(parents=True)
            reference_asset.write_bytes(b"reference sentinel")
            protected = [
                output / "manifest.json",
                output / MODULE.GENERATION_PLAN_NAME,
                reference_manifest,
                reference_asset,
            ]
            before = {
                path: (path.read_bytes(), path.stat().st_mtime_ns)
                for path in protected
            }
            captions = project / "captions.json"
            captions.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "pages": [
                            {
                                "number": 1,
                                "title_zh": "新标题",
                                "title_en": "New title",
                                "narration_zh": "新旁白",
                                "narration_en": "New narration",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            result = MODULE.rebuild_pdfs_only(
                output,
                "both",
                "示例故事 · 第一章",
                "Example Story · Chapter 1",
                captions,
            )
            self.assertEqual(result["status"], "pdf_only_complete")
            self.assertTrue((output / "storybook.pdf").stat().st_size > 0)
            self.assertTrue((output / "storybook_en.pdf").stat().st_size > 0)
            for path in protected:
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before[path])

            _raw, loaded = MODULE.load_manifest(output / "manifest.json")
            overrides = MODULE.load_caption_overrides(captions, loaded)
            changed = MODULE.apply_caption_overrides(loaded, overrides)
            self.assertEqual(loaded[0].title_zh, "原标题")
            self.assertEqual(changed[0].title_zh, "新标题")
            self.assertEqual(changed[0].prompt, loaded[0].prompt)
            forbidden = project / "forbidden-captions.json"
            forbidden.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "pages": [{"number": 1, "prompt": "must not change"}],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "forbidden or unknown"):
                MODULE.load_caption_overrides(forbidden, loaded)

            generated_root = root / "generated_images"
            rejected_source = generated_root / "session" / "rejected.png"
            write_png(rejected_source, color=(190, 30, 60))
            task_id = plan["tasks"][0]["task_id"]
            archived = MODULE.archive_rejected_attempt(
                output,
                task_id,
                rejected_source,
                generated_root=generated_root,
            )
            duplicate = MODULE.archive_rejected_attempt(
                output,
                task_id,
                rejected_source,
                generated_root=generated_root,
            )
            self.assertEqual(archived["status"], "archived")
            self.assertEqual(duplicate["status"], "duplicate")
            self.assertEqual(
                len(list((output / "rejected_attempts").glob("*.png"))),
                1,
            )
            self.assertEqual(
                MODULE.sha256_file(Path(archived["path"])),
                archived["sha256"],
            )

    def test_quality_contract_rejects_contradictions(self):
        scene = MODULE.Scene(
            1,
            "相遇",
            "Meeting",
            "",
            "旁白",
            "Narration",
            "",
            "prompt",
            qa={
                "required_entities": ["hero"],
                "forbidden_entities": ["hero"],
            },
        )
        with self.assertRaisesRegex(RuntimeError, "requires and forbids"):
            MODULE.finalize_scenes([scene])

        valid = MODULE.Scene(
            1,
            "相遇",
            "Meeting",
            "",
            "旁白",
            "Narration",
            "",
            "prompt",
            references=["hero"],
            qa={
                "risk_level": "high",
                "required_entities": ["hero"],
                "forbidden_entities": ["horse"],
                "exact_counts": {"hero": 1},
                "reference_bindings": {
                    "hero": {
                        "use_for": ["identity"],
                        "do_not_copy": ["background"],
                    }
                },
            },
        )
        MODULE.finalize_scenes([valid])
        self.assertIn("required_entities", MODULE.qa_required_check_ids(valid))
        self.assertIn("reference_bindings", MODULE.qa_required_check_ids(valid))

    def test_candidate_qa_gate_promotes_only_passing_artwork(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            output = project / "build" / "storybook"
            project.mkdir()
            scene = MODULE.Scene(
                1,
                "相遇",
                "Meeting",
                "",
                "旁白",
                "Narration",
                "",
                "prompt",
                qa={
                    "risk_level": "high",
                    "required_entities": ["hero"],
                    "forbidden_entities": ["horse"],
                    "exact_counts": {"hero": 1},
                },
            )
            MODULE.finalize_scenes([scene])
            MODULE.write_outputs(
                [],
                [scene],
                output,
                "Story",
                {"mode": "manual", "selected": 1},
                "final",
                footer_zh="示例故事 · 第一章",
                footer_en="Example Story · Chapter 1",
                quality_gate_required=True,
            )
            manifest_path = output / "manifest.json"
            original_manifest = manifest_path.read_text(encoding="utf-8")
            tampered_manifest = json.loads(original_manifest)
            tampered_manifest["quality_gate_required"] = False
            manifest_path.write_text(json.dumps(tampered_manifest), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "release contract hash mismatch"):
                MODULE.load_manifest(manifest_path)
            manifest_path.write_text(original_manifest, encoding="utf-8")
            inspections = MODULE.inspect_scene_images([scene], output / "images")
            plan = MODULE.write_generation_plan(
                output,
                [scene],
                inspections,
                "final",
                1,
                "directory-diff",
            )
            task_id = plan["tasks"][0]["task_id"]
            generated_root = root / "generated_images"

            first_source = generated_root / "session" / "first.png"
            write_png(first_source, color=(180, 40, 20))
            with self.assertRaisesRegex(RuntimeError, "unaudited candidate import"):
                MODULE.import_generated_candidate(
                    output,
                    task_id,
                    first_source,
                    generated_root=generated_root,
                )
            MODULE.record_generation_event(output, "generation_started", task_id)
            MODULE.record_generation_event(output, "generation_returned", task_id)
            first = MODULE.import_generated_candidate(
                output,
                task_id,
                first_source,
                generated_root=generated_root,
            )
            required_checks = first["required_checks"]
            failed_report = project / "failed-qa.json"
            failed_report.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "task_id": task_id,
                        "candidate_sha256": first["candidate_sha256"],
                        "verdict": "fail",
                        "reviewer": "codex-vision",
                        "checks": [
                            {
                                "id": check_id,
                                "result": "fail" if check_id == "forbidden_entities" else "pass",
                                "detail": "unexpected horse" if check_id == "forbidden_entities" else "ok",
                            }
                            for check_id in required_checks
                        ],
                        "failure_codes": ["extra_character"],
                        "detail": "A forbidden horse is visible.",
                    }
                ),
                encoding="utf-8",
            )
            failed = MODULE.record_candidate_qa(
                output,
                task_id,
                first["candidate_sha256"],
                failed_report,
            )
            self.assertEqual(failed["status"], "fail")
            self.assertIn("unexpected horse", failed["retry_prompt"].lower())
            self.assertFalse((output / "images" / scene.expected_image).exists())
            self.assertTrue(Path(failed["archived"]).is_file())

            second_source = generated_root / "session" / "second.png"
            write_png(second_source, color=(20, 120, 60))
            MODULE.record_generation_event(output, "generation_started", task_id)
            MODULE.record_generation_event(output, "generation_returned", task_id)
            second = MODULE.import_generated_candidate(
                output,
                task_id,
                second_source,
                generated_root=generated_root,
            )
            passed_report = project / "passed-qa.json"
            passed_report.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "task_id": task_id,
                        "candidate_sha256": second["candidate_sha256"],
                        "verdict": "pass",
                        "reviewer": "codex-vision",
                        "checks": [
                            {"id": check_id, "result": "pass", "detail": "verified"}
                            for check_id in second["required_checks"]
                        ],
                        "failure_codes": [],
                        "detail": "All scene and continuity checks passed.",
                    }
                ),
                encoding="utf-8",
            )
            passed = MODULE.record_candidate_qa(
                output,
                task_id,
                second["candidate_sha256"],
                passed_report,
            )
            self.assertEqual(passed["status"], "approved")
            manifest, scenes = MODULE.load_manifest(output / "manifest.json")
            MODULE.require_quality_gate(output, scenes, manifest)
            gate_path = output / MODULE.QUALITY_GATE_NAME
            original_gate = gate_path.read_text(encoding="utf-8")
            tampered_gate = json.loads(original_gate)
            tampered_gate["attempts"][0]["reviewer"] = "tampered-reviewer"
            gate_path.write_text(json.dumps(tampered_gate), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "quality gate hash mismatch"):
                MODULE.load_quality_gate(output, manifest["plan_sha256"])
            gate_path.write_text(original_gate, encoding="utf-8")
            rebuilt = MODULE.rebuild_pdfs_only(output, "both", None, None)
            self.assertEqual(rebuilt["status"], "pdf_only_complete")
            self.assertTrue((output / "preview" / "final" / "zh" / "page_01.png").is_file())
            self.assertTrue((output / "preview" / "final" / "en" / "page_01.png").is_file())
            with self.assertRaisesRegex(RuntimeError, "Generic final footer"):
                MODULE.rebuild_pdfs_only(output, "both", "绘本", "Storybook")

    def test_cli_draft_resume_import_and_pdf_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            output = project / "out"
            project.mkdir()
            source = project / "story.md"
            source.write_text(
                "# 小河故事\n\n小鹿沿着河流寻找朋友，经过树林、石桥和开满花朵的山坡。",
                encoding="utf-8",
            )

            first = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--project-dir",
                    str(project),
                    "--output-dir",
                    str(output),
                    "--draft",
                    "--prompts-only",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            plan = json.loads(
                (output / MODULE.GENERATION_PLAN_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["scene_count"], 6)
            self.assertEqual(manifest["workflow_mode"], "draft")
            self.assertEqual(plan["summary"]["total"], 6)
            self.assertEqual(plan["summary"]["complete"], 0)
            self.assertEqual(plan["summary"]["pending"], 6)
            self.assertEqual(
                plan["summary"]["planned_reference_payload_bytes_per_pending_pass"],
                0,
            )
            frozen_hash = manifest["plan_sha256"]

            tampered_plan = json.loads(json.dumps(plan))
            tampered_plan["tasks"][0]["prompt"] = "tampered prompt"
            (output / MODULE.GENERATION_PLAN_NAME).write_text(
                json.dumps(tampered_plan, ensure_ascii=False),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "field prompt differs"):
                MODULE.load_generation_plan(output)
            (output / MODULE.GENERATION_PLAN_NAME).write_text(
                json.dumps(plan, ensure_ascii=False),
                encoding="utf-8",
            )

            source.write_text("# 已修改\n\n源文件已经发生显著变化，但恢复必须沿用冻结分镜。", encoding="utf-8")
            resumed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-dir",
                    str(output),
                    "--resume",
                    "--prompts-only",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            resumed_manifest = json.loads(
                (output / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(resumed_manifest["plan_sha256"], frozen_hash)

            missing = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-dir",
                    str(output),
                    "--use-existing-images",
                    "--language",
                    "zh",
                ],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("Missing or invalid expected images", missing.stderr)
            self.assertFalse((output / "storybook.pdf").exists())

            generated_root = root / "generated_images"
            generated_source = generated_root / "session" / "result.png"
            write_png(generated_source)
            first_task = plan["tasks"][0]
            source_symlink = generated_root / "session" / "alias.png"
            source_symlink.symlink_to(generated_source)
            with self.assertRaisesRegex(RuntimeError, "must not be a symlink"):
                MODULE.import_generated_image(
                    output,
                    first_task["task_id"],
                    source_symlink,
                    generated_root=generated_root,
                )
            MODULE.record_generation_event(
                output,
                "generation_started",
                first_task["task_id"],
            )
            MODULE.record_generation_event(
                output,
                "generation_returned",
                first_task["task_id"],
            )
            imported = MODULE.import_generated_image(
                output,
                first_task["task_id"],
                generated_source,
                generated_root=generated_root,
            )
            self.assertEqual(imported.status, "complete")
            imported_hash = imported.sha256
            imported_plan = json.loads(
                (output / MODULE.GENERATION_PLAN_NAME).read_text(encoding="utf-8")
            )
            imported_task = next(
                task
                for task in imported_plan["tasks"]
                if task["task_id"] == first_task["task_id"]
            )
            self.assertEqual(imported_task["status"], "complete")
            self.assertEqual(imported_plan["summary"]["complete"], 1)
            _frozen_manifest, frozen_scenes = MODULE.load_manifest(
                output / "manifest.json"
            )
            stale_inspections = [
                MODULE.ImageInspection(
                    task_id=frozen_scene.task_id,
                    scene_number=frozen_scene.number,
                    expected_image=frozen_scene.expected_image,
                    image_path=str(output / "images" / frozen_scene.expected_image),
                    status="pending",
                    reason="stale pre-import scan",
                )
                for frozen_scene in frozen_scenes
            ]
            race_safe_plan = MODULE.write_generation_plan(
                output,
                frozen_scenes,
                stale_inspections,
                "draft",
                1,
                "directory-diff",
            )
            self.assertEqual(race_safe_plan["summary"]["complete"], 1)
            self.assertEqual(
                next(
                    task
                    for task in race_safe_plan["tasks"]
                    if task["task_id"] == first_task["task_id"]
                )["status"],
                "complete",
            )
            with self.assertRaisesRegex(RuntimeError, "already has a valid project PNG"):
                MODULE.record_generation_event(
                    output,
                    "generation_started",
                    first_task["task_id"],
                )

            second_source = generated_root / "session" / "different.png"
            write_png(second_source, color=(180, 40, 20))
            skipped = MODULE.import_generated_image(
                output,
                first_task["task_id"],
                second_source,
                generated_root=generated_root,
            )
            self.assertEqual(skipped.sha256, imported_hash)

            refreshed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-dir",
                    str(output),
                    "--resume",
                    "--prompts-only",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(refreshed.returncode, 0, refreshed.stderr)
            refreshed_plan = json.loads(
                (output / MODULE.GENERATION_PLAN_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(refreshed_plan["summary"]["complete"], 1)

            for task in refreshed_plan["tasks"][1:]:
                write_png(output / "images" / task["expected_image"])
            built = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-dir",
                    str(output),
                    "--use-existing-images",
                    "--language",
                    "both",
                    "--footer-zh",
                    "示例故事 · 第一章",
                    "--footer-en",
                    "Example Story · Chapter 1",
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            self.assertTrue((output / "storybook.pdf").stat().st_size > 0)
            self.assertTrue((output / "storybook_en.pdf").stat().st_size > 0)

            progress_records = MODULE.read_progress(output / MODULE.PROGRESS_LOG_NAME)
            events = {record["event"] for record in progress_records}
            self.assertIn("generation_started", events)
            self.assertIn("generation_returned", events)
            self.assertIn("image_imported", events)
            self.assertIn("pdf_written", events)


if __name__ == "__main__":
    unittest.main()
