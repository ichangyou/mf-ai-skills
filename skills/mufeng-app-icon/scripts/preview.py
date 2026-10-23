#!/usr/bin/env python3
"""Create flat, pixel-size icon previews; does not simulate OS icon rendering."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


SIZES = (24, 40, 60, 120, 180)
BACKGROUNDS = (("Light", 245), ("Gray", 128), ("Dark", 26))
CELL_WIDTH = 204
CELL_HEIGHT = 232


def generate_preview(source, output):
    source, output = Path(source), Path(output)
    if output.suffix.lower() != ".png":
        raise ValueError("Output must have a .png extension")
    if output.resolve() == source.resolve() or output.exists():
        raise FileExistsError("Choose a new output path; existing files are not overwritten")
    with Image.open(source) as image:
        if image.format not in {"PNG", "JPEG", "WEBP"} or getattr(image, "n_frames", 1) != 1:
            raise ValueError("Input must be a single-frame PNG, JPEG or WebP")
        if image.width != image.height:
            raise ValueError("Input must be square; do not stretch or crop the master implicitly")
        image.load()
        icon = image.convert("RGBA")
    alpha_min, alpha_max = icon.getchannel("A").getextrema()
    sheet = Image.new("RGB", (CELL_WIDTH * len(SIZES), CELL_HEIGHT * len(BACKGROUNDS)))
    draw = ImageDraw.Draw(sheet)
    for row, (label, gray) in enumerate(BACKGROUNDS):
        top = row * CELL_HEIGHT
        draw.rectangle((0, top, sheet.width - 1, top + CELL_HEIGHT - 1), fill=(gray,) * 3)
        text_color = "black" if gray > 100 else "white"
        for col, size in enumerate(SIZES):
            left = col * CELL_WIDTH
            draw.text((left + 12, top + 10), f"{label} / {size} px", fill=text_color)
            small = icon.resize((size, size), Image.Resampling.LANCZOS)
            background = Image.new("RGBA", small.size, (gray, gray, gray, 255))
            flattened = Image.alpha_composite(background, small).convert("RGB")
            sheet.paste(flattened, (left + (CELL_WIDTH - size) // 2, top + 38 + (180 - size) // 2))
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also prevents overwriting a file created during rendering.
    with output.open("xb") as stream:
        sheet.save(stream, format="PNG")
    return {
        "source": str(source.resolve()),
        "source_size_px": list(icon.size),
        "has_transparency": alpha_min < 255,
        "alpha_range": [alpha_min, alpha_max],
        "preview_sizes_px": list(SIZES),
        "preview_upscaled": icon.width < max(SIZES),
        "output": str(output.resolve()),
        "scope": "Flat preview only; no OS mask, appearance variants or color-profile validation",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = generate_preview(args.source, args.output)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Preview failed: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
