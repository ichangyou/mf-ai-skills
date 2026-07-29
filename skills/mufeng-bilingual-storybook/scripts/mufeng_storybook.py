#!/usr/bin/env python3
"""Reusable bilingual picture-book helper.

This script handles deterministic parts of a Codex storybook workflow:
load Markdown, consume or infer a scene plan, write prompt/manifest files,
validate image filenames, create placeholder images for layout tests, and
assemble Chinese/English PDFs from the same image set.

It does not call image APIs. Generate art only with the Codex built-in
image_gen tool, then rerun with --use-existing-images. Do not use Google,
Gemini, GOOGLE_API_KEY, baoyu-image-gen, OpenAI Images API, or provider
fallbacks for storybook artwork.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import textwrap
import time
import unicodedata
import uuid
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "cache",
    "dist",
    "node_modules",
    "vendor",
    "venv",
}

GENERATION_PLAN_NAME = "generation_tasks.json"
PROGRESS_LOG_NAME = "progress.jsonl"
REFERENCE_MANIFEST_NAME = "reference_manifest.json"
MAX_REFERENCES_PER_TASK = 3
REFERENCE_MAX_EDGE = 1024
REFERENCE_JPEG_QUALITY = 85
REFERENCE_ROLES = {"master", "continuity", "style"}
REFERENCE_ID_PATTERN = re.compile(r"[a-z][a-z0-9_-]{0,63}")
MAPPING_MODES = {"directory-diff", "per-call-path", "isolated-worker-dir"}
PROGRESS_EVENTS = {
    "generation_started",
    "generation_returned",
    "generation_failed",
    "persistence_failed",
}


@dataclass
class Scene:
    number: int
    title_zh: str
    title_en: str
    description: str
    narration_zh: str
    narration_en: str
    source_excerpt: str
    prompt: str
    image_path: str = ""
    expected_image: str = ""
    task_id: str = ""
    references: List[str] = field(default_factory=list)


@dataclass
class ImageInspection:
    task_id: str
    scene_number: int
    expected_image: str
    image_path: str
    status: str
    reason: str
    size_bytes: int = 0
    width: int = 0
    height: int = 0
    sha256: str = ""


def validate_project_dir(project_dir: Path) -> Path:
    resolved = project_dir.expanduser().resolve()
    if not resolved.is_dir():
        raise RuntimeError(f"Project directory does not exist or is not a directory: {resolved}")
    if resolved == Path.home().resolve():
        raise RuntimeError(
            "Refusing to use the user home directory as --project-dir. "
            "Choose the specific story project directory."
        )
    if resolved == Path(resolved.anchor):
        raise RuntimeError(
            "Refusing to use a filesystem root as --project-dir. "
            "Choose the specific story project directory."
        )
    return resolved


def path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def markdown_files(project_dir: Path, excluded_paths: Sequence[Path] = ()) -> List[Path]:
    excluded = [path.expanduser().resolve() for path in excluded_paths]
    files: List[Path] = []
    for root, dirnames, filenames in os.walk(project_dir, topdown=True, followlinks=False):
        dirnames[:] = sorted(
            dirname
            for dirname in dirnames
            if (
                not dirname.startswith(".")
                and dirname not in EXCLUDED_DIRS
                and not any(
                    path_is_within((Path(root) / dirname).resolve(), excluded_path)
                    for excluded_path in excluded
                )
            )
        )
        root_path = Path(root)
        for filename in sorted(filenames):
            if filename.startswith("."):
                continue
            if Path(filename).suffix.lower() not in {".md", ".markdown"}:
                continue
            path = root_path / filename
            if path.is_file() and not path.is_symlink():
                files.append(path)
    return sorted(files, key=lambda path: path.as_posix())


def read_markdown(project_dir: Path, excluded_paths: Sequence[Path] = ()) -> Dict[str, str]:
    result = {
        str(path): path.read_text(encoding="utf-8")
        for path in markdown_files(project_dir, excluded_paths)
    }
    if not result:
        raise RuntimeError(f"No Markdown files found under {project_dir}")
    return result


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def plain_text(markdown: str) -> str:
    text = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_`>]+", "", text)
    return text.strip()


def markdown_plain_text(markdown: Dict[str, str]) -> str:
    return "\n\n".join(plain_text(content) for content in markdown.values())


def story_metrics(markdown: Dict[str, str]) -> Dict[str, int]:
    combined = markdown_plain_text(markdown)
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", combined))
    latin_words = len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", combined))
    paragraphs = [normalize(p) for p in re.split(r"\n\s*\n", combined) if len(normalize(p)) > 20]
    sentences = [normalize(s) for s in re.split(r"[。！？!?；;\n]+", combined) if len(normalize(s)) > 8]
    headings = sum(len(re.findall(r"^#{1,6}\s+", content, flags=re.MULTILINE)) for content in markdown.values())
    narrative_units = cjk_chars + latin_words
    effective_sentences = min(len(sentences), max(12, len(paragraphs) * 3))
    complexity_score = narrative_units + effective_sentences * 20 + len(paragraphs) * 70 + headings * 90
    return {
        "cjk_chars": cjk_chars,
        "latin_words": latin_words,
        "narrative_units": narrative_units,
        "paragraphs": len(paragraphs),
        "sentences": len(sentences),
        "effective_sentences": effective_sentences,
        "headings": headings,
        "complexity_score": complexity_score,
    }


def auto_scene_count(markdown: Dict[str, str]) -> Tuple[int, str, Dict[str, int]]:
    metrics = story_metrics(markdown)
    units = metrics["narrative_units"]
    paragraphs = metrics["paragraphs"]
    sentences = metrics["sentences"]
    if units <= 1400 and paragraphs <= 18 and sentences <= 60:
        return 12, "short story / compact single episode", metrics
    if units <= 2800 and paragraphs <= 30 and sentences <= 100:
        return 16, "medium chapter / several clear beats", metrics
    if units <= 5500 and paragraphs <= 85 and sentences <= 190:
        return 20, "formal picture-book chapter", metrics
    return 24, "long or complex chapter", metrics


def resolve_scene_count(
    value: str,
    markdown: Dict[str, str],
    draft: bool = False,
) -> Tuple[int, Dict[str, object]]:
    requested = value.strip().lower()
    if requested == "auto":
        final_count, reason, metrics = auto_scene_count(markdown)
        count = 6 if draft and final_count <= 16 else 8 if draft else final_count
        return count, {
            "mode": "draft-auto" if draft else "auto",
            "requested": value,
            "selected": count,
            "reason": f"draft storyboard from {reason}" if draft else reason,
            "metrics": metrics,
            "policy": {
                "short_story": 6 if draft else 12,
                "medium_chapter": 6 if draft else 16,
                "formal_picture_book_chapter": 8 if draft else 20,
                "long_or_complex_chapter": 8 if draft else 24,
            },
        }
    if not re.fullmatch(r"\d+", requested):
        raise RuntimeError("Use --scene-count auto or a positive integer, e.g. --scene-count 12")
    count = int(requested)
    if count < 1 or count > 60:
        raise RuntimeError("--scene-count must be between 1 and 60.")
    if draft and count not in (6, 8):
        raise RuntimeError("Draft mode supports exactly 6 or 8 scenes.")
    return count, {
        "mode": "draft-manual" if draft else "manual",
        "requested": value,
        "selected": count,
        "reason": "manual draft override" if draft else "manual override",
    }


def slug(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", value).strip("_")
    return cleaned or "page"


def default_image_name(scene: Scene) -> str:
    return f"scene_{scene.number:02d}_{slug(scene.title_zh)}.png"


def image_name(scene: Scene) -> str:
    return scene.expected_image or default_image_name(scene)


def scene_task_id(scene: Scene) -> str:
    parts = [str(scene.number), image_name(scene), scene.prompt]
    if scene.references:
        parts.extend(scene.references)
    digest_input = "\0".join(parts).encode("utf-8")
    digest = hashlib.sha256(digest_input).hexdigest()[:12]
    return f"scene-{scene.number:02d}-{digest}"


def build_prompt(scene: Scene, story_title: str) -> str:
    if scene.prompt.strip():
        return scene.prompt.strip()
    return f"""Use case: illustration-story
Asset type: one page illustration for a formal children's picture book.
Primary request: create one full-bleed illustration for this story page.

Book: {story_title}
Scene {scene.number}: {scene.title_en or scene.title_zh}

Visual brief:
{scene.description}

Source excerpt:
{scene.source_excerpt}

Style:
Classic children's picture-book illustration, polished composition, expressive character acting, rich environment, gentle cinematic lighting.

Constraints:
No readable text, labels, captions, speech bubbles, borders, or watermark inside the image.
If inscriptions, plaques, tablets, scrolls, or carved stones appear, use abstract decorative marks only.
Generation policy: use Codex built-in image_gen only; do not use Google/Gemini APIs, GOOGLE_API_KEY, baoyu-image-gen, OpenAI Images API, or any provider fallback.
""".strip()


def load_scene_plan(path: Path, story_title: str) -> List[Scene]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise RuntimeError("Scene plan JSON must be a list.")
    scenes: List[Scene] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise RuntimeError(f"Scene item {index} is not an object.")
        number = int(item.get("number") or index)
        references = item.get("references") or []
        if not isinstance(references, list) or not all(
            isinstance(value, str) for value in references
        ):
            raise RuntimeError(f"Scene item {index} references must be a list of IDs.")
        scene = Scene(
            number=number,
            title_zh=str(item.get("title_zh") or item.get("title") or f"第{number}页"),
            title_en=str(item.get("title_en") or f"Page {number}"),
            description=str(item.get("description") or ""),
            narration_zh=str(item.get("narration_zh") or item.get("narration") or ""),
            narration_en=str(item.get("narration_en") or ""),
            source_excerpt=str(item.get("source_excerpt") or item.get("excerpt") or ""),
            prompt=str(item.get("prompt") or ""),
            expected_image=str(item.get("expected_image") or ""),
            references=[value.strip() for value in references],
        )
        scene.prompt = build_prompt(scene, story_title)
        scenes.append(scene)
    return sorted(scenes, key=lambda scene: scene.number)


def finalize_scenes(scenes: Sequence[Scene]) -> None:
    seen_numbers = set()
    seen_images = set()
    for scene in scenes:
        if scene.number in seen_numbers:
            raise RuntimeError(f"Duplicate scene number: {scene.number}")
        seen_numbers.add(scene.number)
        expected = image_name(scene)
        if Path(expected).name != expected or Path(expected).suffix.lower() != ".png":
            raise RuntimeError(f"Unsafe expected image filename: {expected}")
        collision_key = unicodedata.normalize("NFKC", expected).casefold()
        if collision_key in seen_images:
            raise RuntimeError(f"Duplicate expected image filename: {expected}")
        seen_images.add(collision_key)
        if len(scene.references) > MAX_REFERENCES_PER_TASK:
            raise RuntimeError(
                f"Scene {scene.number} has {len(scene.references)} references; "
                f"the hard limit is {MAX_REFERENCES_PER_TASK}."
            )
        normalized_references = []
        seen_references = set()
        for reference_id in scene.references:
            if not REFERENCE_ID_PATTERN.fullmatch(reference_id):
                raise RuntimeError(
                    f"Scene {scene.number} has an unsafe reference ID: {reference_id}"
                )
            collision_key = unicodedata.normalize("NFKC", reference_id).casefold()
            if collision_key in seen_references:
                raise RuntimeError(
                    f"Scene {scene.number} repeats reference ID: {reference_id}"
                )
            seen_references.add(collision_key)
            normalized_references.append(reference_id)
        scene.references = normalized_references
        scene.expected_image = expected
        scene.task_id = scene_task_id(scene)


def scene_plan_data(scenes: Sequence[Scene]) -> List[Dict[str, object]]:
    fields = (
        "number",
        "title_zh",
        "title_en",
        "description",
        "narration_zh",
        "narration_en",
        "source_excerpt",
        "prompt",
        "expected_image",
    )
    result = []
    for scene in scenes:
        item = {field: getattr(scene, field) for field in fields}
        if scene.references:
            item["references"] = list(scene.references)
        result.append(item)
    return result


def scene_plan_sha256(scenes: Sequence[Scene]) -> str:
    encoded = json.dumps(
        scene_plan_data(scenes),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_manifest(
    path: Path,
    allow_legacy: bool = False,
) -> Tuple[Dict[str, Any], List[Scene]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    pages = raw.get("pages")
    if not isinstance(pages, list) or not pages:
        raise RuntimeError(f"Manifest has no usable pages: {path}")
    scenes: List[Scene] = []
    for index, item in enumerate(pages, start=1):
        if not isinstance(item, dict):
            raise RuntimeError(f"Manifest page {index} is not an object.")
        number = int(item.get("number") or index)
        references = item.get("references") or []
        if not isinstance(references, list) or not all(
            isinstance(value, str) for value in references
        ):
            raise RuntimeError(f"Manifest page {index} references must be a list of IDs.")
        scene = Scene(
            number=number,
            title_zh=str(item.get("title_zh") or item.get("title") or f"第{number}页"),
            title_en=str(item.get("title_en") or f"Page {number}"),
            description=str(item.get("description") or ""),
            narration_zh=str(item.get("narration_zh") or item.get("narration") or ""),
            narration_en=str(item.get("narration_en") or ""),
            source_excerpt=str(item.get("source_excerpt") or item.get("excerpt") or ""),
            prompt=str(item.get("prompt") or ""),
            expected_image=str(item.get("expected_image") or ""),
            references=[value.strip() for value in references],
        )
        scenes.append(scene)
    scenes.sort(key=lambda scene: scene.number)
    finalize_scenes(scenes)
    version_value = raw.get("manifest_version", 1)
    try:
        manifest_version = int(version_value)
    except (TypeError, ValueError) as error:
        raise RuntimeError(f"Invalid manifest version: {version_value}") from error
    stored_hash = raw.get("plan_sha256")
    calculated_hash = scene_plan_sha256(scenes)
    if stored_hash is None:
        if manifest_version >= 2:
            raise RuntimeError(
                f"Manifest v{manifest_version} is missing plan_sha256."
            )
        if not allow_legacy:
            raise RuntimeError(
                "Legacy manifest has no plan_sha256. "
                "Rerun with --migrate-legacy-manifest to freeze it explicitly."
            )
    elif not isinstance(stored_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", stored_hash):
        raise RuntimeError(f"Manifest has an invalid plan_sha256: {stored_hash}")
    elif stored_hash != calculated_hash:
        raise RuntimeError(
            f"Manifest plan hash mismatch: expected {stored_hash}, calculated {calculated_hash}"
        )
    has_references = any(scene.references for scene in scenes)
    reference_hash = raw.get("reference_manifest_sha256")
    if has_references and manifest_version < 3:
        raise RuntimeError("Referenced scenes require manifest v3.")
    if has_references and (
        not isinstance(reference_hash, str)
        or not re.fullmatch(r"[0-9a-f]{64}", reference_hash)
    ):
        raise RuntimeError(
            "Referenced manifest v3 is missing a valid reference_manifest_sha256."
        )
    return raw, scenes


def ensure_compatible_existing_plan(
    output_dir: Path,
    scenes: Sequence[Scene],
    allow_legacy: bool = False,
) -> None:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        return
    _manifest, existing_scenes = load_manifest(manifest_path, allow_legacy=allow_legacy)
    if scene_plan_sha256(existing_scenes) == scene_plan_sha256(scenes):
        return
    image_dir = output_dir / "images"
    has_valid_artwork = False
    if image_dir.is_dir():
        for path in image_dir.glob("*.png"):
            valid, _reason, _details = inspect_png(path)
            if valid:
                has_valid_artwork = True
                break
    if has_valid_artwork:
        raise RuntimeError(
            "The output directory contains valid artwork for a different scene plan. "
            "Use a new output directory instead of silently reusing or overwriting it."
        )


def infer_scene_plan(markdown: Dict[str, str], count: int, story_title: str) -> List[Scene]:
    combined = markdown_plain_text(markdown)
    paragraphs = [normalize(p) for p in re.split(r"\n\s*\n", combined) if len(normalize(p)) > 20]
    if not paragraphs:
        raise RuntimeError("Cannot infer scenes: no usable prose paragraphs found.")
    joined = " ".join(paragraphs)
    chunk_size = max(1, len(joined) // count)
    chunks = textwrap.wrap(joined, width=chunk_size, break_long_words=False, replace_whitespace=False)
    chunks = chunks[:count]
    while len(chunks) < count:
        chunks.append(chunks[-1])
    scenes: List[Scene] = []
    for number, chunk in enumerate(chunks, start=1):
        title_zh = f"分镜{number}"
        scene = Scene(
            number=number,
            title_zh=title_zh,
            title_en=f"Scene {number}",
            description=chunk[:220],
            narration_zh=chunk[:42].rstrip("，。,. ") + "。",
            narration_en=f"Scene {number}.",
            source_excerpt=chunk[:700],
            prompt="",
        )
        scene.prompt = build_prompt(scene, story_title)
        scenes.append(scene)
    return scenes


def load_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def load_pdf_font(size: int, language: str, bold: bool = False):
    from PIL import ImageFont

    if language == "zh":
        songti = Path("/System/Library/Fonts/Supplemental/Songti.ttc")
        if songti.exists():
            # Songti.ttc index 0 is Songti SC Black and is too heavy for captions.
            # Use explicit SC weights: Light for body/footer, Regular for titles.
            return ImageFont.truetype(str(songti), size=size, index=6 if bold else 3)

        hiragino = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
        if hiragino.exists():
            return ImageFont.truetype(str(hiragino), size=size, index=0)

    return load_font(size, bold=bold)


def text_width(draw, text: str, font) -> int:
    left, _top, right, _bottom = draw.textbbox((0, 0), text, font=font)
    return right - left


def trim_to_width(draw, text: str, font, max_width: int) -> str:
    ellipsis = "..."
    while text and text_width(draw, text + ellipsis, font) > max_width:
        text = text[:-1]
    return text.rstrip("，,。 ") + ellipsis


def wrap_text(draw, text: str, font, max_width: int, max_lines: Optional[int] = None) -> List[str]:
    lines: List[str] = []
    paragraphs = text.splitlines() or [""]
    for paragraph_index, paragraph in enumerate(paragraphs):
        if not paragraph.strip():
            lines.append("")
            continue
        units = paragraph.split(" ") if re.search(r"\s", paragraph) else list(paragraph)
        current = ""
        for unit_index, unit in enumerate(units):
            candidate = f"{current} {unit}".strip() if re.search(r"\s", paragraph) else current + unit
            if current and text_width(draw, candidate, font) > max_width:
                lines.append(current)
                current = unit
                if max_lines and len(lines) >= max_lines:
                    lines[-1] = trim_to_width(draw, lines[-1], font, max_width)
                    return lines
            else:
                current = candidate
        if current:
            lines.append(current)
            if max_lines and len(lines) >= max_lines:
                has_more_units = unit_index < len(units) - 1
                has_more_paragraphs = any(item.strip() for item in paragraphs[paragraph_index + 1 :])
                if has_more_units or has_more_paragraphs:
                    lines[-1] = trim_to_width(draw, lines[-1], font, max_width)
                return lines
    return lines


def draw_lines(draw, lines: Sequence[str], xy: Tuple[int, int], font, fill, line_gap: int) -> None:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line or " ", font=font)
        y += bbox[3] - bbox[1] + line_gap


def create_placeholder(path: Path, scene: Scene, size: Tuple[int, int]) -> None:
    from PIL import Image, ImageDraw, PngImagePlugin

    if path.is_symlink():
        raise RuntimeError(f"Placeholder target must not be a symlink: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", size, (240, 232, 214))
    draw = ImageDraw.Draw(image)
    font_title = load_font(max(30, size[0] // 30), bold=True)
    font_body = load_font(max(24, size[0] // 48))
    draw.rectangle((40, 40, size[0] - 40, size[1] - 40), outline=(116, 92, 60), width=4)
    draw_lines(draw, [f"{scene.number:02d}. {scene.title_zh}"], (80, 90), font_title, (50, 42, 32), 8)
    draw_lines(draw, wrap_text(draw, scene.narration_zh, font_body, size[0] - 160, 3), (80, 170), font_body, (80, 62, 44), 8)
    draw_lines(draw, wrap_text(draw, scene.narration_en, font_body, size[0] - 160, 3), (80, 320), font_body, (80, 62, 44), 8)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("mufeng_placeholder", "true")
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        image.save(temporary, "PNG", pnginfo=metadata)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def append_progress(progress_path: Path, event: str, **fields: object) -> None:
    if progress_path.is_symlink():
        raise RuntimeError(f"Progress log must not be a symlink: {progress_path}")
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "schema_version": 1,
        "ts": utc_now(),
        "event": event,
        **{key: value for key, value in fields.items() if value is not None},
    }
    encoded = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    flags = os.O_APPEND | os.O_CREAT | os.O_RDWR
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(progress_path, flags, 0o644)
    try:
        prefix = b""
        if os.fstat(descriptor).st_size:
            os.lseek(descriptor, -1, os.SEEK_END)
            if os.read(descriptor, 1) != b"\n":
                prefix = b"\n"
        os.write(descriptor, prefix + encoded)
    finally:
        os.close(descriptor)


def read_progress(progress_path: Path, strict: bool = True) -> List[Dict[str, Any]]:
    if progress_path.is_symlink():
        raise RuntimeError(f"Progress log must not be a symlink: {progress_path}")
    if not progress_path.exists():
        return []
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(progress_path, flags)
    try:
        handle = os.fdopen(descriptor, "r", encoding="utf-8")
        descriptor = -1
        with handle:
            lines = handle.read().splitlines()
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    records: List[Dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            if strict:
                raise RuntimeError(f"Invalid progress JSON at line {line_number}: {error}") from error
            continue
        if isinstance(item, dict):
            records.append(item)
    return records


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def reference_policy() -> Dict[str, object]:
    return {
        "max_references_per_task": MAX_REFERENCES_PER_TASK,
        "upload_format": "JPEG",
        "upload_max_edge": REFERENCE_MAX_EDGE,
        "upload_quality": REFERENCE_JPEG_QUALITY,
        "metadata": "stripped",
        "alpha_background": "white",
        "lock": "sha256-contract",
    }


def reference_library_dir(project_dir: Path) -> Path:
    return project_dir / ".mufeng-storybook" / "references"


def validate_reference_library_path(project_dir: Path) -> Path:
    library = reference_library_dir(project_dir)
    if path_has_symlink_component(library, project_dir):
        raise RuntimeError(f"Reference library must not use symlinks: {library}")
    resolved = library.resolve()
    if not path_is_within(resolved, project_dir):
        raise RuntimeError(f"Reference library resolves outside the project: {resolved}")
    return resolved


def path_has_symlink_component(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def path_has_symlink_below_resolved_root(path: Path, resolved_root: Path) -> bool:
    current = path
    descendants: List[Path] = []
    while True:
        try:
            if current.resolve() == resolved_root:
                return any(item.is_symlink() for item in reversed(descendants))
        except OSError:
            return True
        descendants.append(current)
        if current.parent == current:
            return True
        current = current.parent


def project_local_file(value: str, project_dir: Path, label: str) -> Path:
    raw = Path(value).expanduser()
    candidate = raw if raw.is_absolute() else project_dir / raw
    lexical = Path(os.path.abspath(candidate))
    if lexical.is_symlink():
        raise RuntimeError(f"{label} must not be a symlink: {lexical}")
    resolved = lexical.resolve()
    if not path_is_within(resolved, project_dir):
        raise RuntimeError(f"{label} resolves outside the project directory: {resolved}")
    if path_has_symlink_below_resolved_root(lexical, project_dir):
        raise RuntimeError(f"{label} must not use project-internal symlinks: {lexical}")
    if not resolved.is_file():
        raise RuntimeError(f"{label} does not exist or is not a file: {resolved}")
    return resolved


def inspect_reference_image(path: Path) -> Tuple[bool, str, Dict[str, object]]:
    from PIL import Image

    if path.is_symlink():
        return False, "symlinks are not accepted", {}
    if not path.is_file():
        return False, "file is missing", {}
    before = path.stat()
    if before.st_size <= 0:
        return False, "file is empty", {}
    try:
        with Image.open(path) as image:
            image_format = str(image.format or "").upper()
            frame_count = int(getattr(image, "n_frames", 1))
            if frame_count != 1:
                return False, "animated or multi-frame images are not accepted", {}
            image.verify()
        with Image.open(path) as image:
            image.load()
            width, height = image.size
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            return False, "file changed while it was being validated", {}
        if width < 1 or height < 1:
            return False, "image dimensions are invalid", {}
        digest = sha256_file(path)
        final = path.stat()
        if (before.st_size, before.st_mtime_ns) != (final.st_size, final.st_mtime_ns):
            return False, "file changed while it was being hashed", {}
        return True, "valid reference image", {
            "format": image_format,
            "size_bytes": final.st_size,
            "width": width,
            "height": height,
            "sha256": digest,
        }
    except (OSError, ValueError, Image.DecompressionBombError) as error:
        return False, f"reference image decode failed: {error}", {}


def atomic_copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
    try:
        shutil.copyfile(source, temporary)
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def create_reference_proxy(master: Path, target: Path) -> None:
    from PIL import Image, ImageOps

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
    try:
        with Image.open(master) as source:
            source.load()
            oriented = ImageOps.exif_transpose(source)
            if "A" in oriented.getbands() or "transparency" in oriented.info:
                rgba = oriented.convert("RGBA")
                flattened = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
                flattened.alpha_composite(rgba)
                prepared = flattened.convert("RGB")
            else:
                prepared = oriented.convert("RGB")
            prepared.thumbnail(
                (REFERENCE_MAX_EDGE, REFERENCE_MAX_EDGE),
                Image.Resampling.LANCZOS,
            )
            prepared.save(
                temporary,
                "JPEG",
                quality=REFERENCE_JPEG_QUALITY,
                optimize=True,
                progressive=True,
            )
        valid, reason, details = inspect_reference_image(temporary)
        if not valid:
            raise RuntimeError(f"Generated reference proxy is invalid: {reason}")
        if details.get("format") != "JPEG":
            raise RuntimeError("Generated reference proxy is not JPEG.")
        if max(int(details["width"]), int(details["height"])) > REFERENCE_MAX_EDGE:
            raise RuntimeError("Generated reference proxy exceeds the 1024px limit.")
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def reference_catalog_payload(entries: Sequence[Dict[str, object]]) -> Dict[str, object]:
    return {
        "schema_version": 1,
        "policy": reference_policy(),
        "entries": list(entries),
    }


def validate_reference_entry(
    entry: Dict[str, object],
    project_dir: Path,
) -> Dict[str, object]:
    reference_id = str(entry.get("id") or "")
    if not REFERENCE_ID_PATTERN.fullmatch(reference_id):
        raise RuntimeError(f"Invalid reference ID in catalog: {reference_id}")
    role = str(entry.get("role") or "")
    if role not in REFERENCE_ROLES:
        raise RuntimeError(f"Invalid role for reference {reference_id}: {role}")
    library = reference_library_dir(project_dir).resolve()
    for prefix in ("master", "upload"):
        path_value = entry.get(f"{prefix}_path")
        if not isinstance(path_value, str) or not path_value:
            raise RuntimeError(f"Reference {reference_id} has no {prefix}_path.")
        candidate = Path(os.path.abspath(project_dir / path_value))
        if (
            not path_is_within(candidate, library)
            or path_has_symlink_component(candidate, project_dir)
        ):
            raise RuntimeError(
                f"Reference {reference_id} has an unsafe {prefix}_path: {candidate}"
            )
        valid, reason, details = inspect_reference_image(candidate)
        if not valid:
            raise RuntimeError(f"Reference {reference_id} {prefix} is invalid: {reason}")
        for field_name in ("sha256", "size_bytes", "width", "height"):
            expected = entry.get(f"{prefix}_{field_name}")
            if expected != details[field_name]:
                raise RuntimeError(
                    f"Reference {reference_id} {prefix}_{field_name} does not match "
                    "the hash-locked catalog."
                )
        if prefix == "upload":
            if details.get("format") != "JPEG":
                raise RuntimeError(f"Reference {reference_id} upload proxy is not JPEG.")
            if max(int(details["width"]), int(details["height"])) > REFERENCE_MAX_EDGE:
                raise RuntimeError(
                    f"Reference {reference_id} upload proxy exceeds {REFERENCE_MAX_EDGE}px."
                )
    return entry


def load_project_reference_catalog(
    project_dir: Path,
    required: bool = False,
) -> Dict[str, Dict[str, object]]:
    path = reference_library_dir(project_dir) / "catalog.json"
    if not path.is_file():
        if required:
            raise RuntimeError(f"Missing project reference catalog: {path}")
        return {}
    if path.is_symlink():
        raise RuntimeError(f"Project reference catalog must not be a symlink: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    entries = raw.get("entries") if isinstance(raw, dict) else None
    if not isinstance(entries, list):
        raise RuntimeError(f"Invalid project reference catalog: {path}")
    payload = reference_catalog_payload(entries)
    if raw.get("catalog_sha256") != canonical_sha256(payload):
        raise RuntimeError("Project reference catalog hash mismatch.")
    result: Dict[str, Dict[str, object]] = {}
    collision_keys = set()
    for raw_entry in entries:
        if not isinstance(raw_entry, dict):
            raise RuntimeError("Project reference catalog contains a non-object entry.")
        entry = validate_reference_entry(raw_entry, project_dir)
        reference_id = str(entry["id"])
        collision_key = unicodedata.normalize("NFKC", reference_id).casefold()
        if collision_key in collision_keys:
            raise RuntimeError(f"Duplicate reference ID in catalog: {reference_id}")
        collision_keys.add(collision_key)
        result[reference_id] = entry
    return result


def write_project_reference_catalog(
    project_dir: Path,
    catalog: Dict[str, Dict[str, object]],
) -> None:
    validate_reference_library_path(project_dir)
    entries = [catalog[key] for key in sorted(catalog)]
    payload = reference_catalog_payload(entries)
    document = {
        **payload,
        "catalog_sha256": canonical_sha256(payload),
    }
    path = reference_library_dir(project_dir) / "catalog.json"
    if path.is_symlink():
        raise RuntimeError(f"Project reference catalog must not be a symlink: {path}")
    atomic_write_text(
        path,
        json.dumps(document, ensure_ascii=False, indent=2),
    )


def master_extension(image_format: str) -> str:
    extensions = {
        "JPEG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
    }
    if image_format not in extensions:
        raise RuntimeError(
            f"Unsupported reference format {image_format}; use PNG, JPEG, or WebP."
        )
    return extensions[image_format]


def parse_reference_spec(path: Path, project_dir: Path) -> List[Dict[str, str]]:
    if path.is_symlink():
        raise RuntimeError(f"Reference spec must not be a symlink: {path}")
    if not path.is_file():
        raise RuntimeError(f"Reference spec does not exist: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        unknown_top_level = set(raw) - {"schema_version", "references"}
        if unknown_top_level:
            raise RuntimeError(
                f"Reference spec has unknown fields: {sorted(unknown_top_level)}"
            )
        if raw.get("schema_version", 1) != 1:
            raise RuntimeError("Reference spec schema_version must be 1.")
    items = raw.get("references") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise RuntimeError("Reference spec must be a list or an object with references.")
    result: List[Dict[str, str]] = []
    seen = set()
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise RuntimeError(f"Reference spec item {index} is not an object.")
        unknown = set(item) - {"id", "path", "role"}
        if unknown:
            raise RuntimeError(
                f"Reference spec item {index} has unknown fields: {sorted(unknown)}"
            )
        reference_id = str(item.get("id") or "")
        if not REFERENCE_ID_PATTERN.fullmatch(reference_id):
            raise RuntimeError(f"Reference spec item {index} has an unsafe ID.")
        collision_key = unicodedata.normalize("NFKC", reference_id).casefold()
        if collision_key in seen:
            raise RuntimeError(f"Reference spec repeats ID: {reference_id}")
        seen.add(collision_key)
        role = str(item.get("role") or "continuity")
        if role not in REFERENCE_ROLES:
            raise RuntimeError(f"Reference {reference_id} has unsupported role: {role}")
        source_value = item.get("path")
        if not isinstance(source_value, str) or not source_value:
            raise RuntimeError(f"Reference {reference_id} has no path.")
        source = project_local_file(source_value, project_dir, f"Reference {reference_id}")
        result.append(
            {
                "id": reference_id,
                "role": role,
                "source": str(source),
            }
        )
    return result


def prepare_project_references(
    project_dir: Path,
    spec_path: Optional[Path],
) -> Dict[str, Dict[str, object]]:
    validate_reference_library_path(project_dir)
    catalog = load_project_reference_catalog(project_dir)
    if spec_path is None:
        return catalog
    spec = project_local_file(str(spec_path), project_dir, "Reference spec")
    for item in parse_reference_spec(spec, project_dir):
        reference_id = item["id"]
        source = Path(item["source"])
        valid, reason, source_details = inspect_reference_image(source)
        if not valid:
            raise RuntimeError(f"Reference {reference_id} source is invalid: {reason}")
        source_hash = str(source_details["sha256"])
        existing = catalog.get(reference_id)
        if existing is not None:
            if existing.get("master_sha256") != source_hash:
                raise RuntimeError(
                    f"Reference ID {reference_id} is hash-locked to different source bytes. "
                    "Use a new reference ID for a changed master."
                )
            if existing.get("role") != item["role"]:
                raise RuntimeError(
                    f"Reference ID {reference_id} is already locked to role "
                    f"{existing.get('role')}."
                )
            continue

        library = reference_library_dir(project_dir)
        stem = f"{reference_id}-{source_hash[:12]}"
        master_path = library / "master" / f"{stem}{master_extension(str(source_details['format']))}"
        upload_path = library / "upload" / f"{stem}.jpg"
        if master_path.exists() or upload_path.exists():
            raise RuntimeError(
                f"Reference asset path already exists without a catalog entry: {stem}"
            )
        created_paths: List[Path] = []
        try:
            atomic_copy_file(source, master_path)
            created_paths.append(master_path)
            master_valid, master_reason, master_details = inspect_reference_image(master_path)
            if not master_valid or master_details.get("sha256") != source_hash:
                raise RuntimeError(
                    f"Copied master for {reference_id} failed validation: {master_reason}"
                )
            create_reference_proxy(master_path, upload_path)
            created_paths.append(upload_path)
            upload_valid, upload_reason, upload_details = inspect_reference_image(upload_path)
            if not upload_valid:
                raise RuntimeError(
                    f"Upload proxy for {reference_id} failed validation: {upload_reason}"
                )
            entry: Dict[str, object] = {
                "id": reference_id,
                "role": item["role"],
                "source_path": str(source.relative_to(project_dir)),
                "master_path": str(master_path.relative_to(project_dir)),
                "master_sha256": master_details["sha256"],
                "master_size_bytes": master_details["size_bytes"],
                "master_width": master_details["width"],
                "master_height": master_details["height"],
                "upload_path": str(upload_path.relative_to(project_dir)),
                "upload_sha256": upload_details["sha256"],
                "upload_size_bytes": upload_details["size_bytes"],
                "upload_width": upload_details["width"],
                "upload_height": upload_details["height"],
            }
            catalog[reference_id] = validate_reference_entry(entry, project_dir)
            write_project_reference_catalog(project_dir, catalog)
        except Exception:
            catalog.pop(reference_id, None)
            for created_path in reversed(created_paths):
                if created_path.is_file() and not created_path.is_symlink():
                    created_path.unlink()
            raise
    return catalog


def validate_scene_references(
    scenes: Sequence[Scene],
    catalog: Dict[str, Dict[str, object]],
) -> None:
    for scene in scenes:
        for reference_id in scene.references:
            if reference_id not in catalog:
                raise RuntimeError(
                    f"Scene {scene.number} references unknown ID {reference_id}. "
                    "Add it to --reference-spec before freezing the plan."
                )


def reference_snapshot_payload(
    project_dir: Path,
    entries: Sequence[Dict[str, object]],
) -> Dict[str, object]:
    return {
        "schema_version": 1,
        "project_dir": str(project_dir),
        "policy": reference_policy(),
        "entries": list(entries),
    }


def write_reference_snapshot(
    output_dir: Path,
    project_dir: Path,
    scenes: Sequence[Scene],
    catalog: Dict[str, Dict[str, object]],
) -> Tuple[Dict[str, Dict[str, object]], str]:
    used_ids = sorted({reference_id for scene in scenes for reference_id in scene.references})
    if not used_ids:
        return {}, ""
    selected = {reference_id: catalog[reference_id] for reference_id in used_ids}
    payload = reference_snapshot_payload(
        project_dir,
        [selected[reference_id] for reference_id in used_ids],
    )
    snapshot_hash = canonical_sha256(payload)
    path = output_dir / REFERENCE_MANIFEST_NAME
    if path.is_symlink():
        raise RuntimeError(f"Reference snapshot must not be a symlink: {path}")
    manifest_path = output_dir / "manifest.json"
    if manifest_path.is_file() and not manifest_path.is_symlink():
        existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        existing_manifest_hash = str(
            existing_manifest.get("reference_manifest_sha256") or ""
        )
        if existing_manifest_hash and existing_manifest_hash != snapshot_hash:
            raise RuntimeError(
                "The output directory is frozen to different reference bytes. "
                "Use a new output directory instead of rebinding reference IDs."
            )
    if path.is_file():
        existing_raw = json.loads(path.read_text(encoding="utf-8"))
        existing_hash = str(existing_raw.get("snapshot_sha256") or "")
        _existing, verified_hash, _project = load_reference_snapshot(
            output_dir,
            expected_hash=existing_hash,
            required=True,
        )
        if verified_hash != snapshot_hash:
            raise RuntimeError(
                "The output directory already has a different frozen reference "
                "snapshot. Use a new output directory."
            )
    atomic_write_text(
        path,
        json.dumps(
            {
                **payload,
                "snapshot_sha256": snapshot_hash,
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    return selected, snapshot_hash


def load_reference_snapshot(
    output_dir: Path,
    expected_hash: str = "",
    required: bool = False,
) -> Tuple[Dict[str, Dict[str, object]], str, Optional[Path]]:
    path = output_dir / REFERENCE_MANIFEST_NAME
    if not required and not expected_hash:
        return {}, "", None
    if not path.is_file():
        if required or expected_hash:
            raise RuntimeError(f"Missing frozen reference snapshot: {path}")
        return {}, "", None
    if path.is_symlink():
        raise RuntimeError(f"Reference snapshot must not be a symlink: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    entries = raw.get("entries") if isinstance(raw, dict) else None
    project_value = raw.get("project_dir") if isinstance(raw, dict) else None
    if not isinstance(entries, list) or not isinstance(project_value, str):
        raise RuntimeError(f"Invalid reference snapshot: {path}")
    project_dir = validate_project_dir(Path(project_value))
    if not path_is_within(output_dir.resolve(), project_dir):
        raise RuntimeError("Reference snapshot project does not contain the output directory.")
    payload = reference_snapshot_payload(project_dir, entries)
    snapshot_hash = canonical_sha256(payload)
    if raw.get("snapshot_sha256") != snapshot_hash:
        raise RuntimeError("Frozen reference snapshot hash mismatch.")
    if expected_hash and expected_hash != snapshot_hash:
        raise RuntimeError("Manifest and reference snapshot hashes differ.")
    result: Dict[str, Dict[str, object]] = {}
    collision_keys = set()
    for raw_entry in entries:
        if not isinstance(raw_entry, dict):
            raise RuntimeError("Reference snapshot contains a non-object entry.")
        entry = validate_reference_entry(raw_entry, project_dir)
        reference_id = str(entry["id"])
        collision_key = unicodedata.normalize("NFKC", reference_id).casefold()
        if collision_key in collision_keys:
            raise RuntimeError(f"Duplicate reference ID in snapshot: {reference_id}")
        collision_keys.add(collision_key)
        result[reference_id] = entry
    return result, snapshot_hash, project_dir


def task_reference_records(
    scene: Scene,
    catalog: Dict[str, Dict[str, object]],
    project_dir: Optional[Path],
) -> List[Dict[str, object]]:
    if scene.references and project_dir is None:
        raise RuntimeError("Referenced scenes require a frozen project directory.")
    records = []
    for reference_id in scene.references:
        entry = catalog[reference_id]
        upload_path = (project_dir / str(entry["upload_path"])).resolve()
        records.append(
            {
                "id": reference_id,
                "role": entry["role"],
                "path": str(upload_path),
                "sha256": entry["upload_sha256"],
                "size_bytes": entry["upload_size_bytes"],
                "width": entry["upload_width"],
                "height": entry["upload_height"],
            }
        )
    return records


def inspect_png(path: Path, allow_placeholder: bool = False) -> Tuple[bool, str, Dict[str, object]]:
    from PIL import Image

    if path.is_symlink():
        return False, "symlinks are not accepted", {}
    if not path.is_file():
        return False, "file is missing", {}
    before = path.stat()
    if before.st_size <= 8:
        return False, "file is empty or too small", {}
    try:
        with path.open("rb") as handle:
            if handle.read(8) != b"\x89PNG\r\n\x1a\n":
                return False, "PNG signature is missing", {}
        with Image.open(path) as image:
            if image.format != "PNG":
                return False, f"decoded format is {image.format}, not PNG", {}
            placeholder = str(image.info.get("mufeng_placeholder", "")).lower() == "true"
            image.verify()
        with Image.open(path) as image:
            image.load()
            width, height = image.size
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            return False, "file changed while it was being validated", {}
        if width < 1 or height < 1:
            return False, "image dimensions are invalid", {}
        if placeholder and not allow_placeholder:
            return False, "dry-run placeholder is not final artwork", {}
        digest = sha256_file(path)
        final = path.stat()
        if (before.st_size, before.st_mtime_ns) != (final.st_size, final.st_mtime_ns):
            return False, "file changed while it was being hashed", {}
        return True, "valid PNG", {
            "size_bytes": after.st_size,
            "width": width,
            "height": height,
            "sha256": digest,
            "placeholder": placeholder,
        }
    except (OSError, ValueError, Image.DecompressionBombError) as error:
        return False, f"PNG decode failed: {error}", {}


def inspect_scene_images(
    scenes: Sequence[Scene],
    image_dir: Path,
    allow_placeholder: bool = False,
) -> List[ImageInspection]:
    inspections: List[ImageInspection] = []
    for scene in scenes:
        path = image_dir / image_name(scene)
        scene.image_path = str(path)
        valid, reason, details = inspect_png(path, allow_placeholder=allow_placeholder)
        status = (
            "placeholder"
            if valid and bool(details.get("placeholder"))
            else "complete"
            if valid
            else "pending"
        )
        inspections.append(
            ImageInspection(
                task_id=scene.task_id,
                scene_number=scene.number,
                expected_image=image_name(scene),
                image_path=str(path),
                status=status,
                reason=reason,
                size_bytes=int(details.get("size_bytes", 0)),
                width=int(details.get("width", 0)),
                height=int(details.get("height", 0)),
                sha256=str(details.get("sha256", "")),
            )
        )
    return inspections


def validate_generation_config(concurrency: int, mapping_mode: str) -> None:
    if concurrency < 1 or concurrency > 4:
        raise RuntimeError("--concurrency must be between 1 and 4.")
    if mapping_mode not in MAPPING_MODES:
        raise RuntimeError(f"Unsupported mapping mode: {mapping_mode}")
    if concurrency > 1 and mapping_mode == "directory-diff":
        raise RuntimeError(
            "Parallel generation cannot use a shared directory diff. "
            "Use --mapping-mode per-call-path or isolated-worker-dir, or set --concurrency 1."
        )


def acquire_generation_plan_lock(output_dir: Path) -> int:
    import fcntl

    output_dir.mkdir(parents=True, exist_ok=True)
    lock_path = output_dir / ".generation_tasks.lock"
    if lock_path.is_symlink():
        raise RuntimeError(f"Generation-plan lock must not be a symlink: {lock_path}")
    flags = os.O_CREAT | os.O_RDWR
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(lock_path, flags, 0o644)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
    except Exception:
        os.close(descriptor)
        raise
    return descriptor


def release_generation_plan_lock(descriptor: int) -> None:
    import fcntl

    try:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def update_generation_plan_statuses(
    plan: Dict[str, Any],
    inspections: Sequence[ImageInspection],
    add_updated_at: bool = False,
) -> None:
    by_task = {inspection.task_id: inspection for inspection in inspections}
    for task in plan["tasks"]:
        inspection = by_task[str(task["task_id"])]
        task["status"] = inspection.status
        task["status_reason"] = inspection.reason
        task["image"] = (
            {
                "size_bytes": inspection.size_bytes,
                "width": inspection.width,
                "height": inspection.height,
                "sha256": inspection.sha256,
            }
            if inspection.status == "complete"
            else None
        )
    complete = sum(task["status"] == "complete" for task in plan["tasks"])
    if add_updated_at:
        plan["updated_at"] = utc_now()
    plan["summary"].update(
        {
            "total": len(plan["tasks"]),
            "complete": complete,
            "pending": len(plan["tasks"]) - complete,
            "planned_reference_payload_bytes_per_pending_pass": sum(
                int(task.get("reference_payload_bytes") or 0)
                for task in plan["tasks"]
                if task["status"] != "complete"
            ),
        }
    )


def write_generation_plan(
    output_dir: Path,
    scenes: Sequence[Scene],
    inspections: Sequence[ImageInspection],
    workflow_mode: str,
    concurrency: int,
    mapping_mode: str,
    reference_catalog: Optional[Dict[str, Dict[str, object]]] = None,
    reference_snapshot_sha256: str = "",
    reference_project_dir: Optional[Path] = None,
) -> Dict[str, object]:
    validate_generation_config(concurrency, mapping_mode)
    catalog = reference_catalog or {}
    status_by_task = {inspection.task_id: inspection for inspection in inspections}
    tasks = []
    for scene in scenes:
        inspection = status_by_task[scene.task_id]
        references = task_reference_records(scene, catalog, reference_project_dir)
        payload_bytes = sum(int(item["size_bytes"]) for item in references)
        tasks.append(
            {
                "task_id": scene.task_id,
                "scene_number": scene.number,
                "title_zh": scene.title_zh,
                "title_en": scene.title_en,
                "expected_image": image_name(scene),
                "prompt_sha256": hashlib.sha256(scene.prompt.encode("utf-8")).hexdigest(),
                "prompt": scene.prompt,
                "references": references,
                "referenced_image_paths": [item["path"] for item in references],
                "reference_count": len(references),
                "reference_payload_bytes": payload_bytes,
                "status": inspection.status,
                "status_reason": inspection.reason,
                "image": {
                    "size_bytes": inspection.size_bytes,
                    "width": inspection.width,
                    "height": inspection.height,
                    "sha256": inspection.sha256,
                }
                if inspection.status == "complete"
                else None,
            }
        )
    complete = sum(task["status"] == "complete" for task in tasks)
    planned_payload = sum(
        int(task["reference_payload_bytes"])
        for task in tasks
        if task["status"] != "complete"
    )
    plan: Dict[str, object] = {
        "schema_version": 2 if reference_snapshot_sha256 else 1,
        "created_at": utc_now(),
        "workflow_mode": workflow_mode,
        "plan_sha256": scene_plan_sha256(scenes),
        "reference_snapshot_sha256": reference_snapshot_sha256 or None,
        "reference_policy": reference_policy(),
        "concurrency": concurrency,
        "mapping_mode": mapping_mode,
        "summary": {
            "total": len(tasks),
            "complete": complete,
            "pending": len(tasks) - complete,
            "planned_reference_payload_bytes_per_pending_pass": planned_payload,
            "payload_note": (
                "Local reference-file bytes only; not measured upload traffic. "
                "Retries and client transport overhead are excluded."
            ),
        },
        "tasks": tasks,
    }
    descriptor = acquire_generation_plan_lock(output_dir)
    try:
        fresh_inspections = inspect_scene_images(
            scenes,
            output_dir / "images",
            allow_placeholder=any(
                inspection.status == "placeholder" for inspection in inspections
            ),
        )
        update_generation_plan_statuses(plan, fresh_inspections)
        atomic_write_text(
            output_dir / GENERATION_PLAN_NAME,
            json.dumps(plan, ensure_ascii=False, indent=2),
        )
    finally:
        release_generation_plan_lock(descriptor)
    return plan


def load_generation_plan(output_dir: Path) -> Dict[str, Any]:
    path = output_dir / GENERATION_PLAN_NAME
    if not path.is_file():
        raise RuntimeError(f"Missing generation plan: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("tasks"), list):
        raise RuntimeError(f"Invalid generation plan: {path}")
    schema_value = raw.get("schema_version", 1)
    if isinstance(schema_value, bool) or not isinstance(schema_value, int):
        raise RuntimeError("Generation plan schema_version must be an integer.")
    if schema_value not in (1, 2):
        raise RuntimeError(f"Unsupported generation plan schema: {schema_value}")
    concurrency = raw.get("concurrency")
    mapping_mode = raw.get("mapping_mode")
    if isinstance(concurrency, bool) or not isinstance(concurrency, int):
        raise RuntimeError("Generation plan concurrency must be an integer.")
    if not isinstance(mapping_mode, str):
        raise RuntimeError("Generation plan mapping_mode must be a string.")
    validate_generation_config(concurrency, mapping_mode)
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Missing manifest for generation plan: {manifest_path}")
    manifest, scenes = load_manifest(manifest_path)
    expected_workflow = str(manifest.get("workflow_mode") or "final")
    if raw.get("workflow_mode") != expected_workflow:
        raise RuntimeError("Generation plan workflow mode differs from the manifest.")
    if raw.get("plan_sha256") != manifest.get("plan_sha256"):
        raise RuntimeError(
            "Generation plan and manifest hashes differ. "
            "Regenerate the plan before importing artwork."
        )
    schema_version = schema_value
    if (
        schema_version >= 2
        and raw.get("reference_policy") != reference_policy()
    ) or (
        schema_version < 2
        and raw.get("reference_policy") not in (None, reference_policy())
    ):
        raise RuntimeError("Generation plan reference policy has been altered.")
    reference_hash = str(manifest.get("reference_manifest_sha256") or "")
    catalog, snapshot_hash, project_dir = load_reference_snapshot(
        output_dir,
        expected_hash=reference_hash,
        required=any(scene.references for scene in scenes),
    )
    if raw.get("reference_snapshot_sha256") not in (snapshot_hash, None):
        raise RuntimeError("Generation plan and reference snapshot hashes differ.")
    if snapshot_hash and raw.get("reference_snapshot_sha256") != snapshot_hash:
        raise RuntimeError("Generation plan is missing its frozen reference snapshot hash.")
    validate_scene_references(scenes, catalog)
    expected_tasks = {}
    for scene in scenes:
        references = task_reference_records(scene, catalog, project_dir)
        expected_tasks[scene.task_id] = {
            "scene_number": scene.number,
            "expected_image": image_name(scene),
            "prompt_sha256": hashlib.sha256(scene.prompt.encode("utf-8")).hexdigest(),
            "prompt": scene.prompt,
            "references": references,
            "referenced_image_paths": [item["path"] for item in references],
            "reference_count": len(references),
            "reference_payload_bytes": sum(
                int(item["size_bytes"]) for item in references
            ),
        }
    if len(raw["tasks"]) != len(expected_tasks):
        raise RuntimeError("Generation task count does not match the manifest.")
    actual_inspections = {
        inspection.task_id: inspection
        for inspection in inspect_scene_images(
            scenes,
            output_dir / "images",
            allow_placeholder=True,
        )
    }
    seen_task_ids = set()
    for task in raw["tasks"]:
        if not isinstance(task, dict):
            raise RuntimeError("Generation plan contains a non-object task.")
        task_id = str(task.get("task_id") or "")
        if task_id in seen_task_ids or task_id not in expected_tasks:
            raise RuntimeError(f"Generation plan has an unknown or duplicate task: {task_id}")
        seen_task_ids.add(task_id)
        expected = expected_tasks[task_id]
        status = task.get("status")
        if status not in {"pending", "complete", "placeholder"}:
            raise RuntimeError(
                f"Generation task {task_id} has an invalid status: {status}"
            )
        actual_inspection = actual_inspections[task_id]
        if status == "complete":
            if actual_inspection.status != "complete":
                raise RuntimeError(
                    f"Generation task {task_id} claims complete but its PNG is invalid."
                )
            expected_image_record = {
                "size_bytes": actual_inspection.size_bytes,
                "width": actual_inspection.width,
                "height": actual_inspection.height,
                "sha256": actual_inspection.sha256,
            }
            if task.get("image") != expected_image_record:
                raise RuntimeError(
                    f"Generation task {task_id} image metadata differs from its PNG."
                )
        elif status == "placeholder" and actual_inspection.status != "placeholder":
            raise RuntimeError(
                f"Generation task {task_id} claims placeholder but its PNG differs."
            )
        for field_name in (
            "scene_number",
            "expected_image",
            "prompt_sha256",
            "prompt",
            "references",
            "referenced_image_paths",
            "reference_count",
            "reference_payload_bytes",
        ):
            actual = task.get(field_name)
            if (
                schema_version == 1
                and not expected["references"]
                and field_name
                in {
                    "references",
                    "referenced_image_paths",
                    "reference_count",
                    "reference_payload_bytes",
                }
                and field_name not in task
            ):
                actual = expected[field_name]
            if actual != expected[field_name]:
                raise RuntimeError(
                    f"Generation task {task_id} field {field_name} differs from the manifest."
                )
    summary = raw.get("summary")
    if not isinstance(summary, dict):
        raise RuntimeError("Generation plan has no valid summary.")
    expected_total = len(raw["tasks"])
    expected_complete = sum(
        task.get("status") == "complete" for task in raw["tasks"]
    )
    expected_pending = expected_total - expected_complete
    for field_name, expected_value in (
        ("total", expected_total),
        ("complete", expected_complete),
        ("pending", expected_pending),
    ):
        if summary.get(field_name) != expected_value:
            raise RuntimeError(
                f"Generation plan summary {field_name} has been altered."
            )
    expected_payload = sum(
        int(task.get("reference_payload_bytes") or 0)
        for task in raw["tasks"]
        if task.get("status") != "complete"
    )
    stored_payload = summary.get("planned_reference_payload_bytes_per_pending_pass")
    if (
        schema_version >= 2
        and stored_payload != expected_payload
    ) or (
        schema_version < 2
        and stored_payload is not None
        and stored_payload != expected_payload
    ):
        raise RuntimeError("Generation plan reference payload summary has been altered.")
    return raw


def refresh_generation_plan_status(output_dir: Path) -> Dict[str, Any]:
    descriptor = acquire_generation_plan_lock(output_dir)
    try:
        plan = load_generation_plan(output_dir)
        _manifest, scenes = load_manifest(output_dir / "manifest.json")
        inspections = inspect_scene_images(
            scenes,
            output_dir / "images",
            allow_placeholder=True,
        )
        update_generation_plan_statuses(plan, inspections, add_updated_at=True)
        atomic_write_text(
            output_dir / GENERATION_PLAN_NAME,
            json.dumps(plan, ensure_ascii=False, indent=2),
        )
        return plan
    finally:
        release_generation_plan_lock(descriptor)


def generation_root() -> Path:
    codex_root = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
    return (codex_root / "generated_images").resolve()


def find_generation_task(plan: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    matches = [task for task in plan["tasks"] if task.get("task_id") == task_id]
    if len(matches) != 1:
        raise RuntimeError(f"Unknown or duplicate task ID: {task_id}")
    return matches[0]


def latest_generation_start(progress_path: Path, task_id: str) -> Optional[datetime]:
    for record in reversed(read_progress(progress_path, strict=False)):
        if record.get("task_id") != task_id or record.get("event") != "generation_started":
            continue
        timestamp = str(record.get("ts", "")).replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(timestamp)
        except ValueError:
            return None
    return None


def record_generation_event(
    output_dir: Path,
    event: str,
    task_id: str,
    detail: str = "",
) -> None:
    if event not in PROGRESS_EVENTS:
        raise RuntimeError(f"Unsupported progress event: {event}")
    plan = load_generation_plan(output_dir)
    task = find_generation_task(plan, task_id)
    if event == "generation_started":
        target = output_dir / "images" / str(task["expected_image"])
        target_valid, _target_reason, _target_details = inspect_png(target)
        if target_valid:
            refresh_generation_plan_status(output_dir)
            raise RuntimeError(
                f"Task {task_id} already has a valid project PNG; skip ImageGen."
            )
    fields: Dict[str, object] = {
        "task_id": task_id,
        "scene_number": task.get("scene_number"),
        "expected_image": task.get("expected_image"),
        "reference_count": task.get("reference_count"),
        "local_reference_payload_bytes": task.get("reference_payload_bytes"),
        "detail": detail or None,
    }
    if event != "generation_started":
        started = latest_generation_start(output_dir / PROGRESS_LOG_NAME, task_id)
        if started is not None:
            elapsed = datetime.now(timezone.utc) - started
            fields["elapsed_ms"] = max(0, round(elapsed.total_seconds() * 1000))
    append_progress(output_dir / PROGRESS_LOG_NAME, event, **fields)


def import_generated_image(
    output_dir: Path,
    task_id: str,
    source_path: Path,
    generated_root: Optional[Path] = None,
) -> ImageInspection:
    started = time.perf_counter()
    plan = load_generation_plan(output_dir)
    task = find_generation_task(plan, task_id)
    output_root = output_dir.resolve()
    image_dir = output_root / "images"
    if image_dir.is_symlink():
        raise RuntimeError(f"Project image directory must not be a symlink: {image_dir}")
    image_dir.mkdir(parents=True, exist_ok=True)
    target = image_dir / str(task["expected_image"])
    if not path_is_within(target, image_dir):
        raise RuntimeError(f"Unsafe target image path: {target}")

    target_valid, target_reason, target_details = inspect_png(target)
    if target_valid:
        refresh_generation_plan_status(output_dir)
        inspection = ImageInspection(
            task_id=task_id,
            scene_number=int(task["scene_number"]),
            expected_image=str(task["expected_image"]),
            image_path=str(target),
            status="complete",
            reason="valid existing image skipped",
            size_bytes=int(target_details["size_bytes"]),
            width=int(target_details["width"]),
            height=int(target_details["height"]),
            sha256=str(target_details["sha256"]),
        )
        append_progress(
            output_dir / PROGRESS_LOG_NAME,
            "image_skipped_existing",
            task_id=task_id,
            scene_number=task.get("scene_number"),
            expected_image=task.get("expected_image"),
            sha256=inspection.sha256,
        )
        return inspection

    root = (generated_root or generation_root()).resolve()
    source_input = source_path.expanduser()
    if not source_input.is_absolute():
        source_input = (Path.cwd() / source_input).absolute()
    if source_input.is_symlink():
        raise RuntimeError(f"Generated source PNG must not be a symlink: {source_input}")
    source = source_input.resolve()
    if not path_is_within(source, root):
        raise RuntimeError(f"Source PNG is outside the Codex generated-images directory: {source}")

    source_valid, source_reason, source_details = inspect_png(source_input)
    if not source_valid:
        raise RuntimeError(f"Invalid generated source PNG: {source_reason}")

    staging_dir = image_dir / ".staging"
    if staging_dir.is_symlink():
        raise RuntimeError(f"Project staging directory must not be a symlink: {staging_dir}")
    staging_dir.mkdir(parents=True, exist_ok=True)
    staging = staging_dir / f"{task_id}-{uuid.uuid4().hex}.png"
    try:
        shutil.copyfile(source, staging)
        staged_valid, staged_reason, staged_details = inspect_png(staging)
        if not staged_valid:
            raise RuntimeError(f"Invalid staged PNG: {staged_reason}")
        if staged_details["sha256"] != source_details["sha256"]:
            raise RuntimeError("Staged PNG hash does not match its generated source.")

        target_valid, _target_reason, target_details = inspect_png(target)
        if target_valid:
            staging.unlink()
            refresh_generation_plan_status(output_dir)
            append_progress(
                output_dir / PROGRESS_LOG_NAME,
                "image_skipped_existing",
                task_id=task_id,
                scene_number=task.get("scene_number"),
                expected_image=task.get("expected_image"),
                sha256=target_details["sha256"],
            )
            return ImageInspection(
                task_id=task_id,
                scene_number=int(task["scene_number"]),
                expected_image=str(task["expected_image"]),
                image_path=str(target),
                status="complete",
                reason="valid existing image won concurrent import race",
                size_bytes=int(target_details["size_bytes"]),
                width=int(target_details["width"]),
                height=int(target_details["height"]),
                sha256=str(target_details["sha256"]),
            )

        os.replace(staging, target)
        final_valid, final_reason, final_details = inspect_png(target)
        if not final_valid:
            raise RuntimeError(f"Imported project PNG failed validation: {final_reason}")
        if final_details["sha256"] != source_details["sha256"]:
            raise RuntimeError("Imported project PNG hash does not match its generated source.")
        inspection = ImageInspection(
            task_id=task_id,
            scene_number=int(task["scene_number"]),
            expected_image=str(task["expected_image"]),
            image_path=str(target),
            status="complete",
            reason="generated image imported",
            size_bytes=int(final_details["size_bytes"]),
            width=int(final_details["width"]),
            height=int(final_details["height"]),
            sha256=str(final_details["sha256"]),
        )
        refresh_generation_plan_status(output_dir)
        append_progress(
            output_dir / PROGRESS_LOG_NAME,
            "image_imported",
            task_id=task_id,
            scene_number=task.get("scene_number"),
            expected_image=task.get("expected_image"),
            source=str(source),
            size_bytes=inspection.size_bytes,
            width=inspection.width,
            height=inspection.height,
            sha256=inspection.sha256,
            elapsed_ms=round((time.perf_counter() - started) * 1000),
        )
        return inspection
    except Exception:
        if staging.exists():
            staging.unlink()
        append_progress(
            output_dir / PROGRESS_LOG_NAME,
            "image_import_failed",
            task_id=task_id,
            scene_number=task.get("scene_number"),
            expected_image=task.get("expected_image"),
            source=str(source),
            previous_target_status=target_reason,
            elapsed_ms=round((time.perf_counter() - started) * 1000),
        )
        raise


def archive_rejected_attempt(
    output_dir: Path,
    task_id: str,
    source_path: Path,
    detail: str = "",
    generated_root: Optional[Path] = None,
) -> Dict[str, object]:
    started = time.perf_counter()
    plan = load_generation_plan(output_dir)
    task = find_generation_task(plan, task_id)
    root = (generated_root or generation_root()).resolve()
    source_input = source_path.expanduser()
    if not source_input.is_absolute():
        source_input = (Path.cwd() / source_input).absolute()
    if source_input.is_symlink():
        raise RuntimeError(f"Rejected source PNG must not be a symlink: {source_input}")
    source = source_input.resolve()
    if not path_is_within(source, root):
        raise RuntimeError(
            f"Rejected source PNG is outside the Codex generated-images directory: {source}"
        )
    source_valid, source_reason, source_details = inspect_png(source_input)
    if not source_valid:
        raise RuntimeError(f"Invalid rejected source PNG: {source_reason}")

    rejected_dir = output_dir.resolve() / "rejected_attempts"
    if rejected_dir.is_symlink():
        raise RuntimeError(f"Rejected-attempt directory must not be a symlink: {rejected_dir}")
    rejected_dir.mkdir(parents=True, exist_ok=True)
    digest = str(source_details["sha256"])
    target = rejected_dir / f"{digest}.png"
    duplicate = False
    if target.exists() or target.is_symlink():
        target_valid, target_reason, target_details = inspect_png(target)
        if not target_valid or target_details.get("sha256") != digest:
            raise RuntimeError(
                f"Existing rejected-attempt object is invalid: {target_reason}"
            )
        duplicate = True
    else:
        staging = rejected_dir / f".{digest}.{uuid.uuid4().hex}.tmp"
        try:
            shutil.copyfile(source, staging)
            staged_valid, staged_reason, staged_details = inspect_png(staging)
            if not staged_valid or staged_details.get("sha256") != digest:
                raise RuntimeError(
                    f"Rejected-attempt staging failed validation: {staged_reason}"
                )
            if target.exists():
                existing_valid, existing_reason, existing_details = inspect_png(target)
                if not existing_valid or existing_details.get("sha256") != digest:
                    raise RuntimeError(
                        "Concurrent rejected-attempt object is invalid: "
                        f"{existing_reason}"
                    )
                duplicate = True
            else:
                os.replace(staging, target)
        finally:
            if staging.exists():
                staging.unlink()
    append_progress(
        output_dir / PROGRESS_LOG_NAME,
        "image_rejected_archived",
        task_id=task_id,
        scene_number=task.get("scene_number"),
        expected_image=task.get("expected_image"),
        source=str(source),
        archive=str(target),
        sha256=digest,
        size_bytes=source_details["size_bytes"],
        duplicate=duplicate,
        detail=detail or None,
        elapsed_ms=round((time.perf_counter() - started) * 1000),
    )
    return {
        "status": "duplicate" if duplicate else "archived",
        "task_id": task_id,
        "path": str(target),
        "sha256": digest,
        "size_bytes": source_details["size_bytes"],
    }


def fit_size(source: Tuple[int, int], box: Tuple[int, int]) -> Tuple[int, int]:
    scale = min(box[0] / source[0], box[1] / source[1])
    return max(1, int(source[0] * scale)), max(1, int(source[1] * scale))


def make_pdf(scenes: Sequence[Scene], output_pdf: Path, language: str, footer: str) -> None:
    from PIL import Image, ImageDraw

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    if output_pdf.is_symlink():
        raise RuntimeError(f"Refusing to replace a PDF symlink: {output_pdf}")
    page_w, page_h = 1600, 1200
    margin = 68
    image_box = (page_w - margin * 2, 840)
    caption_top = margin + image_box[1] + 42
    title_font = load_pdf_font(32 if language == "en" else 34, language, bold=True)
    caption_font = load_pdf_font(32 if language == "en" else 38, language)
    footer_font = load_pdf_font(22, language)

    rendered = []
    for index, scene in enumerate(scenes, start=1):
        canvas = Image.new("RGB", (page_w, page_h), (248, 243, 232))
        draw = ImageDraw.Draw(canvas)
        image_path = Path(scene.image_path)
        if not image_path.exists():
            raise RuntimeError(f"Missing image: {image_path}")
        with Image.open(image_path) as source:
            source = source.convert("RGB")
            draw_size = fit_size(source.size, image_box)
            resized = source.resize(draw_size, Image.Resampling.LANCZOS)
        x = (page_w - draw_size[0]) // 2
        y = margin + (image_box[1] - draw_size[1]) // 2
        canvas.paste(resized, (x, y))
        draw.rectangle((x, y, x + draw_size[0] - 1, y + draw_size[1] - 1), outline=(108, 91, 68), width=3)

        if language == "en":
            title = scene.title_en or scene.title_zh
            narration = scene.narration_en or scene.narration_zh
        else:
            title = scene.title_zh
            narration = scene.narration_zh
        draw_lines(draw, wrap_text(draw, f"{scene.number:02d}. {title}", title_font, page_w - margin * 2, 1), (margin, caption_top), title_font, (45, 38, 30), 8)
        draw_lines(draw, wrap_text(draw, narration, caption_font, page_w - margin * 2, 2), (margin, caption_top + 56), caption_font, (75, 58, 42), 12)
        draw.text((margin, page_h - 44), footer, font=footer_font, fill=(118, 97, 75))
        page_num = f"{index}/{len(scenes)}"
        draw.text((page_w - margin - text_width(draw, page_num, footer_font), page_h - 44), page_num, font=footer_font, fill=(118, 97, 75))
        rendered.append(canvas)

    temporary = output_pdf.with_name(f".{output_pdf.name}.{uuid.uuid4().hex}.tmp")
    try:
        rendered[0].save(
            temporary,
            "PDF",
            save_all=True,
            append_images=rendered[1:],
            resolution=144.0,
        )
        if temporary.stat().st_size <= 4:
            raise RuntimeError(f"Generated PDF is empty: {temporary}")
        with temporary.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                raise RuntimeError(f"Generated file is not a PDF: {temporary}")
        os.replace(temporary, output_pdf)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_caption_overrides(
    path: Path,
    scenes: Sequence[Scene],
) -> Dict[int, Dict[str, str]]:
    if path.is_symlink():
        raise RuntimeError(f"Caption plan must not be a symlink: {path}")
    if not path.is_file():
        raise RuntimeError(f"Caption plan does not exist: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != 1:
        raise RuntimeError("Caption plan must be an object with schema_version 1.")
    if set(raw) - {"schema_version", "pages"}:
        raise RuntimeError(
            f"Caption plan has unknown fields: {sorted(set(raw) - {'schema_version', 'pages'})}"
        )
    pages = raw.get("pages")
    if not isinstance(pages, list):
        raise RuntimeError("Caption plan pages must be a list.")
    allowed = {"number", "title_zh", "title_en", "narration_zh", "narration_en"}
    known_numbers = {scene.number for scene in scenes}
    result: Dict[int, Dict[str, str]] = {}
    for index, item in enumerate(pages, start=1):
        if not isinstance(item, dict):
            raise RuntimeError(f"Caption page {index} is not an object.")
        unknown = set(item) - allowed
        if unknown:
            raise RuntimeError(
                f"Caption page {index} has forbidden or unknown fields: {sorted(unknown)}"
            )
        number_value = item.get("number")
        if isinstance(number_value, bool):
            raise RuntimeError(f"Caption page {index} has no valid number.")
        if isinstance(number_value, int):
            number = number_value
        elif isinstance(number_value, str) and re.fullmatch(r"\d+", number_value):
            number = int(number_value)
        else:
            raise RuntimeError(f"Caption page {index} has no valid number.")
        if number not in known_numbers:
            raise RuntimeError(f"Caption plan references unknown scene number: {number}")
        if number in result:
            raise RuntimeError(f"Caption plan repeats scene number: {number}")
        values: Dict[str, str] = {}
        for field_name in allowed - {"number"}:
            if field_name not in item:
                continue
            if not isinstance(item[field_name], str):
                raise RuntimeError(
                    f"Caption scene {number} field {field_name} must be a string."
                )
            values[field_name] = item[field_name]
        result[number] = values
    return result


def apply_caption_overrides(
    scenes: Sequence[Scene],
    overrides: Dict[int, Dict[str, str]],
) -> List[Scene]:
    result = []
    for scene in scenes:
        updated = replace(scene, references=list(scene.references))
        for field_name, value in overrides.get(scene.number, {}).items():
            setattr(updated, field_name, value)
        result.append(updated)
    return result


def build_pdfs(
    scenes: Sequence[Scene],
    output_dir: Path,
    language: str,
    footer_zh: str,
    footer_en: str,
    progress_path: Path,
    run_id: str,
) -> List[str]:
    outputs = []
    for current_language, filename, footer in (
        ("zh", "storybook.pdf", footer_zh),
        ("en", "storybook_en.pdf", footer_en),
    ):
        if language not in (current_language, "both"):
            continue
        pdf_path = output_dir / filename
        pdf_started = time.perf_counter()
        append_progress(
            progress_path,
            "pdf_started",
            run_id=run_id,
            language=current_language,
        )
        make_pdf(scenes, pdf_path, current_language, footer)
        append_progress(
            progress_path,
            "pdf_written",
            run_id=run_id,
            language=current_language,
            path=str(pdf_path),
            size_bytes=pdf_path.stat().st_size,
            elapsed_ms=round((time.perf_counter() - pdf_started) * 1000),
        )
        outputs.append(str(pdf_path))
    return outputs


def rebuild_pdfs_only(
    output_dir: Path,
    language: str,
    footer_zh: str,
    footer_en: str,
    captions_plan: Optional[Path] = None,
) -> Dict[str, object]:
    manifest_path = output_dir / "manifest.json"
    _manifest, scenes = load_manifest(manifest_path)
    inspections = inspect_scene_images(scenes, output_dir / "images")
    pending = [item for item in inspections if item.status != "complete"]
    if pending:
        details = "\n".join(
            f"- scene {item.scene_number}: {item.expected_image}: {item.reason}"
            for item in pending
        )
        raise RuntimeError(f"Cannot rebuild PDF with missing or invalid images:\n{details}")
    overrides: Dict[int, Dict[str, str]] = {}
    caption_hash = ""
    if captions_plan is not None:
        caption_input = captions_plan.expanduser()
        if not caption_input.is_absolute():
            caption_input = (Path.cwd() / caption_input).absolute()
        if caption_input.is_symlink():
            raise RuntimeError(f"Caption plan must not be a symlink: {caption_input}")
        caption_path = caption_input.resolve()
        overrides = load_caption_overrides(caption_path, scenes)
        caption_hash = sha256_file(caption_path)
    render_scenes = apply_caption_overrides(scenes, overrides)
    run_id = uuid.uuid4().hex
    progress_path = output_dir / PROGRESS_LOG_NAME
    append_progress(
        progress_path,
        "run_started",
        run_id=run_id,
        output_dir=str(output_dir),
        pdf_only=True,
        captions_plan=str(captions_plan) if captions_plan else None,
        captions_sha256=caption_hash or None,
    )
    try:
        pdfs = build_pdfs(
            render_scenes,
            output_dir,
            language,
            footer_zh,
            footer_en,
            progress_path,
            run_id,
        )
        append_progress(
            progress_path,
            "run_finished",
            run_id=run_id,
            status="pdf_only_complete",
            pdfs=pdfs,
        )
        return {
            "status": "pdf_only_complete",
            "pdfs": pdfs,
            "captions_sha256": caption_hash or None,
            "progress": str(progress_path),
        }
    except Exception as error:
        append_progress(
            progress_path,
            "run_finished",
            run_id=run_id,
            status="failed",
            error=str(error),
        )
        raise


def write_outputs(
    markdown_file_names: Sequence[str],
    scenes: Sequence[Scene],
    output_dir: Path,
    story_title: str,
    scene_count_info: Dict[str, object],
    workflow_mode: str,
    reference_snapshot_sha256: str = "",
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Parsed Scenes", ""]
    image_policy = (
        "Use Codex built-in image_gen only. Do not use Google/Gemini APIs, "
        "GOOGLE_API_KEY, baoyu-image-gen, OpenAI Images API, SDK clients, "
        "or provider fallbacks."
    )
    prompt_lines = [
        "# Generated Image Prompts",
        "",
        "Image generation policy: " + image_policy,
        "",
    ]
    for scene in scenes:
        lines.extend([
            f"## Scene {scene.number}: {scene.title_zh}",
            "",
            f"English title: {scene.title_en}",
            "",
            f"描述：{scene.description}",
            "",
            f"中文旁白：{scene.narration_zh}",
            "",
            f"English narration: {scene.narration_en}",
            "",
            f"> {scene.source_excerpt}",
            "",
        ])
        prompt_lines.extend([
            f"## Scene {scene.number}: {scene.title_zh}",
            "",
            f"Expected image: `{image_name(scene)}`",
            "",
            "References: "
            + (
                ", ".join(f"`{reference_id}`" for reference_id in scene.references)
                if scene.references
                else "none"
            ),
            "",
            "```text",
            scene.prompt,
            "```",
            "",
        ])
    atomic_write_text(output_dir / "scenes.parsed.md", "\n".join(lines))
    atomic_write_text(output_dir / "prompts.generated.md", "\n".join(prompt_lines))
    manifest = {
        "manifest_version": 3,
        "story_title": story_title,
        "workflow_mode": workflow_mode,
        "plan_sha256": scene_plan_sha256(scenes),
        "reference_manifest_sha256": reference_snapshot_sha256 or None,
        "image_generation_policy": image_policy,
        "markdown_files": list(markdown_file_names),
        "scene_count": len(scenes),
        "scene_count_info": scene_count_info,
        "pages": [asdict(scene) for scene in scenes],
    }
    atomic_write_text(
        output_dir / "manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2),
    )


def assign_images(
    scenes: Sequence[Scene],
    image_dir: Path,
    dry_run: bool,
    use_existing: bool,
    force: bool,
    size: Tuple[int, int],
) -> List[ImageInspection]:
    if image_dir.is_symlink():
        raise RuntimeError(f"Project image directory must not be a symlink: {image_dir}")
    image_dir.mkdir(parents=True, exist_ok=True)
    if dry_run:
        for scene in scenes:
            path = image_dir / image_name(scene)
            valid, _reason, _details = inspect_png(path, allow_placeholder=True)
            if force or not valid:
                create_placeholder(path, scene, size)
        return inspect_scene_images(scenes, image_dir, allow_placeholder=True)

    inspections = inspect_scene_images(scenes, image_dir)
    if use_existing:
        pending = [inspection for inspection in inspections if inspection.status != "complete"]
        if pending:
            details = "\n".join(
                f"- scene {item.scene_number}: {item.expected_image}: {item.reason}"
                for item in pending
            )
            raise RuntimeError(f"Missing or invalid expected images:\n{details}")
    return inspections


def parse_size(value: str) -> Tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value)
    if not match:
        raise RuntimeError("Use --size WIDTHxHEIGHT, e.g. 1536x1024")
    return int(match.group(1)), int(match.group(2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("build/storybook_auto"))
    parser.add_argument("--scene-plan", type=Path, default=None)
    parser.add_argument(
        "--reference-spec",
        type=Path,
        default=None,
        help="Project-local JSON catalog additions for hash-locked reference assets.",
    )
    parser.add_argument("--scene-count", default="auto", help="auto, or a positive integer such as 12, 16, 20, 24")
    parser.add_argument("--draft", action="store_true", help="Create a 6- or 8-page draft storyboard.")
    parser.add_argument("--resume", action="store_true", help="Resume from the existing manifest without rescanning source Markdown.")
    parser.add_argument(
        "--migrate-legacy-manifest",
        action="store_true",
        help="Explicitly freeze a pre-v2 manifest that has no plan_sha256.",
    )
    parser.add_argument("--story-title", default="Storybook")
    parser.add_argument("--footer-zh", default="绘本")
    parser.add_argument("--footer-en", default="Storybook")
    parser.add_argument("--language", choices=["zh", "en", "both"], default="both")
    parser.add_argument("--size", default="1536x1024")
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--mapping-mode", choices=sorted(MAPPING_MODES), default="directory-diff")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-existing-images", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--prompts-only", action="store_true")
    parser.add_argument(
        "--pdf-only",
        action="store_true",
        help="Rebuild PDFs from frozen images without rewriting generation files.",
    )
    parser.add_argument(
        "--captions-plan",
        type=Path,
        default=None,
        help="Text-only caption overrides; valid only with --pdf-only.",
    )
    parser.add_argument("--progress-event", choices=sorted(PROGRESS_EVENTS), default=None)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--detail", default="")
    parser.add_argument("--import-image", type=Path, default=None)
    parser.add_argument(
        "--archive-rejected",
        type=Path,
        default=None,
        help="Archive one rejected generated PNG once by content hash.",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.expanduser().resolve()
    command_actions = (
        int(args.progress_event is not None)
        + int(args.import_image is not None)
        + int(args.archive_rejected is not None)
        + int(args.pdf_only)
    )
    if command_actions > 1:
        raise RuntimeError(
            "Use only one of --progress-event, --import-image, "
            "--archive-rejected, or --pdf-only at a time."
        )
    if args.captions_plan is not None and not args.pdf_only:
        raise RuntimeError("--captions-plan is valid only with --pdf-only.")
    if args.pdf_only:
        incompatible = (
            args.resume
            or args.migrate_legacy_manifest
            or args.draft
            or args.scene_plan is not None
            or args.reference_spec is not None
            or args.dry_run
            or args.use_existing_images
            or args.force
            or args.prompts_only
            or args.concurrency != 1
            or args.mapping_mode != "directory-diff"
            or bool(args.task_id)
            or bool(args.detail)
        )
        if incompatible:
            raise RuntimeError(
                "--pdf-only cannot be combined with planning, generation, "
                "resume, import, or reference-preparation options."
            )
        result = rebuild_pdfs_only(
            output_dir,
            args.language,
            args.footer_zh,
            args.footer_en,
            args.captions_plan,
        )
        print(json.dumps(result, ensure_ascii=False))
        return
    if args.progress_event is not None or args.import_image is not None or args.archive_rejected is not None:
        if not args.task_id:
            raise RuntimeError(
                "--task-id is required for progress, import, and rejected-archive commands."
            )
        if args.progress_event:
            record_generation_event(output_dir, args.progress_event, args.task_id, args.detail)
            print(json.dumps({"event": args.progress_event, "task_id": args.task_id}))
        elif args.import_image is not None:
            inspection = import_generated_image(output_dir, args.task_id, args.import_image)
            print(json.dumps(asdict(inspection), ensure_ascii=False))
        else:
            archived = archive_rejected_attempt(
                output_dir,
                args.task_id,
                args.archive_rejected,
                detail=args.detail,
            )
            print(json.dumps(archived, ensure_ascii=False))
        return

    if args.dry_run and args.use_existing_images:
        raise RuntimeError("--dry-run and --use-existing-images cannot be combined.")
    validate_generation_config(args.concurrency, args.mapping_mode)

    manifest_path = output_dir / "manifest.json"
    use_manifest = args.resume or (args.use_existing_images and manifest_path.is_file())
    if use_manifest and args.reference_spec is not None:
        raise RuntimeError(
            "--reference-spec cannot modify a frozen manifest. "
            "Use the existing reference snapshot or start a new output directory."
        )
    if args.resume and not manifest_path.is_file():
        raise RuntimeError(f"Cannot resume without an existing manifest: {manifest_path}")
    project_dir: Optional[Path] = None
    if not use_manifest:
        project_dir = validate_project_dir(args.project_dir)
        if output_dir == project_dir or not path_is_within(output_dir, project_dir):
            raise RuntimeError(
                "--output-dir must be a child directory inside --project-dir "
                "so generated files cannot become source material."
            )

    run_id = uuid.uuid4().hex
    progress_path = output_dir / PROGRESS_LOG_NAME
    finished_logged = False
    append_progress(
        progress_path,
        "run_started",
        run_id=run_id,
        output_dir=str(output_dir),
        resume=args.resume,
        migrate_legacy_manifest=args.migrate_legacy_manifest,
        draft=args.draft,
        prompts_only=args.prompts_only,
        dry_run=args.dry_run,
        use_existing_images=args.use_existing_images,
        concurrency=args.concurrency,
        mapping_mode=args.mapping_mode,
        reference_spec=str(args.reference_spec) if args.reference_spec else None,
    )

    try:
        load_started = time.perf_counter()
        reference_catalog: Dict[str, Dict[str, object]] = {}
        reference_snapshot_sha256 = ""
        reference_project_dir: Optional[Path] = None
        if use_manifest:
            manifest, scenes = load_manifest(
                manifest_path,
                allow_legacy=args.migrate_legacy_manifest,
            )
            reference_catalog, reference_snapshot_sha256, reference_project_dir = (
                load_reference_snapshot(
                    output_dir,
                    expected_hash=str(
                        manifest.get("reference_manifest_sha256") or ""
                    ),
                    required=any(scene.references for scene in scenes),
                )
            )
            validate_scene_references(scenes, reference_catalog)
            legacy_manifest_loaded = (
                int(manifest.get("manifest_version", 1)) < 2
                and not manifest.get("plan_sha256")
            )
            story_title = str(manifest.get("story_title") or args.story_title)
            workflow_mode = str(manifest.get("workflow_mode") or "final")
            if args.draft and workflow_mode != "draft":
                raise RuntimeError("The existing manifest is not a draft plan.")
            scene_count_info = dict(
                manifest.get("scene_count_info")
                or {
                    "mode": "manifest",
                    "requested": str(manifest_path),
                    "selected": len(scenes),
                    "reason": "existing manifest",
                }
            )
            markdown_file_names = [
                str(value) for value in manifest.get("markdown_files", [])
            ]
            for scene in scenes:
                scene.prompt = build_prompt(scene, story_title)
            finalize_scenes(scenes)
            if args.scene_plan:
                supplied_scenes = load_scene_plan(args.scene_plan.expanduser().resolve(), story_title)
                for scene in supplied_scenes:
                    scene.prompt = build_prompt(scene, story_title)
                finalize_scenes(supplied_scenes)
                if scene_plan_sha256(supplied_scenes) != scene_plan_sha256(scenes):
                    raise RuntimeError(
                        "The supplied scene plan differs from the frozen manifest. "
                        "Resume with the manifest or use a new output directory."
                    )
            append_progress(
                progress_path,
                "manifest_loaded",
                run_id=run_id,
                manifest=str(manifest_path),
                plan_sha256=scene_plan_sha256(scenes),
                elapsed_ms=round((time.perf_counter() - load_started) * 1000),
            )
        else:
            assert project_dir is not None
            markdown = read_markdown(project_dir, excluded_paths=[output_dir])
            markdown_file_names = list(markdown.keys())
            story_title = args.story_title
            workflow_mode = "draft" if args.draft else "final"
            append_progress(
                progress_path,
                "sources_loaded",
                run_id=run_id,
                project_dir=str(project_dir),
                markdown_count=len(markdown),
                elapsed_ms=round((time.perf_counter() - load_started) * 1000),
            )
            if args.scene_plan:
                scenes = load_scene_plan(args.scene_plan.expanduser().resolve(), story_title)
                if args.draft and len(scenes) not in (6, 8):
                    raise RuntimeError("A draft scene plan must contain exactly 6 or 8 scenes.")
                scene_count_info = {
                    "mode": "draft-scene-plan" if args.draft else "scene-plan",
                    "requested": str(args.scene_plan),
                    "selected": len(scenes),
                    "reason": "scene plan item count",
                }
            else:
                scene_count, scene_count_info = resolve_scene_count(
                    args.scene_count,
                    markdown,
                    draft=args.draft,
                )
                scenes = infer_scene_plan(markdown, scene_count, story_title)
            for scene in scenes:
                scene.prompt = build_prompt(scene, story_title)
            finalize_scenes(scenes)
            reference_catalog = prepare_project_references(
                project_dir,
                args.reference_spec,
            )
            validate_scene_references(scenes, reference_catalog)
            ensure_compatible_existing_plan(
                output_dir,
                scenes,
                allow_legacy=args.migrate_legacy_manifest,
            )
            (
                reference_catalog,
                reference_snapshot_sha256,
            ) = write_reference_snapshot(
                output_dir,
                project_dir,
                scenes,
                reference_catalog,
            )
            reference_project_dir = project_dir

        image_dir = output_dir / "images"
        inspections = assign_images(
            scenes,
            image_dir,
            args.dry_run,
            False,
            args.force,
            parse_size(args.size),
        )
        write_outputs(
            markdown_file_names,
            scenes,
            output_dir,
            story_title,
            scene_count_info,
            workflow_mode,
            reference_snapshot_sha256,
        )
        if use_manifest and legacy_manifest_loaded:
            append_progress(
                progress_path,
                "legacy_manifest_migrated",
                run_id=run_id,
                manifest=str(manifest_path),
                plan_sha256=scene_plan_sha256(scenes),
            )
        generation_plan = write_generation_plan(
            output_dir,
            scenes,
            inspections,
            workflow_mode,
            args.concurrency,
            args.mapping_mode,
            reference_catalog,
            reference_snapshot_sha256,
            reference_project_dir,
        )
        append_progress(
            progress_path,
            "outputs_written",
            run_id=run_id,
            plan_sha256=scene_plan_sha256(scenes),
            total=generation_plan["summary"]["total"],
            complete=generation_plan["summary"]["complete"],
            pending=generation_plan["summary"]["pending"],
            planned_reference_payload_bytes_per_pending_pass=generation_plan["summary"][
                "planned_reference_payload_bytes_per_pending_pass"
            ],
        )
        for inspection in inspections:
            append_progress(
                progress_path,
                "image_status",
                run_id=run_id,
                task_id=inspection.task_id,
                scene_number=inspection.scene_number,
                expected_image=inspection.expected_image,
                status=inspection.status,
                reason=inspection.reason,
                size_bytes=inspection.size_bytes or None,
                width=inspection.width or None,
                height=inspection.height or None,
                sha256=inspection.sha256 or None,
            )

        pending = [item for item in inspections if item.status != "complete"]
        if args.use_existing_images and pending:
            details = "\n".join(
                f"- scene {item.scene_number}: {item.expected_image}: {item.reason}"
                for item in pending
            )
            append_progress(
                progress_path,
                "run_finished",
                run_id=run_id,
                status="waiting_for_images",
                pending=len(pending),
            )
            finished_logged = True
            raise RuntimeError(f"Missing or invalid expected images:\n{details}")

        if args.prompts_only or (args.resume and not args.use_existing_images):
            status = "prompts_ready" if pending else "images_complete"
            append_progress(
                progress_path,
                "run_finished",
                run_id=run_id,
                status=status,
                pending=len(pending),
            )
            finished_logged = True
            print(
                json.dumps(
                    {
                        "status": status,
                        "total": len(inspections),
                        "complete": len(inspections) - len(pending),
                        "pending": len(pending),
                        "generation_plan": str(output_dir / GENERATION_PLAN_NAME),
                        "progress": str(progress_path),
                    },
                    ensure_ascii=False,
                )
            )
            return

        if not args.dry_run and not args.use_existing_images:
            raise RuntimeError(
                "Generate images only with Codex built-in image_gen, then rerun with "
                "--resume --prompts-only or --use-existing-images. Do not use Google/Gemini, "
                "GOOGLE_API_KEY, baoyu-image-gen, OpenAI Images API, or provider fallbacks."
            )

        pdf_outputs = build_pdfs(
            scenes,
            output_dir,
            args.language,
            args.footer_zh,
            args.footer_en,
            progress_path,
            run_id,
        )

        append_progress(
            progress_path,
            "run_finished",
            run_id=run_id,
            status="dry_run_complete" if args.dry_run else "complete",
            pdfs=pdf_outputs,
        )
        finished_logged = True
        print(
            json.dumps(
                {
                    "status": "dry_run_complete" if args.dry_run else "complete",
                    "pdfs": pdf_outputs,
                    "progress": str(progress_path),
                },
                ensure_ascii=False,
            )
        )
    except Exception as error:
        if not finished_logged:
            append_progress(
                progress_path,
                "run_finished",
                run_id=run_id,
                status="failed",
                error=str(error),
            )
        raise


if __name__ == "__main__":
    main()
