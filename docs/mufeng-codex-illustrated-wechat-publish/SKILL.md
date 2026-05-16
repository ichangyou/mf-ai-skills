---
name: mufeng-codex-illustrated-wechat-publish
description: Use when turning source materials in a directory into a professional WeChat Official Account article with mufeng-blog-writing, then adding Codex-generated PNG cover and inline illustrations, uploading images to a GitHub image host, inserting raw GitHub image URLs into the article, and publishing it to WeChat.
---

# Mufeng Codex Illustrated WeChat Publish

## Core Rules

- Start from the materials in the requested directory, not from a blank topic. Generate the article first with the `mufeng-blog-writing` skill's article-writing conventions.
- Use Codex built-in image generation for all new cover and illustration images. Do not call OpenAI Images API, `baoyu-image-gen`, Google, DashScope, or other image CLIs unless the user explicitly asks to switch.
- Save generated images as PNG. If a generated asset is not PNG, convert it to PNG before upload.
- Keep generated images free of readable UI text, Chinese text, labels, captions, watermarks, and signatures unless the user explicitly requests text in the image. Put titles/captions in Markdown instead.
- Upload the cover and all inline illustrations to GitHub image hosting, then insert `https://raw.githubusercontent.com/...` URLs into the Markdown article.
- Publish from the final Markdown file. Do not pre-convert Markdown to HTML before calling the WeChat publishing script.

## Workflow

1. Locate source materials and generate the article.
   - If the user gives a directory, use that directory. Otherwise use the current working directory.
   - Treat Markdown, text notes, transcripts, outlines, code snippets, screenshots/OCR notes, and other user-provided files in that directory as source material.
   - Ignore build/cache/vendor folders, generated image folders, previous WeChat output folders, and existing `github-image-urls.json` files.
   - Read the `mufeng-blog-writing` skill and follow its workflow, tone, structure, metadata, and footer rules.
   - Generate a professional Chinese WeChat Official Account article as Markdown. It should be publish-ready, with frontmatter `title`, `author: changyou`, `date: YYYY-MM-DD`, a clear `#` title, summary, tags, and practical structure.
   - Save the generated Markdown article in the requested directory unless the user specifies another output path. If a target filename already exists, append `-v2`, `-v3`, etc. rather than overwriting.
   - The generated article becomes the target article for all later steps.

2. Read the generated article and make an image plan.
   - Use one cover image.
   - Add inline illustrations at natural breakpoints: after the opening setup, before dense technical sections, or after major H2 sections.
   - Avoid inserting images inside code blocks, tables, lists, blockquotes, or YAML frontmatter.
   - For short articles, use 1-2 inline illustrations. For long articles, use roughly one illustration per 600-900 Chinese characters or per major section, capped unless the user asks for many.

3. Generate PNG images with Codex image generation.
   - Recommended local layout: `imgs/<article-slug>/cover.png`, `imgs/<article-slug>/fig-01.png`, `imgs/<article-slug>/fig-02.png`.
   - Cover prompt: ask for a wide 2.35:1 or 16:9 editorial/tech composition with clear focal area and no text.
   - Illustration prompts: make each image explain the nearby idea visually, not generic decoration.
   - If the article is technical, prefer diagrams, metaphors, product/workflow scenes, or abstract system visuals that match the surrounding section.

4. Validate image files.
   - Confirm each generated image exists, is non-empty, and is PNG.
   - Prefer keeping each PNG under 5 MB. Compress or resize only if upload/publish tools reject the file.

5. Upload images to GitHub.
   - Preferred config:
     - `MUFENG_GITHUB_IMAGE_REPO=owner/repo`
     - `MUFENG_GITHUB_IMAGE_BRANCH=main`
     - `MUFENG_GITHUB_IMAGE_DIR=images/mufeng`
   - If the repo cannot be discovered from env/config, ask once for `owner/repo`.
   - Use the bundled helper:

```bash
python3 "$HOME/.agents/skills/mufeng-codex-illustrated-wechat-publish/scripts/upload_github_images.py" \
  --repo "$MUFENG_GITHUB_IMAGE_REPO" \
  --branch "${MUFENG_GITHUB_IMAGE_BRANCH:-main}" \
  --remote-dir "${MUFENG_GITHUB_IMAGE_DIR:-images/mufeng}/<article-slug>" \
  --json-out "imgs/<article-slug>/github-image-urls.json" \
  imgs/<article-slug>/cover.png \
  imgs/<article-slug>/fig-01.png
```

6. Insert image URLs into the generated Markdown article.
   - Add or update frontmatter with `coverImage: <cover-url>`.
   - Insert the cover near the top of the article only if the user asked for the cover to appear in the article body; otherwise use it as publishing metadata.
   - Insert inline illustrations as normal Markdown images:

```markdown
![短描述](https://raw.githubusercontent.com/OWNER/REPO/main/images/mufeng/article/fig-01.png)
```

   - Use concise alt text that describes the idea, not `image1`.
   - Preserve existing user content and formatting.

7. Publish to WeChat Official Account.
   - Read `$HOME/.baoyu-skills/baoyu-post-to-wechat/EXTEND.md` if present for defaults.
   - Prefer API publishing unless the user or config chooses browser publishing.
   - Use the existing baoyu script directly:

```bash
bun /Users/changyou/.claude/plugins/marketplaces/baoyu-skills/skills/baoyu-post-to-wechat/scripts/wechat-api.ts \
  <article.md> \
  --theme default \
  --author changyou \
  --cover <cover-url>
```

   - Always include a title if it cannot be reliably extracted from frontmatter or the first H1.
   - If API publishing fails with IP/auth errors, check the current outbound IP and WeChat IP whitelist before retrying.

## GitHub Upload Notes

- The helper uses `gh api`; GitHub CLI must be installed and authenticated.
- It rejects non-PNG files by default.
- If a remote path already exists, it appends a timestamp suffix unless `--overwrite` is passed.
- Raw URLs are printed and optionally saved to JSON for precise insertion.

## Completion Report

Report:

- Source material directory used.
- Generated article path.
- Article path changed.
- Cover URL and inline image URLs.
- WeChat publishing method and result, including draft `media_id` if the API returns one.
- Any skipped step or manual action still required.
