---
name: mufeng-bilingual-storybook
description: Create bilingual AI picture books from Markdown source material. Use when Codex is asked to read story markdown, split it into scenes, write child-friendly Chinese and English narration, create image prompts, generate page illustrations with Codex built-in image generation rather than OpenAI Images API, and assemble Chinese/English PDF storybooks from generated images.
---

# Mufeng Bilingual Storybook

## Core Rule

Use Codex built-in image generation for artwork. Do not call OpenAI Images API, do not require `OPENAI_API_KEY`, and do not create one-off image SDK clients.

Use the bundled helper script for deterministic text/PDF work:

```bash
python "$CODEX_HOME/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" --help
```

If `CODEX_HOME` is unset, use `$HOME/.codex`.

## Workflow

1. Load all Markdown files in the project except build/cache/vendor folders.
2. Choose the page count from context unless the user asks for a fixed count.
   - Short story / compact single episode: 12 pages
   - Medium chapter / several clear beats: 16 pages
   - Formal picture-book chapter: 20 pages
   - Long or complex chapter: 24 pages
3. Write:
   - `scenes.parsed.md`
   - `prompts.generated.md`
   - `manifest.json`
4. Generate one full-page illustration per scene using Codex built-in image generation.
5. Copy final images into `<output-dir>/images/`.
6. Build both PDFs from the same images:
   - Chinese: `storybook.pdf`
   - English: `storybook_en.pdf`
7. Verify page count, image count, and sample rendered pages.

## Recommended Commands

Create scene and prompt files only:

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto \
  --scene-count auto \
  --prompts-only
```

Build PDFs from already-generated images:

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto \
  --scene-count auto \
  --use-existing-images \
  --language both
```

Run a dry layout check without real images:

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto_dryrun \
  --scene-count auto \
  --dry-run \
  --language both
```

Force an exact page count when needed:

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_12 \
  --scene-count 12 \
  --prompts-only
```

## Image Generation Procedure

The helper script intentionally does not call image APIs. For each block in `prompts.generated.md`:

1. Use the built-in `image_gen` tool with the prompt text.
2. Save/copy the resulting image into `<output-dir>/images/` using the expected filename from `manifest.json`.
3. Keep generated images free of readable text, labels, captions, borders, and watermarks.
4. After images exist, run the helper with `--use-existing-images --language both`.

When generating many pages, do not compress distinct scenes into variants of one prompt. Generate one image per scene.

## Scene And Translation Guidance

For classic Chinese source text:

- Use `--scene-count auto` by default, and override only when the user gives an exact page count.
- Use short two-sentence narration per page.
- Keep Chinese narration natural and avoid rare glyphs when previous rendering shows font artifacts.
- Translate for children, not literally. Preserve plot, emotion, and clarity.
- Keep page titles short.
- Put no readable text inside images, even when the source mentions tablets, plaques, or stone inscriptions.

For detailed guidance, read `references/workflow.md`.
