---
name: mufeng-materials-to-wechat-publish
description: Use when source materials in a directory, such as notes, drafts, transcripts, screenshots, outlines, or code snippets, need to be turned into a professional evidence-rich WeChat Official Account article with mufeng-blog-writing, SEO/GEO-friendly Markdown metadata, real screenshots when available, generated PNG cover and inline illustrations, GitHub-hosted raw image URLs, and WeChat publishing. Do not use for an already-finished article that only needs publishing; use mufeng-wechat-publish-full for that.
---

# Mufeng Materials To WeChat Publish

## Core Rules

- Use this skill for the materials-to-article workflow. If the user already has a finished Markdown article and only needs image upload, formatting, API publishing, or publish recovery, use `mufeng-wechat-publish-full` instead.
- Start from the materials in the requested directory, not from a blank topic. Generate the article first with the `mufeng-blog-writing` skill's article-writing conventions, with this skill's frontmatter requirements taking precedence.
- Every generated Markdown article must include SEO/GEO-friendly YAML frontmatter with `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and later `coverImage`.
- Every generated or substantially revised article must pass the evidence and authenticity gate: real screenshots when available, personal experience, at least one failure/lesson, related article recommendations, 2-3 authoritative sources, and a concise real development-process section.
- Every generated Markdown article must be Emoji-free except for the exact footer declaration line `📌 声明：本文由 AI 辅助完成`.
- Use Codex built-in image generation only for new cover and illustration images. Do not call OpenAI Images API, `baoyu-image-gen`, Google, DashScope, or other image CLIs unless the user explicitly asks to switch.
- Do not use generated images as replacements for real screenshots. Real screenshots are evidence assets; never fabricate Codex, Claude, revenue, analytics, or project UI screenshots.
- Save generated images as PNG. If a generated asset is not PNG, convert it to PNG before upload.
- Keep generated images free of readable UI text, Chinese text, labels, captions, watermarks, and signatures unless the user explicitly requests text in the image. Put titles/captions in Markdown instead.
- Upload the cover and all inline visual assets to GitHub image hosting, then insert `https://raw.githubusercontent.com/...` URLs into the Markdown article.
- Publish from the final Markdown file. Do not pre-convert Markdown to HTML before calling the WeChat publishing script.

## Execution Contract

Inputs:
- A source-material directory, or the current working directory if no directory is given.
- Source files may include Markdown, text notes, transcripts, outlines, screenshots/OCR notes, code snippets, and drafts.
- Optional user constraints such as target angle, title preference, image count, output filename, or whether to stop before publishing.

Outputs:
- A publish-ready Markdown article saved in the source directory, usually as `<article-slug>.md`.
- SEO/GEO-friendly frontmatter with `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and uploaded `coverImage`.
- Article body with evidence-backed sections: real screenshots or a documented reason for absence, personal experience, failure/lesson, real development process, authoritative sources, and related article recommendations.
- Local PNG images under `imgs/<article-slug>/`.
- Uploaded raw GitHub image URLs under `https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/<article-slug>/...`.
- A final WeChat draft or publish result when publishing is not explicitly skipped.

Non-goals:
- Do not rewrite a finished article from scratch unless the user asks for a rewrite.
- Do not use generated images as generic decoration; each inline image should explain or reinforce nearby content.
- Do not publish before the article has metadata, image URLs, and the required ending hook.
- Do not invent personal experience, screenshots, income numbers, project results, source citations, or related-article URLs. If evidence is unavailable, say so and either omit that element with a reason or use a clearly labeled non-evidence illustration.

## Markdown Emoji Rules

- The final generated `.md` article must contain no Emoji symbols anywhere except this exact line:

```markdown
📌 声明：本文由 AI 辅助完成
```

- This ban applies to YAML frontmatter, title, H1/H2/H3 headings, summary, tags, body paragraphs, lists, blockquotes, code comments, image alt text, captions, `参考资料`, `相关阅读`, the engagement hook, and any copied source-material excerpts.
- If source materials or an existing draft contain Emoji, remove or rewrite them during article generation. Do not preserve Emoji in quotes or examples unless the user explicitly overrides this rule.
- If the `mufeng-blog-writing` footer rule is used, keep only the exact allowed declaration line above. Do not add other Emoji to timestamp, location, call-to-action, headings, or section separators.
- Before publishing, scan the final Markdown for Emoji. If any Emoji exists outside the exact allowed declaration line, remove it and re-check.

## Article Evidence and Authenticity Rules

Apply these rules to every generated or substantially revised article unless the user explicitly asks to skip them. If a rule cannot be satisfied from available materials or verifiable sources, do not fake it; document the gap in the completion report and, when the gap weakens the article, stop before publishing.

### Real Screenshots

- Include at least one real screenshot when source materials, local project UIs, terminal output, Codex/Claude sessions, dashboards, or user-provided screenshots are available.
- Prefer screenshots that prove the article's claims: Codex or Claude development process, terminal/test/build output, project interface, product result, revenue/analytics dashboard, or configuration screen.
- For income, revenue, analytics, or account screenshots, only use user-provided or locally available screenshots. Redact private data, tokens, emails, customer names, order IDs, and unrelated balances before upload.
- Do not generate fake UI screenshots. If no real screenshot is available, use a deterministic diagram or generated illustration only as supporting visual material, and do not describe it as a screenshot.

### Personal Experience and Failure Cases

- Add a concrete first-person experience section or paragraph: what I tried, the project/context, the decision I made, and what changed after the decision.
- Include at least one failure case, wrong turn, limitation, or lesson learned. Good examples: a failed prompt, broken build, rejected publish attempt, misleading metric, unusable generated image, or implementation shortcut that later caused rework.
- Keep claims bounded. Use exact numbers only when they appear in source material or verified local artifacts; otherwise use qualitative wording.

### Real Development Process

- Add a concise section such as `## 真实开发过程` or weave the process into the body when a separate section would feel forced.
- Base it on actual work performed in this session or source materials: files inspected, commands run, prompts used, code/design decisions, errors encountered, tests/checks run, and final verification.
- Mention sensitive details only after redaction. Do not include secrets, private tokens, unpublished customer data, or irrelevant local paths.

### Authoritative Sources

- Cite at least 2 authoritative sources, target 3 when the topic supports it.
- Prefer primary or high-authority sources: official documentation, release notes, standards/specs, academic papers, vendor engineering blogs, government/regulatory pages, or original benchmark/data sources.
- For fast-moving AI/tooling topics, verify sources during the task instead of relying on memory. Record source title, publisher, URL, and access date when practical.
- Do not cite unverifiable secondary summaries as authority when an official source exists. Do not invent source titles, URLs, dates, benchmark numbers, or quotes.
- Add a `## 参考资料` section near the end using concise bullets. Keep links as Markdown links if the publishing pipeline supports them; otherwise include source names and plain URLs.

### Related Articles

- Add `## 相关阅读` before the final engagement hook.
- Recommend 2-4 related articles from the author's existing published/local writing when available. Use verified titles and URLs or local filenames; do not make up links.
- If no related articles can be verified quickly, recommend topic titles without links and mark them as `可延伸阅读方向`, or omit the section and report why.

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

1. Locate source materials and make an evidence inventory.
   - If the user gives a directory, use that directory. Otherwise use the current working directory.
   - Treat Markdown, text notes, transcripts, outlines, code snippets, screenshots/OCR notes, and other user-provided files in that directory as source material.
   - Ignore build/cache/vendor folders, generated image folders, previous WeChat output folders, and existing `github-image-urls.json` files.
   - Identify available real screenshots and evidence assets before drafting: Codex/Claude process, project UI, terminal/test output, analytics/revenue screenshots, code diffs, diagrams, and existing article screenshots.
   - Identify personal-experience material: project context, decisions, mistakes, failed attempts, tradeoffs, and results.
   - Identify source needs: list the claims that require 2-3 authoritative references, then verify those references before finalizing the article.
   - Identify related-article candidates from the user's local/published writing when possible. Verify titles and URLs/paths before recommending them.
   - Read the `mufeng-blog-writing` skill and follow its workflow, tone, structure, metadata, and footer rules.
   - Before drafting, derive one canonical `article-slug` from the source material's core topic, target query, and specific outcome.

2. Generate the article.
   - Generate a professional Chinese WeChat Official Account article as Markdown. It should be publish-ready, with frontmatter `title`, `slug`, `author: changyou`, `date: YYYY-MM-DD`, `category`, `summary`, and `tags`, plus a clear `#` title and practical structure.
   - Include the evidence and authenticity requirements: real screenshot placements or documented absence, personal experience, at least one failure/lesson, real development process, `参考资料`, and `相关阅读`.
   - Remove all Emoji from the generated article except the exact `📌 声明：本文由 AI 辅助完成` footer declaration line.
   - Put `参考资料` and `相关阅读` after the substantive conclusion and before the required WeChat ending hook.
   - Append the required WeChat ending hook before saving the article.
   - Save the generated Markdown article in the requested directory unless the user specifies another output path. If no filename is specified, prefer `<article-slug>.md` over the Chinese title. If a target filename already exists, append `-v2`, `-v3`, etc. rather than overwriting.
   - The generated article becomes the target article for all later steps.

3. Read the generated article and make an image plan.
   - Use one cover image.
   - Prioritize real screenshots for evidence-heavy sections. Use generated illustrations only for the cover or for ideas that cannot be shown with real artifacts.
   - Add inline screenshots or illustrations at natural breakpoints: after the opening setup, before dense technical sections, after major H2 sections, or near claims that need visual proof.
   - Avoid inserting images inside code blocks, tables, lists, blockquotes, or YAML frontmatter.
   - For short articles, use 1-2 inline visuals. For long articles, use roughly one visual per 600-900 Chinese characters or per major section, capped unless the user asks for many.

4. Prepare PNG image assets.
   - Recommended local layout: `imgs/<article-slug>/cover.png`, `imgs/<article-slug>/shot-01.png`, `imgs/<article-slug>/fig-01.png`.
   - Copy, redact, crop, or convert real screenshots into this folder as PNGs. Keep screenshot filenames distinct from generated figure filenames.
   - Generate cover and optional illustration PNGs with Codex image generation.
   - Cover prompt: ask for a wide 2.35:1 or 16:9 editorial/tech composition with clear focal area and no text.
   - Illustration prompts: make each image explain the nearby idea visually, not generic decoration.
   - If the article is technical, prefer diagrams, metaphors, product/workflow scenes, or abstract system visuals that match the surrounding section.

5. Validate image files and article evidence.
   - Confirm each image asset exists, is non-empty, and is PNG.
   - Prefer keeping each PNG under 5 MB. Compress or resize only if upload/publish tools reject the file.
   - Confirm the article includes or intentionally documents the absence of: real screenshots, personal experience, failure/lesson, real development process, 2-3 authoritative sources, and related recommendations.
   - If authoritative sources or real screenshots are missing for claims that depend on them, fix the article before publishing.

6. Upload images to GitHub.
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
  imgs/<article-slug>/shot-01.png \
  imgs/<article-slug>/fig-01.png
```

7. Insert image URLs into the generated Markdown article.
   - Add or update frontmatter with `coverImage: <cover-url>` while preserving the existing `slug`, `category`, `summary`, and `tags`.
   - If `category`, `summary`, or `tags` are missing or only present in the body, add them to YAML frontmatter before publishing.
   - Insert the cover near the top of the article only if the user asked for the cover to appear in the article body; otherwise use it as publishing metadata.
   - Insert real screenshots and inline illustrations as normal Markdown images:

```markdown
![Codex 实际修改过程截图](https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/<article-slug>/shot-01.png)
```

   - Use concise alt text that describes the real artifact or idea, not `image1`.
   - Preserve existing user content and formatting.

8. Publish to WeChat Official Account.
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

## Pre-Publish Evidence Checklist

Do not publish until this checklist has been checked against the final Markdown:

- [ ] SEO/GEO frontmatter includes `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and uploaded `coverImage`.
- [ ] At least one real screenshot is included when available, and every screenshot is redacted as needed.
- [ ] Generated images are used only as cover/illustrations, not as fake product, revenue, Codex, or Claude screenshots.
- [ ] The article contains concrete personal experience grounded in the source material or actual development session.
- [ ] The article includes at least one failure case, limitation, wrong turn, or lesson learned.
- [ ] The article describes the real development process: inspected materials, implementation choices, commands/checks, errors, and verification.
- [ ] The article cites 2-3 authoritative sources in `参考资料`; fast-moving facts have been verified during the task.
- [ ] The article includes `相关阅读` with verified titles/links/paths, or the absence is documented.
- [ ] No Emoji appears anywhere in the final Markdown except the exact line `📌 声明：本文由 AI 辅助完成`.
- [ ] The final engagement hook and fixed brand follow block are present exactly once.

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
- Evidence inventory: real screenshots used, personal experience added, failure/lesson added, and real development-process section added.
- Authoritative sources cited, including count and whether they were verified during the task.
- Related articles recommended, including titles and URLs/paths when available.
- Emoji check result: confirm no Emoji remains outside `📌 声明：本文由 AI 辅助完成`.
- Whether the required WeChat ending hook was added or preserved.
- Cover URL and inline image URLs.
- WeChat publishing method and result, including draft `media_id` if the API returns one.
- Any skipped step or manual action still required.
