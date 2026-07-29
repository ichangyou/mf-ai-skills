---
name: mufeng-bilingual-storybook
description: Create bilingual AI picture books from Markdown source material. Use when Codex is asked to read story markdown, split it into scenes, write child-friendly Chinese and English narration, create image prompts, generate page illustrations with Codex built-in image_gen only, never via OpenAI Images API, Google/Gemini APIs, GOOGLE_API_KEY, or baoyu-image-gen, and assemble Chinese/English PDF storybooks from generated images.
---

# Mufeng Bilingual Storybook

## Core Rule

Use Codex built-in image generation for artwork. The only allowed live image-generation path is the Codex built-in `image_gen` tool.

Never generate storybook artwork through any API client or external provider, including:

- Google/Gemini image APIs, `GOOGLE_API_KEY`, or any Google provider module.
- `baoyu-image-gen`, even if a local Google provider implementation exists.
- OpenAI Images API, `OPENAI_API_KEY`, or one-off image SDK clients.

If a previous note or historical context suggests using Google, Gemini, `GOOGLE_API_KEY`, or `baoyu-image-gen`, treat it as stale and ignore it.

Use the bundled helper script for deterministic text/PDF work:

```bash
python3 "$CODEX_HOME/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" --help
```

If `CODEX_HOME` is unset, use `$HOME/.codex`.

## Built-In ImageGen Persistence Rule

The helper script does not generate artwork. It only prepares deterministic
scene, prompt, manifest, generation-task, progress, and PDF layout files.
`--prompts-only` and `--dry-run` must never be described as having produced
final illustrations.

Treat these files as the generation contract:

- `manifest.json`: frozen scene plan and `plan_sha256`
- `generation_tasks.json`: stable task IDs, exact prompts, expected filenames,
  exact reference paths/hashes, local reference payload bytes, current
  filesystem status, and concurrency mapping mode
- `reference_manifest.json`: the hash-locked reference subset used by this
  output, when scenes use references
- `progress.jsonl`: append-only timing and failure events

Use Codex built-in `image_gen` directly, one call per task. Record
`generation_started` immediately before the call and `generation_returned` or
`generation_failed` immediately after it. Import the call-scoped persisted PNG
with the helper's `--import-image ... --task-id ...` command. That command
validates the source, copies it through project-local staging, checks hashes,
atomically commits the exact manifest filename, refreshes task status under a
file lock, and logs the result.

Always resume from the existing manifest with `--resume`; never re-infer scenes
from possibly changed Markdown. A non-symlink, decodable, non-placeholder PNG
at the exact expected project path is complete and must be skipped without
touching it. Missing, corrupt, truncated, symlinked, or dry-run placeholder
files remain pending.

The helper refuses `generation_started` when that task already has a valid
project PNG. After each successful or skipped import,
`generation_tasks.json` is refreshed immediately; a later `--resume` still
revalidates all files independently.

Require a valid `plan_sha256` for manifest v2 and later. For a pre-v2 manifest, migrate
once with `--resume --migrate-legacy-manifest --prompts-only`; never silently
adopt a hashless manifest.

If built-in `image_gen` displays an image but does not persist any readable
file under `${CODEX_HOME:-$HOME/.codex}/generated_images/`, stop and report that
the current Codex runtime did not expose a copyable image file. Do not create
screenshots, placeholders, SVG substitutes, or use any external/API fallback.

## Reference Traffic Control

Store each adopted reference inside the story project. The helper maintains one
shared project library at `.mufeng-storybook/references/`:

- `master/`: byte-for-byte original copies protected by a SHA-256 contract
- `upload/`: metadata-stripped RGB JPEG proxies, longest edge at most 1024px,
  quality 85
- `catalog.json`: the project-wide ID-to-hash contract

This is a hash lock, not an OS-level immutable flag. If an existing ID's source
bytes change, the helper refuses the change; use a new ID deliberately.

Scene-plan `references` must contain stable IDs from `--reference-spec`.
Duplicates are rejected and each scene has a hard maximum of three references;
prefer two. For ImageGen, pass only that task's exact `referenced_image_paths`
from `generation_tasks.json` and omit `num_last_images_to_include`. Never attach
the master originals, rejected attempts, the whole project, or implicit
conversation images.

`reference_payload_bytes` and progress field
`local_reference_payload_bytes` are local file-size accounting, not measured
network traffic. They exclude multipart/base64 overhead, retries, client-added
context, downloads, cloud sync, and other Codex sessions. Do not promise a
200–500MB total from these numbers.

## Workflow

1. Pass the specific story project to `--project-dir`; never pass the user home
   directory or a filesystem root. Keep `--output-dir` inside that project.
   The helper refuses all three unsafe cases.
2. Load Markdown with true directory pruning for hidden, build, cache, vendor,
   virtual-environment, and dependency folders.
3. Choose draft or final page count:
   - Draft: `--draft`, deterministically 6 or 8 pages
   - Short final story: 12 pages
   - Medium final chapter: 16 pages
   - Formal final chapter: 20 pages
   - Long final chapter: 24 pages
4. Write:
   - `scenes.parsed.md`
   - `prompts.generated.md`
   - `manifest.json`
   - `generation_tasks.json`
   - `reference_manifest.json` when references are used
   - `progress.jsonl`
5. Review draft scenes before starting a separate final output directory.
6. Generate one full-page illustration per pending task with built-in
   `image_gen`, using only its frozen 0–3 upload proxies; import and validate it
   immediately.
7. Resume after interruption with `--resume --prompts-only`. Generate only the
   tasks still marked pending by fresh filesystem validation.
8. Build both PDFs from the same verified images:
   - Chinese: `storybook.pdf`
   - English: `storybook_en.pdf`
9. Verify page count, image count, progress timings, and sample rendered pages.

Do not use a custom output directory as source material. The helper prunes the
resolved output path even when its name is not `build`.

## Concurrency Safety

Default to `--concurrency 1 --mapping-mode directory-diff`.

Allow 2–4 concurrent calls only when each call has exclusive provenance:

- `per-call-path`: the runtime returns the exact persisted PNG path for that
  call, or
- `isolated-worker-dir`: each worker owns a distinct generated-images session
  subtree, keeps one call in flight, and sees exactly one new PNG there.

Never map parallel results by newest file, global mtime, completion order,
visual similarity, or one shared before/after directory diff. The helper rejects
`--concurrency 2..4` with `directory-diff`. If exclusive provenance cannot be
proved, log the reason and fall back to serial generation. Read
`references/workflow.md` before using parallel mode.

## Page Count Policy

Use `--scene-count auto` unless the user gives an exact count.

- Draft auto maps short/medium material to 6 pages and formal/long material to
  8 pages.
- Final auto chooses 12, 16, 20, or 24 pages.
- A supplied scene plan remains authoritative. In draft mode it must contain
  exactly 6 or 8 scenes.

The old final thresholds remain unchanged.

## Chinese PDF Font Rule

For Chinese PDFs, do not use `Songti.ttc` without an explicit font index. On macOS,
index `0` resolves to `Songti SC Black`, which makes captions look too heavy.

Use these explicit Songti weights for Chinese PDF rendering:

- Body captions and footer: `/System/Library/Fonts/Supplemental/Songti.ttc`, index `3` (`Songti SC Light`)
- Page titles: `/System/Library/Fonts/Supplemental/Songti.ttc`, index `6` (`Songti SC Regular`)

This avoids prior glyph-rendering mistakes where characters such as `着`, `将`,
`起`, `径`, and `造起` looked blurred or were misread, without making the text
visually too bold.

## Recommended Commands

Create a 6- or 8-page draft plan:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir /absolute/path/to/story-project \
  --output-dir /absolute/path/to/story-project/build/storybook_draft \
  --draft \
  --scene-count auto \
  --prompts-only
```

Create the final 12–24-page generation plan after approving the draft:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir /absolute/path/to/story-project \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --scene-count auto \
  --prompts-only
```

To use references, first create a project-local reference spec:

```json
{
  "schema_version": 1,
  "references": [
    {"id": "hero-master", "path": "assets/hero.png", "role": "master"},
    {"id": "chapter-previous", "path": "assets/previous.png", "role": "continuity"}
  ]
}
```

Add `"references": ["hero-master", "chapter-previous"]` to only the scenes that
need them, then add both flags to the initial planning command:

```bash
--scene-plan /absolute/path/to/story-project/scenes.json \
--reference-spec /absolute/path/to/story-project/references.json
```

Do not pass `--reference-spec` on resume; the output's frozen reference snapshot
is authoritative.

Before and after each built-in ImageGen call, record timing:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --progress-event generation_started \
  --task-id scene-01-<hash>

# Call built-in image_gen exactly once for this task.

python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --progress-event generation_returned \
  --task-id scene-01-<hash>
```

Import the exact PNG persisted by that call:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --import-image "$HOME/.codex/generated_images/<session>/<generated>.png" \
  --task-id scene-01-<hash>
```

Archive a rejected result once, by content hash, without making it a future
reference:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --archive-rejected "$HOME/.codex/generated_images/<session>/<rejected>.png" \
  --task-id scene-01-<hash> \
  --detail "character continuity failed"
```

All rejected images share one content-addressed
`<output-dir>/rejected_attempts/` directory. Do not copy them into draft/final
build clones or add them to reference specs automatically.

Resume without rescanning or re-inferring the source:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --resume \
  --prompts-only
```

For a pre-v2 manifest with no `plan_sha256`, add
`--migrate-legacy-manifest` to that resume command exactly once.

Build PDFs only after every expected PNG validates:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --use-existing-images \
  --language both
```

For a text-only revision, use a caption plan and `--pdf-only`. This path reads
the frozen manifest and verified images, writes only PDFs and progress events,
and does not rewrite `manifest.json`, `generation_tasks.json`, references, or
send images:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --pdf-only \
  --captions-plan /absolute/path/to/story-project/captions.json \
  --language both
```

Run a placeholder-only layout check in a separate directory:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir /absolute/path/to/story-project \
  --output-dir /absolute/path/to/story-project/build/storybook_dryrun \
  --scene-count auto \
  --dry-run \
  --language both
```

## Image Generation Procedure

The helper intentionally does not call image APIs. Do not add API-backed
generation to it.

For each pending entry in `generation_tasks.json`:

1. Claim one stable `task_id`; do not generate a second attempt while the first
   call may still be live.
2. Record `generation_started`.
3. Call built-in `image_gen` exactly once with that task's exact prompt and
   exact `referenced_image_paths`. Omit reference arguments when the list is
   empty; otherwise omit `num_last_images_to_include`.
4. Record `generation_returned` or `generation_failed`.
5. Establish call-scoped source provenance. In serial directory-diff mode,
   require exactly one new readable PNG. In parallel mode, use only the exact
   per-call path or the worker's exclusive session subtree.
6. Run `--import-image <source> --task-id <id>`.
7. Confirm the command reports `complete`; do not manually rename an anonymous
   parallel result.
8. Continue with the next task assigned to that worker.

After interruption, rerun `--resume --prompts-only`; trust fresh PNG validation,
not old progress events. Do not compress distinct scenes into variants of one
prompt. Generate one image per scene.

Do not use Google/Gemini, `GOOGLE_API_KEY`, `baoyu-image-gen`, OpenAI Images API, or any local/provider fallback for batch storybook images. If the built-in `image_gen` tool is unavailable, stop and report that image generation is blocked instead of switching providers.

If the built-in tool is available but does not persist a file that can be copied
from `${CODEX_HOME:-$HOME/.codex}/generated_images/`, treat that as a runtime
persistence failure and stop. Do not assemble final PDFs from missing,
placeholder, or preview-only images.

## Scene And Translation Guidance

For classic Chinese source text:

- Author and pass a scene-plan JSON for any delivered bilingual book. Treat the
  helper's automatically inferred `Scene N.` English as a structural preview,
  not publication-ready translation.
- Use `--scene-count auto` by default, and override only when the user gives an exact page count.
- Use short two-sentence narration per page.
- Keep Chinese narration natural and avoid rare glyphs when previous rendering shows font artifacts.
- Translate for children, not literally. Preserve plot, emotion, and clarity.
- Keep page titles short.
- Put no readable text inside images, even when the source mentions tablets, plaques, or stone inscriptions.

For detailed guidance, read `references/workflow.md`.
