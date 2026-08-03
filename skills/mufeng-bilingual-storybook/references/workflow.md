# Mufeng Bilingual Storybook Workflow

## Contents

- Output shape
- Image-generation policy
- Project scan safety
- Page-count policy
- Frozen plan and resume
- Reference assets and traffic control
- Progress events
- Safe import transaction
- Rejected-attempt archive
- Optional concurrency
- Scene-plan and prompt rules
- PDF rules and validation
- Text-only PDF rebuild

## Output Shape

Use this structure for a formal bilingual picture-book chapter:

- `build/storybook_auto/scenes.parsed.md`
- `build/storybook_auto/prompts.generated.md`
- `build/storybook_auto/manifest.json`
- `build/storybook_auto/generation_tasks.json`
- `build/storybook_auto/reference_manifest.json` when references are used
- `build/storybook_auto/quality_gate.json`
- `build/storybook_auto/progress.jsonl`
- `build/storybook_auto/candidates/<task-id>/<sha256>.png`
- `build/storybook_auto/qa_reports/<task-id>/<sha256>.json`
- `build/storybook_auto/images/scene_01_title.png` ... `scene_N_title.png`
- `build/storybook_auto/rejected_attempts/<sha256>.png` for explicitly archived
  rejected results
- `build/storybook_auto/storybook.pdf`
- `build/storybook_auto/storybook_en.pdf`
- `build/storybook_auto/pdf_validation.json`
- `build/storybook_auto/preview/final/zh/page_01.png` ...
- `build/storybook_auto/preview/final/en/page_01.png` ...
- `.mufeng-storybook/references/master/` for one shared copy of each original
- `.mufeng-storybook/references/upload/` for 1024px JPEG upload proxies
- `.mufeng-storybook/references/catalog.json` for the project-wide hash lock

Use `build/storybook_auto_dryrun/` only for placeholder layout validation.
Use a separate `build/storybook_draft/` for the 6- or 8-page review draft.

For a forced 20-page version, use `--scene-count 20 --output-dir build/storybook_20`.

## Image Generation Policy

All live artwork generation must use Codex built-in `image_gen` only.

Forbidden for this skill:

- Google/Gemini image APIs and `GOOGLE_API_KEY`.
- Local Google provider modules, including provider code under `baoyu-image-gen`.
- OpenAI Images API, `OPENAI_API_KEY`, or ad hoc SDK clients.

If any old note recommends a Google provider fallback, ignore it. If Codex built-in `image_gen` is unavailable, report the block instead of switching providers.

The helper never calls `image_gen` or a vision API. It prepares text, a frozen
manifest, generation tasks, candidate transactions, structured QA records,
progress events, and PDF assembly outputs. Codex performs visual inspection by
opening candidate and reference images with its image-viewing capability.
`--prompts-only` creates prompts but no artwork; `--dry-run` creates tagged
placeholder layout checks but no final artwork.

For real artwork, call built-in `image_gen` once per attempt. Use the exact
prompt, stable `task_id`, and exact `referenced_image_paths` from
`generation_tasks.json`. If that list is non-empty, pass it as
`referenced_image_paths` and omit `num_last_images_to_include`; if it is empty,
omit both reference arguments. Record timing around the call, establish
call-scoped source provenance, and import through `--import-candidate`. Do not
copy or rename anonymous parallel results manually. Only `--qa-report` with a
fully passing structured review can promote that candidate hash into `images/`.

If an image appears in the conversation but no new PNG is persisted under
`${CODEX_HOME:-$HOME/.codex}/generated_images/`, stop and report a Codex runtime
persistence failure. Do not substitute screenshots, placeholders, SVGs, Google,
Gemini, `baoyu-image-gen`, OpenAI Images API, or any other fallback.

## Project Scan Safety

Pass the smallest directory containing the story Markdown as `--project-dir`.
Keep `--output-dir` inside that project. The helper rejects the resolved user
home, filesystem root, and out-of-project output paths.

For a multi-chapter series, also pass `--reference-root` as the nearest series
ancestor. It must contain the chapter project and output. Reference specs and
source paths resolve against that root, so canonical IDs and hashes stay stable
across chapters while Markdown scanning remains chapter-local.

The scanner uses `os.walk(..., topdown=True, followlinks=False)` and prunes
hidden directories, `build`, `cache`, `dist`, `node_modules`, `vendor`, virtual
environments, and the resolved output directory before descent. It skips
symlinked Markdown files so source discovery cannot escape the project. Do not
weaken these guards to make a broad scan succeed.

Resume and final PDF assembly load the existing manifest and do not rescan the
source. This prevents changed source Markdown from silently changing prompts,
filenames, or scene-to-image mappings during a long run.

## Page Count Policy

Use `--scene-count auto` unless the user gives an exact number. Auto mode chooses one of four page counts and records the decision in `manifest.json` under `scene_count_info`.

- 12 pages: short story / compact single episode
- 16 pages: medium chapter / several clear beats
- 20 pages: formal picture-book chapter
- 24 pages: long or complex chapter

For a review draft, add `--draft`:

- final auto count 12 or 16 -> 6-page draft
- final auto count 20 or 24 -> 8-page draft

In draft mode, a manual count or supplied scene plan must be exactly 6 or 8.
Approve the draft scene structure, then generate the formal plan in a separate
output directory without `--draft`.

The helper script makes this deterministic from Markdown metrics: CJK character count, Latin word count, paragraph count, sentence count, heading count, and a combined complexity score. It uses body length and paragraph complexity as the primary signal so classical Chinese short sentences do not inflate the page count by themselves. If Codex has already authored a `--scene-plan`, the number of JSON scene items overrides `--scene-count`.

Current auto thresholds:

- 12 pages: up to 1400 narrative units, 18 paragraphs, and 60 sentences
- 16 pages: up to 2800 narrative units, 30 paragraphs, and 100 sentences
- 20 pages: up to 5500 narrative units, 85 paragraphs, and 190 sentences
- 24 pages: anything longer or structurally more complex

## Frozen Plan And Resume

`manifest.json` is canonical after prompt preparation. It contains a
`plan_sha256`; `generation_tasks.json` must carry the same hash. Do not import
artwork if those hashes differ.

Require scene numbers and expected filenames to remain unique after Unicode
normalization and case folding; macOS commonly treats case-only filename
differences as the same file. Validate each task's exact prompt as well as its
prompt hash against the manifest before importing artwork.

Manifest v2 and later must contain a valid 64-character plan SHA-256. New
outputs use manifest v4. They freeze the scene `qa` contracts, book footer
metadata, and whether the visual quality gate is required; referenced outputs
also freeze `reference_manifest_sha256`. Migrate a pre-v2, hashless manifest explicitly:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/build/storybook_auto \
  --resume \
  --migrate-legacy-manifest \
  --prompts-only
```

The helper validates the legacy pages, writes a current manifest with a frozen hash,
and logs `legacy_manifest_migrated`. Never add or remove the hash manually.

Resume with:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/build/storybook_auto \
  --resume \
  --prompts-only
```

The helper reconstructs scenes from the manifest, recomputes safe paths beneath
the current output directory, validates every exact PNG, and rewrites the task
summary. Plan/resume writes and import-time refreshes share the same
cross-process lock; the writer performs a final filesystem check while holding
that lock so an older scan cannot downgrade a concurrent import to pending. It
does not reread Markdown.

For legacy outputs, `complete` means only that the exact expected target:

- is a regular non-symlink file;
- has a PNG signature and decodes as PNG;
- remains unchanged during validation;
- has positive dimensions;
- is not tagged as a dry-run placeholder.

For new final outputs, filesystem completeness is not publication approval.
The final PNG hash must also have a passing report in `quality_gate.json` whose
QA-contract hash matches the frozen scene. Keep corrupt or partial files in
place for diagnosis. Never overwrite a valid existing target. If a new scene
plan conflicts with valid artwork in the same output directory, use a new
output directory.

## Reference Assets And Traffic Control

References are opt-in. The scene plan names stable reference IDs; it never names
arbitrary upload paths. The initial planning run may add IDs through a
project-local spec:

```json
{
  "schema_version": 1,
  "references": [
    {"id": "hero-master", "path": "assets/hero.png", "role": "master"},
    {"id": "weapon", "path": "assets/weapon.png", "role": "continuity"},
    {"id": "visual-style", "path": "assets/style.png", "role": "style"}
  ]
}
```

Reference IDs use lowercase ASCII letters, digits, `_`, and `-`; the first
character must be a letter. Roles are `master`, `continuity`, or `style`.
Source images must be regular, decodable, single-frame project files. Symlinked,
out-of-project, empty, animated, or decompression-bomb inputs are rejected.

The helper copies a newly accepted source byte-for-byte into the one shared
project library at `.mufeng-storybook/references/master/`. It then makes one
derived upload proxy:

- JPEG, RGB
- longest edge no greater than 1024px; never upscale
- quality 85, progressive and optimized
- EXIF and other source metadata omitted
- transparent pixels flattened on white

The master and proxy are content-addressed and recorded in the project catalog.
An existing ID is a SHA-256 contract: changed source bytes or role are rejected.
This detects changes but does not make files physically immutable. Recover a
missing/tampered proxy from backup; do not silently re-encode a frozen ID across
environments.

Each scene may list at most three unique IDs, and two should be the normal
ceiling:

```json
{
  "number": 1,
  "references": ["hero-master", "weapon"]
}
```

The output's `reference_manifest.json` contains only the union used by that
plan. Each generation task freezes ordered reference records with role,
absolute upload path, SHA-256, dimensions, and bytes. `load_generation_plan`
revalidates these files before logging, importing, or archiving an attempt.
Once an output freezes a reference snapshot, the same ID cannot be rebound to
different bytes there; use a new output directory for a changed reference plan.

Use only these proxies for ImageGen. Do not attach originals, rejected attempts,
all prior pages, or implicit conversation images. A current task cannot
dynamically adopt a just-generated page without changing the frozen protocol;
prepare and approve continuity references before the plan is frozen.

The task field `reference_payload_bytes` is the sum of local proxy sizes for one
attempt. The summary field
`planned_reference_payload_bytes_per_pending_pass` is the same sum across all
currently pending tasks. These are controllable local payload sizes, not
observed upload traffic. They exclude retries, encoding/transport overhead,
client-added context, download traffic, cloud/backup sync, and other sessions.
Do not claim they prove any 200–500MB total. If an OS reports 5–6GB, inspect
client retries/context, process attribution, and sync software separately.

## Progress Events

`progress.jsonl` is append-only. The helper automatically records source or
manifest loading, output preparation, every filesystem image status, import
results, PDF timings, and final status.

Record ImageGen time explicitly:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/build/storybook_auto \
  --progress-event generation_started \
  --task-id scene-01-<hash>

# Call built-in image_gen once.

python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/build/storybook_auto \
  --progress-event generation_returned \
  --task-id scene-01-<hash>
```

Use `generation_failed` when the tool call fails. Use `persistence_failed` when
the tool displays an image but its call-scoped persisted source cannot be
proved. Finish/failed events include elapsed time from the latest start event.
Progress history aids diagnosis but never overrides fresh filesystem
validation.

Every manually recorded generation event includes `reference_count` and
`local_reference_payload_bytes` from the frozen task. Repeated
`generation_started` records make retries visible, but these values still
describe local input files rather than measured wire bytes.

## Candidate Import And Visual QA Transaction

Import only a source below
`${CODEX_HOME:-$HOME/.codex}/generated_images/`:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/build/storybook_auto \
  --import-candidate "$HOME/.codex/generated_images/<session>/<result>.png" \
  --task-id scene-01-<hash>
```

The helper:

1. verifies task/manifest hash agreement;
2. requires a matching `generation_started`/`generation_returned` cycle;
3. rejects sources outside the built-in generated-images root;
4. rejects symlinked, corrupt, empty, changing, non-PNG, or placeholder files;
5. copies into `<output-dir>/candidates/<task-id>/<sha256>.png`;
6. verifies the project-local candidate hash;
7. emits a QA template containing every built-in and scene-specific check;
8. leaves the final `images/` target empty.

Open the candidate and exact task references at original detail, complete the
template, and record it:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/build/storybook_auto \
  --qa-report /absolute/path/to/completed-report.json \
  --candidate-sha256 <sha256> \
  --task-id scene-01-<hash>
```

A `pass` report is accepted only if every required check is `pass`. The helper
copies the exact candidate bytes to the final filename, records candidate and
QA-contract hashes, then refreshes task status. `fail` archives the candidate
and returns a corrective retry prompt. `needs_review` never promotes artwork.
After the same failure category occurs twice, change references or composition
instead of resubmitting the same strategy. Stop after three failed attempts and
escalate only that scene.

`generation_started` is rejected if the exact task target is already a valid
PNG. This closes the gap between import and the next resume so a loop that
reloads `generation_tasks.json` cannot mistake a completed import for pending.

`--import-image` remains only for legacy manifests whose quality gate is not
required. The CLI refuses it for new final manifests.

## Rejected-Attempt Archive

If a persisted PNG is valid but visually rejected, archive it explicitly:

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/build/storybook_auto \
  --archive-rejected "$HOME/.codex/generated_images/<session>/<result>.png" \
  --task-id scene-01-<hash> \
  --detail "wrong costume"
```

The helper validates the frozen task and generated-images source, then stores
one content-addressed copy at `rejected_attempts/<full-sha256>.png`. The same
bytes archived for any task remain one file; task/scene/reason relationships
live in `progress.jsonl`. It never deletes the generated source, writes into
`images/`, copies a rejected directory into other builds, or adds rejected art
as a reference.

## Optional 2-4 Worker Concurrency

Stay serial unless provenance isolation is available:

```bash
# Safe default
--concurrency 1 --mapping-mode directory-diff

# Allowed only when the runtime returns each call's exact persisted path
--concurrency 2 --mapping-mode per-call-path

# Allowed only when every worker owns a distinct session subtree
--concurrency 2 --mapping-mode isolated-worker-dir
```

The helper rejects parallel shared-directory diff mode. It plans and validates
tasks but does not launch ImageGen or prove runtime provenance; the Codex
orchestrator must enforce the following protocol:

1. Assign disjoint task IDs to at most four workers.
2. Keep at most one ImageGen call in flight per worker.
3. For `per-call-path`, require the tool result to identify one exact readable
   source path below generated-images.
4. For `isolated-worker-dir`, qualify workers serially using real assigned
   scenes. Pin one distinct session subtree per worker; require exactly one new
   PNG per call within that subtree.
5. Never use global newest-file, mtime, completion order, prompt order, or
   visual similarity as attribution.
6. Import with the assigned `task_id` immediately after each call.
7. If directories collide, a call yields zero or multiple candidates, or the
   runtime does not guarantee stable isolation, record `persistence_failed`,
   stop launching parallel calls, and fall back to one serial worker.
8. Never retry while an earlier call for the same task may still be running.

On interruption, allow in-flight calls to become terminal before reassigning
their tasks. Rerun `--resume --prompts-only`; regenerate only tasks whose exact
project-local targets remain pending.

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
    "prompt": "Full image prompt. No text in image.",
    "references": ["hero-master", "weapon"],
    "qa": {
      "risk_level": "high",
      "required_entities": ["hero"],
      "forbidden_entities": ["horse", "extra_guard"],
      "exact_counts": {"hero": 1},
      "identity_states": {"hero": "canonical costume"},
      "weapons": {"hero": "fixed weapon visible"},
      "props": {"lantern": 1},
      "height_rules": ["hero remains shorter than guide"],
      "custom_checks": ["hands and face are anatomically coherent"],
      "reference_bindings": {
        "hero-master": {
          "use_for": ["identity only"],
          "do_not_copy": ["background", "other figures"],
          "notes": "Keep only the canonical hero identity."
        }
      }
    }
  }
]
```

Keep narration short enough for two PDF lines. Use the auto-selected count
unless the user requests another count. Do not deliver the helper's inferred
English (`Scene N.`) as translation; automatic inference is only a structural
layout preview. Every supplied final scene plan must define a non-empty `qa`
contract for every scene. Use stable entity IDs consistently across the whole
series.

## Prompt Rules

Each image prompt should include:

- Use case: `illustration-story`
- Asset type: one page illustration for a formal children's picture book
- Scene title and visual brief
- Style continuity
- Character continuity
- World continuity
- Constraints: no readable text, captions, labels, speech bubbles, borders, or watermark
- Generation policy: use Codex built-in `image_gen` only; no Google/Gemini/API/provider fallback

For inscriptions, tablets, signs, plaques, scrolls, or carved stones, request abstract decorative marks only.

## PDF Rules

Use the same images for both languages. Only the title line, narration, footer, and PDF filename change.

Chinese:

- PDF: `storybook.pdf`
- Footer: explicit series/chapter title such as `西游记 · 第一回`; generic final
  values such as `绘本` are rejected
- Font rule: render Chinese page titles with `Songti.ttc` index `6`
  (`Songti SC Regular`), and Chinese captions/footer with `Songti.ttc` index
  `3` (`Songti SC Light`). Never rely on the default `Songti.ttc` index because
  it maps to `Songti SC Black` and makes the PDF text too heavy.
- Regression check: inspect common problem characters after rendering,
  especially `着`, `将`, `起`, `径`, and phrases such as `造起`.

English:

- PDF: `storybook_en.pdf`
- Footer: explicit series/chapter title such as
  `Journey to the West - Chapter 1`; generic `Storybook` is rejected

Store both footers during initial planning with `--footer-zh` and
`--footer-en`. They are frozen in manifest book metadata and reused by
`--pdf-only`. An explicit later override is allowed but still cannot be generic.

## Text-Only PDF Rebuild

After artwork is frozen, text changes must not re-enter the generation workflow.
Use a narrow caption override:

```json
{
  "schema_version": 1,
  "pages": [
    {
      "number": 1,
      "title_zh": "新标题",
      "title_en": "New Title",
      "narration_zh": "修订后的中文旁白。",
      "narration_en": "Revised English narration."
    }
  ]
}
```

Only `number`, `title_zh`, `title_en`, `narration_zh`, and `narration_en` are
allowed. Prompt, description, expected-image, and reference changes are
rejected.

```bash
python3 "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --output-dir /absolute/path/to/build/storybook_auto \
  --pdf-only \
  --captions-plan /absolute/path/to/captions.json \
  --language both
```

This branch loads the frozen manifest, validates every final PNG, applies text
to in-memory scene copies, and atomically replaces only requested PDFs. Apart
from append-only progress, it does not write `manifest.json`,
`generation_tasks.json`, `reference_manifest.json`, or reference assets and
does not call or prepare ImageGen.

## Validation

Always check:

```bash
file build/storybook_auto/storybook.pdf build/storybook_auto/storybook_en.pdf
find build/storybook_auto/images -maxdepth 1 -type f -name '*.png' | wc -l
python3 -m json.tool build/storybook_auto/manifest.json >/dev/null
python3 -m json.tool build/storybook_auto/generation_tasks.json >/dev/null
```

The helper renders every page to `preview/final/zh/` and
`preview/final/en/` while creating the PDFs. It also writes
`pdf_validation.json` with page count, footers, output hashes, and preview root.
Use `pdftoppm` only as an independent spot check when available:

```bash
mkdir -p build/storybook_auto/preview
pdftoppm -f 1 -l 1 -png -r 100 build/storybook_auto/storybook.pdf build/storybook_auto/preview/page_zh
pdftoppm -f 1 -l 1 -png -r 100 build/storybook_auto/storybook_en.pdf build/storybook_auto/preview/page_en
```

Inspect the complete preview set and a contact sheet for:

- No accidental ellipses in short titles
- No text overlap
- Page number correct
- Footer title short and natural
- Captions not clipped
- Chinese glyphs render correctly without excessive boldness

Also verify:

- `manifest.json` and `generation_tasks.json` have the same `plan_sha256`
- referenced plans have matching manifest/snapshot/task reference hashes and no
  task has more than three `referenced_image_paths`
- task summary reports zero pending pages before final PDF assembly
- payload fields are described as local bytes, never as measured upload traffic
- every line in `progress.jsonl` parses as one JSON object
- every `generation_started` has a terminal returned/failed/persistence event
- no unexpected PNG was adopted by filename or completion order
- `--quality-status` reports `pass` and every final image hash has a matching
  passing QA record
- every supplied final scene has a non-empty structured QA contract
- no generic footer is present and `pdf_validation.json` matches the PDFs
