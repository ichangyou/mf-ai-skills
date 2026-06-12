---
name: mufeng-materials-to-wechat-publish
description: Use when source materials in a directory, such as notes, drafts, transcripts, screenshots, outlines, or code snippets, need to be turned into a professional WeChat Official Account article with mufeng-blog-writing, SEO/GEO-friendly Markdown metadata, generated PNG cover and inline illustrations, GitHub-hosted raw image URLs, and WeChat publishing. Do not use for an already-finished article that only needs publishing; use mufeng-wechat-publish-full for that.
---

# Mufeng Materials To WeChat Publish

## Core Rules

- Use this skill for the materials-to-article workflow. If the user already has a finished Markdown article and only needs image upload, formatting, API publishing, or publish recovery, use `mufeng-wechat-publish-full` instead.
- Start from the materials in the requested directory, not from a blank topic. Generate the article first with the `mufeng-blog-writing` skill's article-writing conventions, with this skill's frontmatter requirements taking precedence.
- Every generated Markdown article must include SEO/GEO-friendly YAML frontmatter with `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and later `coverImage`.
- Use Codex built-in image generation for all new cover and illustration images. Do not call OpenAI Images API, `baoyu-image-gen`, Google, DashScope, or other image CLIs unless the user explicitly asks to switch.
- Save generated images as PNG. If a generated asset is not PNG, convert it to PNG before upload.
- Keep generated images free of readable UI text, Chinese text, labels, captions, watermarks, and signatures unless the user explicitly requests text in the image. Put titles/captions in Markdown instead.
- Upload the cover and all inline illustrations to GitHub image hosting, then insert `https://raw.githubusercontent.com/...` URLs into the Markdown article.
- Publish from the final Markdown file. Do not pre-convert Markdown to HTML before calling the WeChat publishing script.

## Execution Contract

Inputs:
- A source-material directory, or the current working directory if no directory is given.
- Source files may include Markdown, text notes, transcripts, outlines, screenshots/OCR notes, code snippets, and drafts.
- Optional user constraints such as target angle, title preference, image count, output filename, or whether to stop before publishing.

Outputs:
- A publish-ready Markdown article saved in the source directory, usually as `<article-slug>.md`.
- SEO/GEO-friendly frontmatter with `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and uploaded `coverImage`.
- Local PNG images under `imgs/<article-slug>/`.
- Uploaded raw GitHub image URLs under `https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/<article-slug>/...`.
- A final WeChat draft or publish result when publishing is not explicitly skipped.

Non-goals:
- Do not rewrite a finished article from scratch unless the user asks for a rewrite.
- Do not use generated images as generic decoration; each inline image should explain or reinforce nearby content.
- Do not publish before the article has metadata, image URLs, and the required ending hook.

## WeChat Ending Hook Rules

- Every generated or revised WeChat article must end with a short topic-specific engagement hook after the substantive conclusion.
- The hook should invite readers to comment with their own experience, mention that the discussion may help other domestic developers/readers, and ask readers to tap `在看` or share if the article was useful.
- Adapt the first paragraph to the article topic. Do not reuse the payment/card-declined example unless the article is actually about payments.
- End with this fixed brand follow block:

```markdown
写 AI，写成长，偶尔写投资。
关注沐风，不定期更新，全是干货。
```

- Keep the hook natural and restrained: no emojis, no excessive exclamation marks, no generic sales slogans, and no long unrelated self-promotion.
- If the `mufeng-blog-writing` skill has footer rules, this hook is still mandatory. Place it after the article's normal conclusion and before any publishing-only metadata.
- When revising an existing article, add or update the hook once. Do not duplicate existing calls to action.

## SEO/GEO Frontmatter Rules

- Use `category`, not the misspelled `categery`.
- Required frontmatter fields before publishing:
  - `title`: include the core keyword or entity naturally, usually under 60 Chinese characters.
  - `slug`: SEO/GEO-friendly ASCII slug. Use the same value as `<article-slug>` for image folders and GitHub paths.
  - `author`: always `changyou`.
  - `date`: `YYYY-MM-DD`.
  - `category`: one concise human-readable category, for example `AI 编程`, `开发工具`, `iOS 开发`, `后端开发`, `前端开发`, `成长复盘`, or `投资笔记`.
  - `summary`: 150-200 Chinese characters covering the problem, solution, and outcome. Include core keywords naturally. No Markdown, links, line breaks, or promotional filler.
  - `tags`: 4-8 tags as a YAML list. Include the main entity/tool, technology stack, problem domain, and reader intent. Do not use `#` prefixes.
  - `coverImage`: add after GitHub upload using the uploaded cover raw URL.
- Frontmatter `summary` and `tags` are mandatory even if the article body also contains visible `摘要` and `标签` sections.
- Put the slug in YAML frontmatter exactly as `slug: <article-slug>`.
- Use lowercase ASCII kebab-case only: `a-z`, `0-9`, and single hyphens. Do not use Chinese characters, spaces, underscores, punctuation, emoji, or URL encoding.
- Make it semantic and search-aligned: include the main entity/tool/technology plus the concrete problem, solution, or outcome. Prefer `codex-wechat-article-image-publish` over generic values like `article`, `wechat-post`, or `notes`.
- Keep it concise: 3-8 meaningful words, usually under 70 characters.
- Translate Chinese topic words into common English search terms, but preserve established product, framework, API, and library names in normalized lowercase form, for example `swiftui`, `spring-boot`, `wechat`, `codex`.
- Avoid filler and clickbait terms such as `best`, `ultimate`, `guide`, `new`, `latest`, `awesome`, unless they are genuinely part of the user's target keyword.
- Do not include dates unless the date is essential to the topic or needed to avoid a real collision. For filename collisions, prefer the file suffix (`-v2`) without changing the frontmatter slug.
- Reuse this exact slug in local image paths (`imgs/<article-slug>/...`), GitHub remote paths (`images/<article-slug>/...`), and the completion report.
- If revising an existing article that already has a good slug, preserve it. If it is missing or poor, replace it and mention the change.

Recommended frontmatter shape:

```yaml
---
title: "Superpowers Skill - 让 Claude Code 和 Codex 按工程流程做开发"
slug: superpowers-skill-claude-codex-workflow
author: changyou
date: YYYY-MM-DD
category: AI 编程
summary: "这篇文章从 Superpowers Skill 的设计出发，拆解它如何把 Claude Code 和 Codex 从临时问答变成可验证的工程流程，包括计划、测试、实现、复盘这些关键环节，帮助开发者减少返工并提升 AI 编程交付质量，也让团队更容易明确目标、约束变更范围、补齐验证闭环。"
tags:
  - Superpowers
  - Claude Code
  - Codex
  - AI 编程
  - 工程流程
coverImage: https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/superpowers-skill-claude-codex-workflow/cover.png
---
```

## Workflow

1. Locate source materials and generate the article.
   - If the user gives a directory, use that directory. Otherwise use the current working directory.
   - Treat Markdown, text notes, transcripts, outlines, code snippets, screenshots/OCR notes, and other user-provided files in that directory as source material.
   - Ignore build/cache/vendor folders, generated image folders, previous WeChat output folders, and existing `github-image-urls.json` files.
   - Read the `mufeng-blog-writing` skill and follow its workflow, tone, structure, metadata, and footer rules.
   - Before drafting, derive one canonical `article-slug` from the source material's core topic, target query, and specific outcome.
   - Generate a professional Chinese WeChat Official Account article as Markdown. It should be publish-ready, with frontmatter `title`, `slug`, `author: changyou`, `date: YYYY-MM-DD`, `category`, `summary`, and `tags`, plus a clear `#` title and practical structure.
   - Append the required WeChat ending hook before saving the article.
   - Save the generated Markdown article in the requested directory unless the user specifies another output path. If no filename is specified, prefer `<article-slug>.md` over the Chinese title. If a target filename already exists, append `-v2`, `-v3`, etc. rather than overwriting.
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
   - Fixed image host:
     - Repository: `https://github.com/mf-blog/blogPictures`
     - Branch: `main`
     - Directory: `images`
   - Use this repository and directory for future article images. Do not read `MUFENG_GITHUB_IMAGE_REPO`, `MUFENG_GITHUB_IMAGE_BRANCH`, or `MUFENG_GITHUB_IMAGE_DIR` for this skill unless the user explicitly asks to override the fixed image host.
   - Use the bundled helper:

```bash
python3 "$HOME/.agents/skills/mufeng-materials-to-wechat-publish/scripts/upload_github_images.py" \
  --repo "mf-blog/blogPictures" \
  --branch "main" \
  --remote-dir "images/<article-slug>" \
  --json-out "imgs/<article-slug>/github-image-urls.json" \
  imgs/<article-slug>/cover.png \
  imgs/<article-slug>/fig-01.png
```

6. Insert image URLs into the generated Markdown article.
   - Add or update frontmatter with `coverImage: <cover-url>` while preserving the existing `slug`, `category`, `summary`, and `tags`.
   - If `category`, `summary`, or `tags` are missing or only present in the body, add them to YAML frontmatter before publishing.
   - Insert the cover near the top of the article only if the user asked for the cover to appear in the article body; otherwise use it as publishing metadata.
   - Insert inline illustrations as normal Markdown images:

```markdown
![短描述](https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/<article-slug>/fig-01.png)
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
- Article slug.
- Frontmatter category, summary, and tags.
- Generated article path.
- Article path changed.
- Whether the required WeChat ending hook was added or preserved.
- Cover URL and inline image URLs.
- WeChat publishing method and result, including draft `media_id` if the API returns one.
- Any skipped step or manual action still required.
