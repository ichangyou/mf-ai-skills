# Existing chapter revisions and final release

Use the helper path from SKILL.md and the chapter's existing output directory.
The frozen scene contract remains authoritative. If the requested change alters
story meaning, scene entities or references, create a deliberately updated plan;
`--revise-page` is for correcting artwork within the existing scene contract.

## Text first

Run `--output-dir <build> --preflight-text --language both` after planning and
before ImageGen. Add `--captions-plan <json>` to check proposed text overrides.
The check uses the rendering fonts and widths, requires one title line and no
more than two narration lines, and rejects oversized unbroken words.
For text-only changes, run `--pdf-only --captions-plan <json> --language both`.
This does not invalidate unchanged artwork approvals.

## One image revision

1. Run `--output-dir <build> --revise-page --task-id <id> --detail "specific defect"`.
   Save the returned backup path as the edit target. The original remains in
   `revisions/<task-id>/<hash>.png`; its former final path becomes pending.
2. Inspect the backup and mandatory project references. Prefer localized editing
   for a mouth direction, finger, tine or other isolated defect. Preserve all
   unaffected features. Whole-image regeneration is for global composition,
   identity or narrative failures.
3. Record the normal generation start/return events, import the new candidate,
   inspect it and submit the normal full-page QA report. Failed candidates leave
   the previous original recoverable and never become PDF inputs.
4. Passing QA promotes the new image and closes the active revision. Other pages
   retain their existing hash-bound reviews. To abandon an unfinished revision,
   run `--cancel-revision --task-id <id>`; this restores the exact original.
5. Run quality status and inspect affected cross-page continuity before rebuilding.

Keep one mutation command active at a time for a chapter. Do not revise the
same page from concurrent sessions. The revision reason is supplemental edit
instruction; generation_tasks.json continues to hold the frozen base prompt.

## Final bilingual release

Run `--pdf-only --language both` once the quality gate passes. The helper checks
all text before writing either language, verifies actual PDF page counts, and
writes `release_manifest.json` with status `awaiting_pdf_review`.

Render the actual PDF pair with an available PDF renderer and inspect every
page, including page order, current image revisions, complete captions, glyphs,
footers and page numbers. The helper's preview PNGs are rendering inputs, not
proof that the actual PDF renders correctly.

After that review, run `--approve-release --detail "what was visually checked"`.
This verifies hashes and marks the exact artifact set released. Any later image,
caption-plan, manifest, font, renderer or PDF change requires rebuilding and
reviewing again. Old PDFs may remain readable while a revision is pending;
they must not be described as current releases.

Actual PDF verification requires pypdfium2 (also checks each page decodes) or
system pdfinfo (page count); visual review of actual rendered PDFs is required
in either case. No image-generation API or provider fallback is introduced.
