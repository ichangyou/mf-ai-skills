#!/usr/bin/env python3
"""Reusable bilingual picture-book helper.

This script handles deterministic parts of a Codex storybook workflow:
load Markdown, consume or infer a scene plan, write prompt/manifest files,
validate image filenames, create placeholder images for layout tests, and
assemble Chinese/English PDFs from the same image set.

It does not call image APIs. Generate art with Codex built-in image generation,
then rerun with --use-existing-images.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
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


def markdown_files(project_dir: Path) -> List[Path]:
    files: List[Path] = []
    for pattern in ("*.md", "*.markdown"):
        for path in project_dir.rglob(pattern):
            if not path.is_file():
                continue
            parts = path.relative_to(project_dir).parts
            if any(part.startswith(".") or part in EXCLUDED_DIRS for part in parts):
                continue
            files.append(path)
    return sorted(set(files), key=lambda p: p.as_posix())


def read_markdown(project_dir: Path) -> Dict[str, str]:
    result = {str(path): path.read_text(encoding="utf-8") for path in markdown_files(project_dir)}
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


def resolve_scene_count(value: str, markdown: Dict[str, str]) -> Tuple[int, Dict[str, object]]:
    requested = value.strip().lower()
    if requested == "auto":
        count, reason, metrics = auto_scene_count(markdown)
        return count, {
            "mode": "auto",
            "requested": value,
            "selected": count,
            "reason": reason,
            "metrics": metrics,
            "policy": {
                "short_story": 12,
                "medium_chapter": 16,
                "formal_picture_book_chapter": 20,
                "long_or_complex_chapter": 24,
            },
        }
    if not re.fullmatch(r"\d+", requested):
        raise RuntimeError("Use --scene-count auto or a positive integer, e.g. --scene-count 12")
    count = int(requested)
    if count < 1 or count > 60:
        raise RuntimeError("--scene-count must be between 1 and 60.")
    return count, {
        "mode": "manual",
        "requested": value,
        "selected": count,
        "reason": "manual override",
    }


def slug(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", value).strip("_")
    return cleaned or "page"


def image_name(scene: Scene) -> str:
    return f"scene_{scene.number:02d}_{slug(scene.title_zh)}.png"


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
        scene = Scene(
            number=number,
            title_zh=str(item.get("title_zh") or item.get("title") or f"第{number}页"),
            title_en=str(item.get("title_en") or f"Page {number}"),
            description=str(item.get("description") or ""),
            narration_zh=str(item.get("narration_zh") or item.get("narration") or ""),
            narration_en=str(item.get("narration_en") or ""),
            source_excerpt=str(item.get("source_excerpt") or item.get("excerpt") or ""),
            prompt=str(item.get("prompt") or ""),
        )
        scene.prompt = build_prompt(scene, story_title)
        scenes.append(scene)
    return sorted(scenes, key=lambda scene: scene.number)


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
    from PIL import Image, ImageDraw

    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", size, (240, 232, 214))
    draw = ImageDraw.Draw(image)
    font_title = load_font(max(30, size[0] // 30), bold=True)
    font_body = load_font(max(24, size[0] // 48))
    draw.rectangle((40, 40, size[0] - 40, size[1] - 40), outline=(116, 92, 60), width=4)
    draw_lines(draw, [f"{scene.number:02d}. {scene.title_zh}"], (80, 90), font_title, (50, 42, 32), 8)
    draw_lines(draw, wrap_text(draw, scene.narration_zh, font_body, size[0] - 160, 3), (80, 170), font_body, (80, 62, 44), 8)
    draw_lines(draw, wrap_text(draw, scene.narration_en, font_body, size[0] - 160, 3), (80, 320), font_body, (80, 62, 44), 8)
    image.save(path)


def fit_size(source: Tuple[int, int], box: Tuple[int, int]) -> Tuple[int, int]:
    scale = min(box[0] / source[0], box[1] / source[1])
    return max(1, int(source[0] * scale)), max(1, int(source[1] * scale))


def make_pdf(scenes: Sequence[Scene], output_pdf: Path, language: str, footer: str) -> None:
    from PIL import Image, ImageDraw

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = 1600, 1200
    margin = 68
    image_box = (page_w - margin * 2, 840)
    caption_top = margin + image_box[1] + 42
    title_font = load_font(32 if language == "en" else 34, bold=True)
    caption_font = load_font(32 if language == "en" else 38)
    footer_font = load_font(22)

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

    rendered[0].save(output_pdf, "PDF", save_all=True, append_images=rendered[1:], resolution=144.0)


def write_outputs(
    markdown: Dict[str, str],
    scenes: Sequence[Scene],
    output_dir: Path,
    story_title: str,
    scene_count_info: Dict[str, object],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Parsed Scenes", ""]
    prompt_lines = ["# Generated Image Prompts", ""]
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
            "```text",
            scene.prompt,
            "```",
            "",
        ])
    (output_dir / "scenes.parsed.md").write_text("\n".join(lines), encoding="utf-8")
    (output_dir / "prompts.generated.md").write_text("\n".join(prompt_lines), encoding="utf-8")
    manifest = {
        "story_title": story_title,
        "markdown_files": list(markdown.keys()),
        "scene_count": len(scenes),
        "scene_count_info": scene_count_info,
        "pages": [asdict(scene) for scene in scenes],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def assign_images(scenes: Sequence[Scene], image_dir: Path, dry_run: bool, use_existing: bool, force: bool, size: Tuple[int, int]) -> None:
    image_dir.mkdir(parents=True, exist_ok=True)
    for scene in scenes:
        path = image_dir / image_name(scene)
        scene.image_path = str(path)
        if dry_run:
            if force or not path.exists():
                create_placeholder(path, scene, size)
        elif use_existing:
            if not path.exists():
                raise RuntimeError(f"Missing expected image: {path}")


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
    parser.add_argument("--scene-count", default="auto", help="auto, or a positive integer such as 12, 16, 20, 24")
    parser.add_argument("--story-title", default="Storybook")
    parser.add_argument("--footer-zh", default="绘本")
    parser.add_argument("--footer-en", default="Storybook")
    parser.add_argument("--language", choices=["zh", "en", "both"], default="both")
    parser.add_argument("--size", default="1536x1024")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-existing-images", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--prompts-only", action="store_true")
    args = parser.parse_args()

    markdown = read_markdown(args.project_dir.resolve())
    if args.scene_plan:
        scenes = load_scene_plan(args.scene_plan.resolve(), args.story_title)
        scene_count_info = {
            "mode": "scene-plan",
            "requested": str(args.scene_plan),
            "selected": len(scenes),
            "reason": "scene plan item count",
        }
    else:
        scene_count, scene_count_info = resolve_scene_count(args.scene_count, markdown)
        scenes = infer_scene_plan(markdown, scene_count, args.story_title)
    for scene in scenes:
        scene.prompt = build_prompt(scene, args.story_title)

    output_dir = args.output_dir.resolve()
    image_dir = output_dir / "images"
    assign_images(scenes, image_dir, args.dry_run, args.use_existing_images, args.force, parse_size(args.size))
    write_outputs(markdown, scenes, output_dir, args.story_title, scene_count_info)

    if args.prompts_only:
        return
    if not args.dry_run and not args.use_existing_images:
        raise RuntimeError("Generate images with Codex built-in image generation, then rerun with --use-existing-images.")
    if args.language in ("zh", "both"):
        make_pdf(scenes, output_dir / "storybook.pdf", "zh", args.footer_zh)
    if args.language in ("en", "both"):
        make_pdf(scenes, output_dir / "storybook_en.pdf", "en", args.footer_en)


if __name__ == "__main__":
    main()
