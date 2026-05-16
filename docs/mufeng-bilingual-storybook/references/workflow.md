# Mufeng Bilingual Storybook Workflow

## Output Shape

Use this structure for a formal bilingual picture-book chapter:

- `build/storybook_auto/scenes.parsed.md`
- `build/storybook_auto/prompts.generated.md`
- `build/storybook_auto/manifest.json`
- `build/storybook_auto/images/scene_01_title.png` ... `scene_N_title.png`
- `build/storybook_auto/storybook.pdf`
- `build/storybook_auto/storybook_en.pdf`

Use `build/storybook_auto_dryrun/` only for placeholder layout validation.

For a forced 20-page version, use `--scene-count 20 --output-dir build/storybook_20`.

## Page Count Policy

Use `--scene-count auto` unless the user gives an exact number. Auto mode chooses one of four page counts and records the decision in `manifest.json` under `scene_count_info`.

- 12 pages: short story / compact single episode
- 16 pages: medium chapter / several clear beats
- 20 pages: formal picture-book chapter
- 24 pages: long or complex chapter

The helper script makes this deterministic from Markdown metrics: CJK character count, Latin word count, paragraph count, sentence count, heading count, and a combined complexity score. It uses body length and paragraph complexity as the primary signal so classical Chinese short sentences do not inflate the page count by themselves. If Codex has already authored a `--scene-plan`, the number of JSON scene items overrides `--scene-count`.

Current auto thresholds:

- 12 pages: up to 1400 narrative units, 18 paragraphs, and 60 sentences
- 16 pages: up to 2800 narrative units, 30 paragraphs, and 100 sentences
- 20 pages: up to 5500 narrative units, 85 paragraphs, and 190 sentences
- 24 pages: anything longer or structurally more complex

## Scene Plan JSON

For best quality, have Codex author a scene plan JSON before generating images:

```json
[
  {
    "number": 1,
    "title_zh": "混沌初开",
    "title_en": "Chaos Begins",
    "description": "Visual image brief in Chinese or English.",
    "narration_zh": "天地刚刚打开。西游的故事，也从这里开始。",
    "narration_en": "The world had just opened. The journey west begins here.",
    "source_excerpt": "Relevant source quote or prose excerpt.",
    "prompt": "Full image prompt. No text in image."
  }
]
```

Keep narration short enough for two PDF lines. Use the auto-selected count unless the user requests another count.

## Prompt Rules

Each image prompt should include:

- Use case: `illustration-story`
- Asset type: one page illustration for a formal children's picture book
- Scene title and visual brief
- Style continuity
- Character continuity
- World continuity
- Constraints: no readable text, captions, labels, speech bubbles, borders, or watermark

For inscriptions, tablets, signs, plaques, scrolls, or carved stones, request abstract decorative marks only.

## PDF Rules

Use the same images for both languages. Only the title line, narration, footer, and PDF filename change.

Chinese:

- PDF: `storybook.pdf`
- Footer: short title such as `西游记 · 第一回`

English:

- PDF: `storybook_en.pdf`
- Footer: short title such as `Journey to the West - Chapter 1`

## Validation

Always check:

```bash
file build/storybook_auto/storybook.pdf build/storybook_auto/storybook_en.pdf
find build/storybook_auto/images -maxdepth 1 -type f -name '*.png' | wc -l
```

Render a few sample pages with `pdftoppm` when available:

```bash
mkdir -p build/storybook_auto/preview
pdftoppm -f 1 -l 1 -png -r 100 build/storybook_auto/storybook.pdf build/storybook_auto/preview/page_zh
pdftoppm -f 1 -l 1 -png -r 100 build/storybook_auto/storybook_en.pdf build/storybook_auto/preview/page_en
```

Inspect sampled pages for:

- No accidental ellipses in short titles
- No text overlap
- Page number correct
- Footer title short and natural
- Captions not clipped
