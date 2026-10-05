---
name: mufeng-bilingual-storybook
description: Create visually reviewed Chinese and English picture-book PDFs from Markdown stories. Use for scene planning, bilingual narration, reference-guided illustrations, page-level QA, revisions and PDF assembly in Codex or Claude Code with a configured image tool.
compatibility: "Codex and Claude Code. Python 3.10+, Pillow, pypdfium2, Chinese fonts and a configured image/vision tool."
---

# Mufeng Bilingual Storybook

## Resource Paths

Set the shell variable `SKILL_DIR` to the directory containing the **loaded** `SKILL.md` before running the commands below. Resolve supporting paths from that directory, not the working directory or a fixed user/platform installation path. `$SKILL_DIR` is a shell variable you set, not a host-provided macro.


## Image Tool Selection

Read [references/platforms.md](references/platforms.md) before generating artwork.
Prefer Codex built-in `image_gen` when available. In Claude Code, use an explicitly
configured image skill/tool with generation, reference-image and editing support.
Do not switch providers automatically. The helper itself does not call an image API.
If no image tool is configured, complete the scene/prompt plan and report the missing
dependency; do not claim that illustrations or final PDFs were produced.

For Codex, the default image source is `${CODEX_HOME:-$HOME/.codex}/generated_images/`.
For another configured image tool, set `MUFENG_IMAGE_ROOT` to its dedicated, actual
output directory. Import the exact PNG produced by the call and keep all quality gates.

## Image Persistence Rule

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
- `quality_gate.json`: append-only candidate QA decisions bound to task,
  candidate hash, scene QA-contract hash, and reviewer
- `progress.jsonl`: append-only timing and failure events
- `candidates/<task-id>/<sha256>.png`: project-local, unapproved artwork
- `qa_reports/<task-id>/<sha256>.json`: frozen structured visual reviews
- `pdf_validation.json`: final PDF hashes, page count, footers, and preview root

Use the selected image tool directly, one call per attempt. Record
`generation_started` immediately before the call and `generation_returned` or
`generation_failed` immediately after it. For a new quality-gated final
manifest, import the call-scoped persisted PNG with `--import-candidate`, never
`--import-image`. The candidate command requires a complete start/return event
pair, validates provenance and PNG bytes, and copies the attempt into the
project-local candidate area. It does not make the image PDF-eligible.

Open each candidate at original detail with the image-viewing tool, compare it
against that task's exact reference images, and fill the emitted QA template.
Use the actual reviewer identity, not the pending template value.
Record the report with `--qa-report ... --candidate-sha256 ...`. Only a report
whose verdict is `pass` and whose every required check is `pass` atomically
promotes the candidate to the exact final `images/` filename. A failed report
archives the bytes and returns a reason-targeted retry prompt.

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

If the selected tool displays an image but exposes no readable persisted PNG,
stop and report the persistence failure. Do not substitute screenshots, placeholders
or SVGs for artwork. Immediately import each attempt into the project-local candidate
area, verify the copy, then proceed to the next image. A configured source directory
and timing events bound the import; they do not independently prove which provider
created the image. Report the actual tool and call evidence separately.

## Reference Traffic Control

Store each adopted reference inside the story or series project. For a series,
pass its root with `--reference-root` so every chapter uses one shared ID/hash
catalog instead of silently creating chapter-local identities. The helper
maintains the library at `<reference-root>/.mufeng-storybook/references/`:

- `master/`: byte-for-byte original copies protected by a SHA-256 contract
- `upload/`: metadata-stripped RGB JPEG proxies, longest edge at most 1024px,
  quality 85
- `catalog.json`: the project-wide ID-to-hash contract

This is a hash lock, not an OS-level immutable flag. If an existing ID's source
bytes change, the helper refuses the change; use a new ID deliberately.

Scene-plan `references` must contain stable IDs from `--reference-spec`.
Duplicates are rejected and each scene has a hard maximum of three references;
prefer two. For Codex ImageGen, pass only that task's exact `referenced_image_paths`
from `generation_tasks.json` and omit `num_last_images_to_include`. Never use master originals or rejected attempts as canonical references,
or attach the whole project or implicit conversation images. An inspected
project-local candidate may be an explicit localized-edit target; it does not
become an approved identity/style reference.

`reference_payload_bytes` and progress field
`local_reference_payload_bytes` are local file-size accounting, not measured
network traffic. They exclude multipart/base64 overhead, retries, client-added
context, downloads, cloud sync, and other Codex sessions. Do not promise a
200–500MB total from these numbers.

## Revision And Release Workflow

Read [references/revision-release.md](references/revision-release.md) for an
existing chapter, any single-page change, or final PDF delivery.

- Freeze scene meaning and bilingual captions first. Run `--preflight-text`
  before artwork generation. Resolve overflow by editing narration without
  losing story facts; never silently truncate captions or shrink fonts.
- For an otherwise approved image with a local defect, use a localized ImageGen
  edit. Pass the inspected project-local original as the edit target alongside
  the required task references; the target is not a new canonical reference.
  This revision mode supplements the frozen prompt with the specific correction.
  Keep faces, scale, composition and all unaffected objects fixed. Rewrite
  the spatial correction for the current image (target, direction, open/closed
  state); do not copy left/right directions from an older composition.
- Reopen only the requested page with `--revise-page --task-id ... --detail ...`.
  This archives the original, makes that page pending, and blocks PDF assembly.
  Normal candidate QA promotes the replacement; `--cancel-revision` restores
  the original. Do not manually replace files under `images/`.
- A corrected candidate must still pass the whole page contract: local edits
  can introduce regressions elsewhere. Inspect only affected neighboring pages
  for continuity; retain valid approvals for all unchanged image hashes.
- On high-risk checks, record what is visible, where, and why it passes. For
  weapon counts, orientation and height, use original-detail views/crops and
  measurable evidence where feasible. Boilerplate such as "requirement
  satisfied" is insufficient evidence. Uncertain measurements remain review
  items; do not claim precise ratios without a defensible ground plane.
- Build both languages from the same frozen input set. `release_manifest.json`
  binds image bytes, complete bilingual text, fonts, renderer, story manifest
  and PDF hashes. New builds start at `awaiting_pdf_review`, not `released`.
- Review rendered pages of the actual PDFs, including captions and footers.
  Then use `--approve-release --detail ...` to record that review. This verifies
  the frozen inputs, quality gate and actual PDF page counts again. Never run
  it merely because generation succeeded.
- User approval of current artwork is authoritative. If QA records are stale,
  inspect the current bytes and record a new hash-bound review; do not regenerate
  approved artwork or fabricate historical reports to repair bookkeeping.

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
5. For every final scene, freeze a structured `qa` contract covering required
   and forbidden entities, exact counts, identity states, relationships,
   weapons, props, height rules, and reference bindings as applicable.
6. Generate one full-page candidate per pending task with the selected image tool,
   using only its frozen 0–3 upload proxies; import it with
   `--import-candidate` immediately.
7. Review each candidate with the available image-viewing/vision capability at original
   detail. Record a structured QA report. Promote only passing candidates;
   automatically retry failures up to three attempts.
8. Resume after interruption with `--resume --prompts-only`. Generate only the
   tasks still marked pending by fresh filesystem validation.
9. Build both PDFs only after `--quality-status` reports `pass`, using explicit
   non-generic Chinese and English footers:
   - Chinese: `storybook.pdf`
   - English: `storybook_en.pdf`
10. Verify page count, image count, progress timings, `pdf_validation.json`,
    and every rendered Chinese/English PDF page; record the final release review.

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
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --project-dir /absolute/path/to/story-project \
  --output-dir /absolute/path/to/story-project/build/storybook_draft \
  --draft \
  --scene-count auto \
  --prompts-only
```

Create the final 12–24-page generation plan after approving the draft:

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --project-dir /absolute/path/to/story-project \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --scene-count auto \
  --footer-zh '系列名 · 第N章 · 中英双语绘本' \
  --footer-en 'Series Name · Chapter N · Bilingual Storybook' \
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
--reference-spec /absolute/path/to/series/references.json \
--reference-root /absolute/path/to/series
```

Do not pass `--reference-spec` on resume; the output's frozen reference snapshot
is authoritative.

Before and after each selected image-tool call, record timing:

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --progress-event generation_started \
  --task-id scene-01-<hash>

# Call the selected image tool exactly once for this task.

python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --progress-event generation_returned \
  --task-id scene-01-<hash>
```

Import the exact PNG persisted by that call as an unapproved candidate:

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --import-candidate "<image-output-dir>/<call-id>/<generated>.png" \
  --task-id scene-01-<hash>
```

The command returns a project-local candidate path, SHA-256, required check
IDs, and a QA template. Use the image-viewing tool to open the candidate at
original detail and compare it with every task reference. Fill the template;
do not infer a passing result from file validity.

Record the structured review and promote only when all required checks pass:

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --qa-report /absolute/path/to/completed-qa-report.json \
  --candidate-sha256 <candidate-sha256> \
  --task-id scene-01-<hash>
```

For a failed report, use the returned `retry_prompt`. When
`strategy_change_required` becomes true, do not repeat the same prompt/reference
combination: replace a contaminated reference, use a state-specific character
reference, simplify the composition, or edit the closest candidate. Stop after
three failed attempts and mark only that page for human exception review.

Archive a rejected result once, by content hash, without making it a future
reference:

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --archive-rejected "<image-output-dir>/<call-id>/<rejected>.png" \
  --task-id scene-01-<hash> \
  --detail "character continuity failed"
```

All rejected images share one content-addressed
`<output-dir>/rejected_attempts/` directory. Do not copy them into draft/final
build clones or add them to reference specs automatically.

Resume without rescanning or re-inferring the source:

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --resume \
  --prompts-only
```

For a pre-v2 manifest with no `plan_sha256`, add
`--migrate-legacy-manifest` to that resume command exactly once.

Build PDFs only after every expected PNG validates:

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --quality-status

python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --use-existing-images \
  --language both
```

For a text-only revision, use a caption plan and `--pdf-only`. This path reads
the frozen manifest and verified images, writes PDFs, release/validation records and progress events,
and does not rewrite `manifest.json`, `generation_tasks.json`, references, or
send images:

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/story-project/build/storybook_auto \
  --pdf-only \
  --captions-plan /absolute/path/to/story-project/captions.json \
  --language both
```

Run a placeholder-only layout check in a separate directory:

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" \
  --project-dir /absolute/path/to/story-project \
  --output-dir /absolute/path/to/story-project/build/storybook_dryrun \
  --scene-count auto \
  --dry-run \
  --language both
```

## Structured Visual Quality Gate

Every scene in a new final scene plan must include a machine-readable `qa`
object. Use concrete canonical entity IDs, not vague prose:

```json
{
  "qa": {
    "risk_level": "high",
    "required_entities": ["hero", "guide"],
    "forbidden_entities": ["horse", "extra_guard"],
    "exact_counts": {"hero": 1, "guide": 1},
    "identity_states": {"hero": "gray_cave_guard_disguise"},
    "relationships": ["hero stands beside guide on the same ground plane"],
    "weapons": {"hero": "fully out of frame"},
    "props": {"golden_rope": 1},
    "height_rules": ["guide remains visibly taller than hero"],
    "custom_checks": ["all garments fully cover the torso"],
    "reference_bindings": {
      "group-height": {
        "use_for": ["height only"],
        "do_not_copy": ["other group members", "background"],
        "notes": "Do not copy absent characters from this lineup."
      }
    }
  }
}
```

The helper emits a QA template for each candidate. Replace every `pending`
result after actual visual inspection. A passing report must set every required
check to `pass`; `not_applicable` cannot be used to bypass a required contract.
Use short stable failure codes such as `extra_character`, `wrong_identity`,
`height_ratio`, `weapon_shape`, `prop_count`, `anatomy`, `layout`, or
`readable_text` so repeated failures can trigger a strategy change.

The reviewer must be evidence-driven. Inspect the candidate itself, not the
prompt alone. For high-risk scenes, do two separate reviews: first the scene
contract at original detail, then cross-page continuity in a contact sheet.
When uncertain, use `needs_review`; never manufacture a passing report merely
to unblock PDF creation.

## Image Generation Procedure

The helper intentionally does not call image APIs. Do not add API-backed
generation to it.

For each pending entry in `generation_tasks.json`:

1. Claim one stable `task_id`; do not generate a second attempt while the first
   call may still be live.
2. Record `generation_started`.
3. Call the selected image tool exactly once with that task's exact prompt and
   reference images, mapped to the tool's documented parameters. For Codex
   ImageGen, use `referenced_image_paths`, omit reference arguments when empty,
   and omit `num_last_images_to_include` when explicit reference paths are used.
4. Record `generation_returned` or `generation_failed`.
5. Establish call-scoped source provenance. In serial directory-diff mode,
   require exactly one new readable PNG. In parallel mode, use only the exact
   per-call path or the worker's exclusive session subtree.
6. Run `--import-candidate <source> --task-id <id>`.
7. Open the candidate and its exact references with the image-viewing tool at
   original detail. Check every emitted QA item and write a structured report.
8. Run `--qa-report <report> --candidate-sha256 <sha> --task-id <id>`.
9. Continue only when the command reports `approved`. On `fail`, use its retry
   prompt and keep the final image path empty. Never rename a candidate into
   `images/` manually.
10. After all scene-level approvals, inspect a full chapter contact sheet for
    identity, costume, weapon, height, color, and world continuity. Re-review
    any outlier at original detail before PDF assembly.

After interruption, rerun `--resume --prompts-only`; trust fresh PNG validation,
not old progress events. Do not compress distinct scenes into variants of one
prompt. Generate one image per scene.

Keep the selected provider for the whole run unless the user requests a change.
If the tool cannot save a readable PNG under the configured source directory, stop
and report the failure. Never assemble final PDFs from missing, placeholder or
preview-only images.

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
