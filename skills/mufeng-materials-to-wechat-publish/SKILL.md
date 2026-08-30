---
name: mufeng-materials-to-wechat-publish
description: Use when source materials in a directory, such as notes, drafts, transcripts, screenshots, outlines, or code snippets, need to be turned into a professional evidence-rich WeChat Official Account article with mufeng-blog-writing, current WeChat search-intent research, natural keyword mapping, SEO/GEO-friendly Markdown metadata, content-quality gates, real screenshots when available, generated PNG cover and inline illustrations, GitHub-hosted raw image URLs, and WeChat publishing. Do not use for an already-finished article that only needs publishing; use mufeng-wechat-publish-full for that.
---

# Mufeng Materials To WeChat Publish

## Core Rules

- Use this skill for the materials-to-article workflow. If the user already has a finished Markdown article and only needs image upload, formatting, API publishing, or publish recovery, use `mufeng-wechat-publish-full` instead.
- Start from the materials in the requested directory, not from a blank topic. Generate the article first with the `mufeng-blog-writing` skill's article-writing conventions, with this skill's frontmatter requirements taking precedence.
- Every generated Markdown article must include SEO/GEO-friendly YAML frontmatter with `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and later `coverImage`.
- Keep `summary` and `tags` only in YAML frontmatter. Do not add visible `摘要` headings/blocks or `标签` lines/blocks to the article body. This rule overrides `mufeng-blog-writing`'s default visible `摘要` and `标签` blocks.
- Research current WeChat search intent before drafting. Choose one primary query and 3-6 supporting terms from verifiable current evidence; if live WeChat search evidence is unavailable, label the proxy source and uncertainty instead of inventing demand.
- Map keywords naturally into the title, opening, useful H2 headings, summary, and relevant body sections. Treat YAML `tags` as internal metadata, not as a WeChat ranking signal or a substitute for body relevance.
- Use the uploaded cover in both places: as `coverImage`/`--cover` publishing metadata and as the first rendered element of the WeChat article body. Put its Markdown image immediately after the H1 so the renderer can strip the H1 while leaving the cover first; place no text, visible metadata, caption, or divider before it.
- Every generated or substantially revised article must pass the evidence and authenticity gate: real screenshots when available, personal experience, at least one failure/lesson, and 2-3 authoritative sources.
- Before publishing, pass the originality, account-fit, title-integrity, and low-quality-content gates. Revise failures; stop before publishing when a material failure cannot be fixed from available evidence.
- Every generated Markdown article must be Emoji-free. Do not add any AI-assist, AI-generated, or model-use declaration to the article body or footer.
- Use Codex built-in image generation only for new cover and illustration images. Do not call OpenAI Images API, `baoyu-image-gen`, Google, DashScope, or other image CLIs unless the user explicitly asks to switch.
- Do not use generated images as replacements for real screenshots. Real screenshots are evidence assets; never fabricate Codex, Claude, revenue, analytics, or project UI screenshots.
- Default generated visuals to a restrained, article-specific technical-editorial direction. Do not default to neon gradients, glowing networks, floating interfaces, glossy 3D objects, robots, brains, circuit heads, or other recognizable generative-AI clichés.
- Save generated images as PNG. If a generated asset is not PNG, convert it to PNG before upload.
- Keep generated images free of readable UI text, Chinese text, labels, captions, watermarks, and signatures unless the user explicitly requests text in the image. Put titles/captions in Markdown instead.
- Do not add a `真实开发过程` section or any equivalent meta-production section about how materials, logs, commands, research, or screenshots were assembled into the article. Keep reader-relevant evidence inside the topical sections and keep workflow notes in the completion report.
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
- A documented WeChat search brief with the primary intent, primary query, 3-6 supporting terms, evidence source, and research date.
- A body that starts with the uploaded cover image after the Markdown H1 and contains no visible summary or tag metadata blocks.
- Article body with evidence-backed content: real screenshots when available, personal experience, failure/lesson, and authoritative sources.
- Local PNG images under `imgs/<article-slug>/`.
- Uploaded raw GitHub image URLs under `https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/<article-slug>/...`.
- A final WeChat draft or publish result when publishing is not explicitly skipped.

Non-goals:
- Do not rewrite a finished article from scratch unless the user asks for a rewrite.
- Do not use generated images as generic decoration; each inline image should explain or reinforce nearby content.
- Do not publish before the article has metadata, image URLs, and the required ending hook.
- Do not invent personal experience, screenshots, income numbers, project results, or source citations. If evidence is unavailable, record the gap in the completion report and omit the unsupported element or use a clearly labeled non-evidence illustration.

## Markdown Emoji Rules

- The final generated `.md` article must contain no Emoji symbols anywhere.
- This ban applies to YAML frontmatter, title, H1/H2/H3 headings, summary, tags, body paragraphs, lists, blockquotes, code comments, image alt text, captions, `参考资料`, the engagement hook, footer, and any copied source-material excerpts.
- Do not add `📌 声明：本文由 AI 辅助完成` or any equivalent disclosure about AI assistance, AI generation, model use, or automated writing.
- If source materials or an existing draft contain Emoji, remove or rewrite them during article generation. Do not preserve Emoji in quotes or examples unless the user explicitly overrides this rule.
- If the `mufeng-blog-writing` footer rule is used, keep only the timestamp and location. Omit all AI-assist declarations.
- Before publishing, scan the final Markdown for Emoji and AI-assist declarations. Remove every match and re-check.

## Technical Blog Image Art Direction

Apply these rules to every generated cover and inline illustration:

- Derive the visual from the article's concrete subject, system relationship, tool, or decision. Extract 2-4 topic-specific nouns before prompting; do not substitute a generic `AI + code + network` scene.
- When recent covers or illustrations are readily available locally, inspect 6-10 relevant examples before generating. Identify repeated palettes, compositions, materials, and metaphors, then choose a meaningfully different direction unless a fixed brand treatment requires continuity.
- Choose the visual form by function:
  - Use a restrained editorial schematic for architecture, data flow, state, synchronization, dependencies, or comparisons.
  - Use a quiet technical still life or product-like composition for tools, hardware, workflows, and concrete objects.
  - Use a minimal geometric or print-editorial metaphor for abstract decisions, constraints, tradeoffs, and failure modes.
  - Use a real screenshot or a deterministic locally rendered diagram when exact UI, code, labels, arrow directions, or numeric relationships matter. Do not ask ImageGen to invent precision.
- Keep the visual language simple and elegant: one focal idea, ample negative space, clear hierarchy, balanced asymmetry or a disciplined grid, consistent geometry, and only enough detail to explain the concept.
- Use a restrained palette of 2-4 colors. Prefer warm white, paper, stone, ink, graphite, or other quiet neutrals with one muted accent; use stronger colors only when the subject genuinely calls for them.
- Prefer tactile, believable materials and subtle texture such as paper grain, matte metal, glass, or soft natural shadow. Preserve small physical imperfections when they make a still life feel authored rather than synthetic.
- Avoid the common generative-AI look: blue-purple neon gradients, cyan glow, luminous network nodes, holograms, floating dashboards, glassmorphism, glossy plastic, chrome blobs, excessive 3D, isometric server stacks, robots, humanoid brains, circuit-board heads, random particles, light trails, impossible architecture, cinematic bloom, dramatic sci-fi lighting, and dense ornamental detail.
- Keep a single article visually coherent without cloning the same composition. The cover and inline illustrations may share palette or line language, but vary framing and make each image perform a distinct explanatory job.
- Do not use a centered glowing object on a dark gradient as the default cover. Favor light or neutral grounds unless the topic specifically benefits from a dark treatment.
- Keep all generated visuals text-free unless the user explicitly requests text. Put exact terminology, captions, and explanations in Markdown.

Build each ImageGen prompt from these fields:

1. **Purpose:** cover or the exact nearby concept the image must explain.
2. **Concrete subject:** the topic-specific objects, components, or relationship to depict.
3. **Visual form:** editorial schematic, technical still life, restrained geometric illustration, or another justified form.
4. **Composition:** aspect ratio, focal placement, negative space, hierarchy, and camera/viewpoint when relevant.
5. **Palette and material:** 2-4 named colors plus paper, ink, metal, glass, or another restrained material language.
6. **Rendering constraints:** text-free, no watermark, no fake UI, clean edges, technically plausible relationships.
7. **Exclusions:** list the relevant AI clichés from the prohibition above, plus any palette or composition already overused in recent local images.

## Article Evidence and Authenticity Rules

Apply these rules to every generated or substantially revised article unless the user explicitly asks to skip them. If a rule cannot be satisfied from available materials or verifiable sources, do not fake it; document the gap in the completion report and, when the gap weakens the article, stop before publishing.

### Real Screenshots

- Include at least one real screenshot when source materials, local project UIs, terminal output, Codex/Claude sessions, dashboards, or user-provided screenshots are available.
- Prefer screenshots that prove the article's claims: terminal/test/build output, project interface, product result, revenue/analytics dashboard, or configuration screen.
- For income, revenue, analytics, or account screenshots, only use user-provided or locally available screenshots. Redact private data, tokens, emails, customer names, order IDs, and unrelated balances before upload.
- Do not generate fake UI screenshots. If no real screenshot is available, use a deterministic diagram or generated illustration only as supporting visual material, and do not describe it as a screenshot.

### Personal Experience and Failure Cases

- Add a concrete first-person experience section or paragraph: what I tried, the project/context, the decision I made, and what changed after the decision.
- Include at least one failure case, wrong turn, limitation, or lesson learned. Good examples: a failed prompt, broken build, rejected publish attempt, misleading metric, unusable generated image, or implementation shortcut that later caused rework.
- Keep claims bounded. Use exact numbers only when they appear in source material or verified local artifacts; otherwise use qualitative wording.

### Authoritative Sources

- Cite at least 2 authoritative sources, target 3 when the topic supports it.
- Prefer primary or high-authority sources: official documentation, release notes, standards/specs, academic papers, vendor engineering blogs, government/regulatory pages, or original benchmark/data sources.
- For fast-moving AI/tooling topics, verify sources during the task instead of relying on memory. Keep any research or verification date in the private search brief or completion report, not in the visible reference entry.
- Do not cite unverifiable secondary summaries as authority when an official source exists. Do not invent source titles, URLs, dates, benchmark numbers, or quotes.
- Add a `## 参考资料` section near the end using concise bullets. Keep links as Markdown links if the publishing pipeline supports them; otherwise include source names and plain URLs.
- Format visible reference entries with the source title, publisher when useful, and URL. Never append access-date wording such as `访问日期`, `检索日期`, `Accessed`, or `Retrieved`. Preserve a verified publication or release date only when it is materially relevant to the citation.

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
- If the `mufeng-blog-writing` footer is used, format the timestamp as `YYYY.MM.DD HH:mm`, followed by the location on the next line. Example: `2026.08.30 18:20` and `沪 · 赵巷`. Do not use a date-only footer such as `2026.08.30`.
- When revising an existing article, add or update the hook once. Do not duplicate existing calls to action.

## WeChat Search Intent and Content Quality Rules

### Search Intent Research

- Research before drafting, not after the article structure is fixed.
- Prefer current WeChat evidence: `搜一搜` autocomplete, result pages, related searches, `微信指数`, and recent high-ranking results for the topic. Record the research date and evidence source.
- When direct WeChat access is unavailable, use current web search, official documentation, user-provided screenshots, or recent platform evidence as a labeled proxy. Do not describe proxy data as verified WeChat search volume or ranking data.
- Inspect 3-5 query variants and representative results to determine what readers want: explanation, troubleshooting, tutorial, comparison, decision support, or recent change. Use competitors only to identify intent and content gaps; do not copy their wording or structure.
- Choose one primary query, 3-6 supporting terms/entities, and one clear reader outcome. If the material cannot satisfy that intent truthfully, choose a narrower query or stop before drafting.

### Natural Keyword Mapping

- Put the primary query or its natural equivalent once in the title. Make the title accurately state the article's concrete value or outcome.
- Answer the primary intent in the opening paragraph immediately after the cover. Include the main entity and problem naturally within the first 120 Chinese characters when readable.
- Use the primary query or a close variant in at least one useful H2. Build other H2 headings around genuine reader questions, decisions, steps, or findings; do not force the keyword into every heading.
- Place supporting terms, named entities, synonyms, and related questions only in sections that actually answer them. Prefer semantic coverage over exact-match repetition.
- Include the primary entity/problem and concrete outcome once in the 90-120-character `summary` digest.
- Do not add keyword lists, hidden keyword blocks, visible tag blocks, mechanical repetitions, or keyword-density targets. Remove any term that makes the sentence less natural.

### Originality and Recommendation-Readiness Gates

- **Originality:** require at least one material contribution grounded in source evidence or actual work: a first-person decision, real screenshot, failure, measurement, comparison, implementation detail, or bounded conclusion. Synthesize sources in original wording; do not closely paraphrase or imitate another article's structure. Never claim a plagiarism check unless source comparisons were actually performed.
- **Account fit:** classify the topic as core, adjacent, or off-topic for the account promise `写 AI，写成长，偶尔写投资`. Core topics are AI, software development, and practical growth; investment is occasional. Reframe an adjacent topic around a credible connection. For an off-topic article, report the mismatch and stop before publishing unless the user explicitly approves it.
- **Title integrity:** ensure the title's entity, problem, timeframe, and promised outcome are supported by the body. Reject fake urgency, unexplained absolutes, misleading omissions, impersonation of official notices, and words such as `必看`, `震惊`, `封神`, `最强`, `100%`, or `官方推荐` unless the exact claim is necessary and verifiable.
- **Low-quality content:** remove generic scene-setting, repeated conclusions, empty transition paragraphs, fabricated quotes, unsupported rankings, keyword stuffing, and sections that add no evidence, decision, example, comparison, or actionable step. Keep limitations and counter-evidence when they materially change the conclusion.
- Pass all four gates before image upload and publishing. If a gate fails, revise and re-check; document any unresolved limitation in the completion report.

## SEO/GEO Frontmatter Rules

- Use `category`, not the misspelled `categery`.
- Required frontmatter fields before publishing:
  - `title`: include the core keyword or entity naturally, usually under 60 Chinese characters.
  - `slug`: SEO/GEO-friendly ASCII slug. Use the same value as `<article-slug>` for image folders and GitHub paths.
  - `author`: always `changyou`.
  - `date`: `YYYY-MM-DD`.
  - `category`: one concise human-readable category, for example `AI 编程`, `开发工具`, `iOS 开发`, `后端开发`, `前端开发`, `成长复盘`, or `投资笔记`.
  - `summary`: 90-120 Chinese characters covering the problem, solution, and outcome. Include the primary entity/problem naturally once. No Markdown, links, line breaks, or promotional filler. This overrides `mufeng-blog-writing`'s 150-200-character default and stays within the WeChat publishing script's digest limit.
  - `tags`: 4-8 tags as a YAML list for internal organization. Include the main entity/tool, technology stack, problem domain, and reader intent. Do not use `#` prefixes, render them in the body, or treat them as submitted WeChat ranking signals.
  - `coverImage`: add after GitHub upload using the uploaded cover raw URL.
- Frontmatter `summary` and `tags` are mandatory metadata, but must never be duplicated as visible `摘要` or `标签` sections in the article body.
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
summary: "这篇文章基于真实复盘 Superpowers Skill 如何把 Claude Code 和 Codex 的临时问答转成可验证的工程流程，拆解计划、测试、实现和复盘，并说明失败案例与适用边界，帮助开发者减少返工、提升 AI 编程交付质量。"
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

1. Locate source materials, research search intent, and make an evidence inventory.
   - If the user gives a directory, use that directory. Otherwise use the current working directory.
   - Treat Markdown, text notes, transcripts, outlines, code snippets, screenshots/OCR notes, and other user-provided files in that directory as source material.
   - Ignore build/cache/vendor folders, generated image folders, previous WeChat output folders, and existing `github-image-urls.json` files.
   - Identify available real screenshots and evidence assets before drafting: project UI, terminal/test output, analytics/revenue screenshots, code diffs, diagrams, and existing article screenshots.
   - Identify personal-experience material: project context, decisions, mistakes, failed attempts, tradeoffs, and results.
   - Identify source needs: list the claims that require 2-3 authoritative references, then verify those references before finalizing the article.
   - Research current WeChat search intent using the rules above. Record the research date, evidence source, 3-5 query variants, representative result patterns, and any access limitation.
   - Select one primary intent, one primary query, 3-6 supporting terms/entities, and one concrete reader outcome. Keep this search brief outside the visible article body.
   - Read the `mufeng-blog-writing` skill and follow its workflow, tone, structure, metadata, and footer rules.
   - Before drafting, derive one canonical `article-slug` from the source material's core topic, target query, and specific outcome.

2. Generate the article.
   - Generate a professional Chinese WeChat Official Account article as Markdown. It should be publish-ready, with frontmatter `title`, `slug`, `author: changyou`, `date: YYYY-MM-DD`, `category`, `summary`, and `tags`, plus a clear `#` title and practical structure.
   - Do not generate visible `摘要` or `标签` blocks before the main body. Store both values only in YAML frontmatter, overriding the `mufeng-blog-writing` output-format default.
   - Apply the keyword map while drafting: primary query in the title, direct intent answer in the opening, a natural H2 variant, and supporting terms only in relevant sections. Do not retrofit repeated keywords after drafting.
   - Include the evidence and authenticity requirements: real screenshot placements when available, personal experience, at least one failure/lesson, and `参考资料`.
   - Do not add a standalone or disguised `真实开发过程`/`材料整理过程`/`证据链合成过程` section. Do not narrate files inspected, commands run, source-count inventory, research steps, or missing screenshots as article content.
   - In `参考资料`, omit access dates and access-date phrases. Keep verification dates only in the non-visible search brief or completion report.
   - Remove all Emoji from the generated article. Do not append `📌 声明：本文由 AI 辅助完成` or any equivalent AI-assist declaration.
   - Put `参考资料` after the substantive conclusion and before the required WeChat ending hook.
   - Append the required WeChat ending hook before saving the article.
   - Save the generated Markdown article in the requested directory unless the user specifies another output path. If no filename is specified, prefer `<article-slug>.md` over the Chinese title. If a target filename already exists, append `-v2`, `-v3`, etc. rather than overwriting.
   - The generated article becomes the target article for all later steps.

3. Read the generated article and make an image plan.
   - Use one cover image.
   - Prioritize real screenshots for evidence-heavy sections. Use generated illustrations only for the cover or for ideas that cannot be shown with real artifacts.
   - For every generated visual, record its purpose, concrete topic-specific subject, chosen visual form, composition, restrained palette/material language, and exclusions.
   - Inspect 6-10 recent relevant local covers or illustrations when available, and avoid repeating their dominant palette, centered-object layout, or metaphor.
   - Add inline screenshots or illustrations at natural breakpoints: after the opening setup, before dense technical sections, after major H2 sections, or near claims that need visual proof.
   - Avoid inserting images inside code blocks, tables, lists, blockquotes, or YAML frontmatter.
   - For short articles, use 1-2 inline visuals. For long articles, use roughly one visual per 600-900 Chinese characters or per major section, capped unless the user asks for many.

4. Prepare PNG image assets.
   - Recommended local layout: `imgs/<article-slug>/cover.png`, `imgs/<article-slug>/shot-01.png`, `imgs/<article-slug>/fig-01.png`.
   - Copy, redact, crop, or convert real screenshots into this folder as PNGs. Keep screenshot filenames distinct from generated figure filenames.
   - Generate cover and optional illustration PNGs with Codex image generation.
   - Build each prompt with the seven fields in `Technical Blog Image Art Direction`; include the specific article concept and explicit exclusions instead of asking only for an `editorial/tech` image.
   - For the cover, use a wide 2.35:1 or 16:9 composition with a clear focal idea, generous negative space, a restrained 2-4-color palette, and no text.
   - For inline illustrations, explain exactly one nearby idea. Prefer a precise schematic, quiet still life, or minimal print-editorial metaphor over generic abstract system visuals.
   - If exact labels, arrows, UI states, code, or numeric relationships are essential, use a verified screenshot or render a deterministic diagram locally and save it as PNG; do not rely on ImageGen for exact technical notation.

5. Validate image files, article evidence, search alignment, and content quality.
   - Confirm each image asset exists, is non-empty, and is PNG.
   - Prefer keeping each PNG under 5 MB. Compress or resize only if upload/publish tools reject the file.
   - Confirm generated visuals are article-specific, restrained, legible at article width, and free of the prohibited AI clichés. Reject and regenerate generic neon/glowing-network/floating-UI/glossy-3D results.
   - Compare generated visuals with the recent local examples inspected in the image plan. Regenerate when the dominant palette, central composition, or metaphor is substantially the same without a topic-driven reason.
   - Confirm the article includes: real screenshots when available, personal experience, failure/lesson, and 2-3 authoritative sources.
   - Confirm no `真实开发过程` or equivalent meta-production section remains in the article.
   - Confirm visible `参考资料` entries contain no access-date wording or appended access dates.
   - Confirm `summary` is 90-120 Chinese characters and accurately describes the published body without promotional filler.
   - Confirm the title, opening, at least one useful H2, and relevant body sections implement the keyword map naturally. Remove repetitions added only for ranking.
   - Run the originality, account-fit, title-integrity, and low-quality-content gates. Revise every failure before continuing.
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
   - Remove any visible metadata-only `摘要` heading/block and `标签` line/block from the body after their values are safely present in frontmatter. Do not remove a substantive section merely because it discusses summaries or tags as the article topic.
   - Always insert the uploaded cover as the first body image, immediately after the H1 and before the opening paragraph. Do not add a visible caption, divider, summary, tags, author, or date before it. Use this order:

```markdown
# <article-title>

![<concise-cover-alt-text>](<cover-url>)

<opening-paragraph>
```

   - Keep the same uploaded URL in frontmatter `coverImage`, the first body image, and the publishing command's `--cover` argument. Do not upload or generate a second copy solely for the body.
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
- [ ] A dated search brief records the primary intent, primary query, 3-6 supporting terms, evidence source, and any proxy-data limitation.
- [ ] The title, opening, at least one useful H2, and relevant body sections map keywords naturally; no keyword list, stuffing, or mechanical repetition remains.
- [ ] Frontmatter `summary` is 90-120 Chinese characters, matches the body, and contains the primary entity/problem and outcome naturally.
- [ ] Originality gate passed with at least one material first-hand or evidence-backed contribution; no copied wording, imitated structure, or unperformed plagiarism claim remains.
- [ ] Account-fit gate passed for `写 AI，写成长，偶尔写投资`, or explicit user approval for an off-topic article is documented.
- [ ] Title-integrity gate passed: every promise is supported and no fake urgency, unsupported absolute, misleading omission, or official impersonation remains.
- [ ] Low-quality-content gate passed: every section adds evidence, a decision, example, comparison, finding, or actionable step.
- [ ] The body contains no visible metadata-only `摘要` or `标签` blocks; `summary` and `tags` exist only in frontmatter.
- [ ] The first rendered body element is the uploaded cover image: in Markdown it appears immediately after the H1, with no text, caption, or divider before it.
- [ ] At least one real screenshot is included when available, and every screenshot is redacted as needed.
- [ ] Generated images are used only as cover/illustrations, not as fake product, revenue, Codex, or Claude screenshots.
- [ ] Each generated visual is tied to a concrete article concept, uses a restrained 2-4-color palette and clear hierarchy, and avoids the prohibited AI clichés.
- [ ] Recent relevant local images were compared when available; the new cover does not repeat their dominant palette, centered-object composition, or metaphor without a topic-driven reason.
- [ ] The article contains concrete personal experience grounded in the source material or actual development session.
- [ ] The article includes at least one failure case, limitation, wrong turn, or lesson learned.
- [ ] The article contains no `真实开发过程`, `材料整理过程`, `证据链合成过程`, or equivalent meta-production section.
- [ ] The article cites 2-3 authoritative sources in `参考资料`; fast-moving facts have been verified during the task.
- [ ] Visible `参考资料` entries do not contain `访问日期`, `检索日期`, `Accessed`, `Retrieved`, or appended access dates.
- [ ] No Emoji appears anywhere in the final Markdown.
- [ ] No AI-assist, AI-generated, or model-use declaration appears in the article body or footer.
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
- Search brief: research date, evidence source, primary intent, primary query, supporting terms, reader outcome, and any proxy-data limitation.
- Keyword mapping result: title, opening, H2, and body placements; confirm no stuffing or visible keyword/tag block.
- Digest check: report the `summary` character count and confirm it is within 90-120 characters.
- Quality-gate results: originality evidence, account-fit classification, title-integrity result, and low-quality-content result.
- Body-opening check: confirm visible summary/tag blocks were removed and the cover is the first rendered body element.
- Generated article path.
- Article path changed.
- Evidence inventory: real screenshots used, personal experience added, and failure/lesson added.
- Article-structure check: confirm no real-development-process or other meta-production section was added.
- Authoritative sources cited, including count and whether they were verified during the task.
- Reference-format check: confirm visible references omit access dates and access-date wording.
- Emoji and disclosure check result: confirm no Emoji or AI-assist declaration remains.
- Whether the required WeChat ending hook was added or preserved.
- Image direction used: subject, visual form, palette/material language, comparison against recent local images when available, and AI-cliché check result.
- Cover URL and inline image URLs.
- WeChat publishing method and result, including draft `media_id` if the API returns one.
- Any skipped step or manual action still required.
