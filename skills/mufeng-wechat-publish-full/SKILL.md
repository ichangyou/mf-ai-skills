---
name: mufeng-wechat-publish-full
description: Use when publishing articles to WeChat Official Account (微信公众号), including tasks that involve SEO/GEO-friendly Markdown metadata, professional article visuals, background-only cover generation, deterministic screenshots or diagrams before imagegen, uploading assets to the fixed GitHub image host, direct Markdown publishing, HTML fallback publishing, or calling the WeChat API. Also use when any step of a previous WeChat publish attempt failed. Includes AI tech blog content strategy for maximizing WeChat platform recommendation (推荐曝光).
compatibility: "Codex and Claude Code. An image tool when generating covers, gh authentication and a configured WeChat publisher."
---

# Mufeng WeChat Full Publishing Workflow

## Resource Paths

Set the shell variable `SKILL_DIR` to the directory containing the **loaded** `SKILL.md` before running the commands below. Resolve supporting paths from that directory, not the working directory or a fixed user/platform installation path. `$SKILL_DIR` is a shell variable you set, not a host-provided macro.


## Platform Dependencies

Read [references/platforms.md](references/platforms.md) before generating images or publishing. Set `MUFENG_WECHAT_SCRIPT` to the actual `wechat-api.ts` path from an installed `baoyu-post-to-wechat` skill, or use a documented publisher already configured in the host. The variable does not install the publisher. If the dependency or credentials are missing, finish the local article and report that publishing was not executed.

## Overview

End-to-end skill for publishing AI tech blog articles to a WeChat Official Account. Covers every stage: content strategy for platform recommendations, SEO/GEO-friendly Markdown metadata, IP verification, professional visuals, fixed GitHub image hosting, direct Markdown publishing, HTML fallback sanitization, and API draft upload. The default outcome is a verified draft, not public publication. Follow the stages relevant to that outcome; optional backend settings must not block draft upload.

## Core Publishing Rules

- “发布到公众号” defaults to uploading to the selected account's draft box through API. Public publication or mass sending requires an explicit request such as “正式发布” or “群发”; do not infer it from draft upload.
- For article workflows, use API for upload and verification. Do not open the backend, invoke Computer Use, or switch to browser automation unless the user explicitly requests browser operation. An API error is not authorization to switch methods.
- Resolve the account from the user's destination and local EXTEND.md; always pass `--account <alias>` in multi-account setups. For 沐风iOS, use `--account mufeng-ios`. Missing credentials for that account must not silently fall back to another account.
- `wechat-api.ts` calls `draft/add`; it does not submit public publication. Verify the returned `media_id` through `draft/get` on the same account before reporting a verified draft.
- Report local article completion, draft upload, draft read-back verification, and public publication separately. Never claim an unexecuted step succeeded.

- Prefer publishing from the final Markdown file. Do not pre-convert Markdown to HTML unless the user explicitly asks for HTML publishing or the API path is unavailable.
- Every generated or revised Markdown article should have SEO/GEO-friendly YAML frontmatter before publishing.
- Use the fixed image host for article assets:
  - Repository: `mf-blog/blogPictures`
  - Branch: `main`
  - Directory: `images/<article-slug>`
  - Raw URL shape: `https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/<article-slug>/<filename>.png`
- Reuse one canonical `article-slug` across frontmatter, local image folders, GitHub remote paths, and completion reports.
- Use `category`, not the misspelled `categery`.
- Preserve user-authored content. When adding metadata, images, or ending hooks, do not rewrite unrelated article sections.

---

## Stage 0: Content Strategy — AI Tech Blog for Maximum Recommendation (推荐曝光)

The following are editorial suggestions, not verified descriptions of WeChat recommendation algorithms. Do not assert signal weights, guaranteed exposure, or timing benefits without a current, verifiable source. Use account analytics to evaluate reading and engagement.

### Title Formula (标题)

Use a clear title that communicates the article topic and value. For AI tech:

**四种有效结构（四选一）：**
- `[具体工具/场景] + 实测/亲测 + 结论` — e.g., "我用 Claude 做了三个月 AI 助手，说几句真实感受"
- `[反常识结论] + 原因` — e.g., "别急着学提示词，先搞清楚这件事"
- `[数字/量化] + 行动 + 收益` — e.g., "10 个让 Claude Code 效率翻倍的使用习惯"
- `[读者痛点] + 解法` — e.g., "AI 工具用了一年，我踩过的最贵的坑"

数字适合表达真实步骤或清单；是否提升阅读表现，需要用账号数据验证。

**Title rules:**
- 长度：18-26 个汉字（含标点），不超过 30 字
- 避免标题党措辞：不用"震惊""万万没想到""99% 的人不知道""赶紧转"
- AI 技术类关键词前置：Claude、MCP、Agent、Cursor、提示词、大模型等核心词放标题前半段，利于搜索收录
- 优先使用直接表达结论的标题；不声称疑问句会受到算法限制
- 每次输出 3 个标题备选（利益驱动型 / 反常识型 / 代入感型），让作者选择

**Bad → Good examples:**
- ❌ "分享一些 AI 工具使用心得" → ✓ "用了 3 个月 Cursor，整理出这 8 个真正提效的用法"
- ❌ "关于大模型 Prompt 的思考" → ✓ "我的 Prompt 从 3 句话精简到 1 句，效果反而更好——原因在这里"

### Content Structure for High Completion Rate (完读率)

目标：让读者理解内容并愿意读完。完读率可以用于评估文章表现，不声称它具有已知的算法权重。

**Opening (前 150 字，最关键):**
- 第一段必须直接给出"为什么值得读"——一句话说清本文价值
- 不要用背景铺垫开头；不要从历史讲起
- 直接给结论或最有冲击力的发现，再往回解释

**Body structure:**
- 约每 400-600 字考虑一张有信息价值的图；按内容需要调整，不保证降低跳出率
- 段落不超过 4 行（移动端阅读节奏）
- 每个 H2/H3 小标题要能独立成句，让快速浏览者也能获得价值
- 代码块要有上下文说明——纯代码块会造成完读率骤降
- 实测数据 > 理论描述（截图、benchmark、具体数字）

**Ending (结尾 驱动分享/在看):**
- 最后一段给出"行动号召"或总结句，引导点击"在看"
- 不要用"感谢阅读"结尾——用有信息量的总结句
- 可加："如果你也在用 [工具]，欢迎留言你的用法"——激活评论信号

### WeChat Ending Hook

Every generated or revised WeChat article must end with one short topic-specific engagement hook after the substantive conclusion.

- Invite readers to comment with their own experience or use case.
- Mention that the discussion may help other domestic developers/readers when relevant.
- Ask readers to tap `在看` or share if the article was useful.
- Adapt the hook to the article topic. Do not reuse payment/card-declined examples unless the article is actually about payments.
- Do not duplicate an existing hook. Update the existing one if it is weak or off-topic.
- End with this fixed brand follow block:

```markdown
写 AI，写成长，偶尔写投资。
关注沐风，不定期更新，全是干货。
```

### Timing (发布时间)

可把工作日 12:00-13:00 或 20:00-22:00 作为测试时段，并根据账号历史数据调整。这些是经验建议，不是已验证的平台推荐窗口或保证收益。

默认上传草稿不受时段限制。用户要求立即处理时，继续上传；只有用户明确要求定时正式发布时才处理发布时间。

### Cover Image and Shared Layout (封面与统一排版)

Before planning visuals or formatting, read [沐风统一视觉规范](../mufeng-blog-writing/references/visual-style.md). Use the same modern humanistic editorial direction and topic variants as `mufeng-materials-to-wechat-publish`.

- Default to a complete text-free cover, one main relationship and purposeful whitespace. Do not default to a desk/laptop still life or a nearly empty background waiting for a title.
- A separately typeset title is optional. If requested, plan its area before generation; never ask the model to render readable text and then repair it by overpainting.
- Apply the shared layout starting values, prompt records, project-local image storage and thumbnail/crop/mobile checks. Preserve explicit user preferences and report unsupported layout differences.

### Tags & Category (话题标签)

话题标签应贴合内容；不要保证它们会提升搜索权重：
- AI 相关优先选：`#人工智能` `#大模型` `#AI工具` `#程序员` `#Claude` `#ChatGPT` `#Cursor`
- 建议选择 2-3 个相关话题标签，避免无关标签
- YAML `tags` 不等于公众号平台话题标签；当前脚本不支持设置的平台标签，记录为待手动设置，不阻塞草稿上传

### SEO/GEO Markdown Frontmatter

Before publishing Markdown, ensure the YAML frontmatter includes:

```yaml
---
title: "文章标题"
slug: article-topic-keyword
author: changyou
date: YYYY-MM-DD
category: AI 编程
summary: "150-200 字中文摘要，覆盖问题、方案和结果，自然包含核心关键词。"
tags:
  - Claude Code
  - Codex
  - AI 编程
coverImage: https://raw.githubusercontent.com/mf-blog/blogPictures/main/images/article-topic-keyword/cover.png
---
```

Rules:
- `title`: include the core keyword or entity naturally, usually under 60 Chinese characters.
- `slug`: lowercase ASCII kebab-case only, using `a-z`, `0-9`, and single hyphens.
- `author`: always `changyou`.
- `date`: `YYYY-MM-DD`.
- `category`: one concise human-readable category, such as `AI 编程`, `开发工具`, `iOS 开发`, `后端开发`, `前端开发`, `成长复盘`, or `投资笔记`.
- `summary`: 150-200 Chinese characters, no Markdown, links, line breaks, or promotional filler.
- `tags`: 4-8 YAML list items covering the main entity/tool, stack, problem domain, and reader intent. Do not use `#` prefixes here.
- `coverImage`: add or update after the cover is uploaded to GitHub.
- If an article already has a good slug, preserve it. If it is missing or poor, replace it and mention the change.

### Original Mark (原创标识)

- 主要内容来自作者的原创经验时，可准备原创声明；转载他人内容不得声明原创。
- 当前 `wechat-api.ts` 未提供原创声明参数。将原创标识记录为待手动设置，不为此打开后台，不阻塞草稿上传，也不声称已经开启。
- 如后续使用其他接口设置，先核对接口支持范围，并验证实际结果。

### Evaluate Content Performance (内容表现)

用阅读完成情况、分享、在看、评论、收藏和打开情况评估文章；不预设这些指标的算法权重。实际代码、截图、对比和清单应服务主题，不为追求未经证实的推荐收益添加无关内容。

## Stage 1: Pre-flight — Account, Credentials and Egress IP

1. Read local EXTEND.md and resolve the requested account and credentials without printing AppSecret or access tokens.
2. Record the current outbound IP before WeChat API calls:

```bash
curl -fsS --max-time 15 https://api.ipify.org
```

3. Do not require opening the backend to confirm the whitelist in advance. Use the configured API path; a successful authenticated API response shows that request was accepted from its actual egress route. A failed IP lookup alone does not establish a whitelist failure.
4. On an explicit invalid-IP error (for example `errcode 40164`), stop dependent calls and report the account, observed IP, and redacted error. Do not blindly retry. Use an already configured, authorized `remote-api` route if available; otherwise ask the user to correct the whitelist. Retry only after that condition changes.
5. HTTP 401/403 alone does not prove an IP issue. Inspect the returned error; distinguish credentials, access-token expiry, permissions, network failures and invalid IP. Do not expose credential-bearing URLs in logs.
6. Do not invoke Computer Use for diagnosis unless the user explicitly requests it.

## Stage 2: Image Generation

Resolve providers from the current user instruction and applicable AGENTS.md first. Otherwise use the host tools described in `references/platforms.md`: prefer Codex built-in generation when available; on Claude Code use an explicitly configured image tool. If no tool is available, preserve the local article and prompts and report the missing dependency. Do not silently switch services or impose a Google-first fallback; report an unavailable provider before any unapproved switch.

Read the shared visual reference linked above before preparing assets:

1. Inventory authentic screenshots and source documents. Keep them as evidence; crop or redact only with necessary context retained.
2. Choose each image by its job: cover, explanation or evidence. Use deterministic diagrams for precise labels, arrows, UI, code and numeric relationships. Do not require a fixed image count or code screenshots merely to decorate an article.
3. Select the topic variant, one main visual relationship, palette and composition. Default generated artwork to flat editorial or light print texture; use photography or still life only when the subject benefits.
4. Save each complete prompt and adopted references in the current project before generation. Generate a complete text-free cover; add a separate title layout only when requested.
5. Verify project-local PNGs before referencing them. For built-in ImageGen, recursively verify the generated source, immediately copy to the project and verify the non-empty copy before proceeding to another image.
6. Check actual 320px thumbnails, banner and central square crops. Inspect readability and palette coherence; revise cluttered, gray/muddy or meaningless compositions as well as prohibited neon/fake-UI/glossy-3D imagery. Record what was checked and what remains unverified.

A generation error does not authorize changing providers. Diagnose the actual response and report the failed item; do not regenerate successful assets or upload a draft merely to test an image.

---

## Stage 3: GitHub Image Upload

Upload images to a GitHub repo so WeChat can reference stable CDN URLs. WeChat rejects direct local paths and many third-party CDNs.

```bash
# Preferred fixed image host:
python3 "$SKILL_DIR/scripts/upload_github_images.py" \
  --repo "mf-blog/blogPictures" \
  --branch "main" \
  --remote-dir "images/<article-slug>" \
  --json-out "imgs/<article-slug>/github-image-urls.json" \
  imgs/<article-slug>/cover.png \
  imgs/<article-slug>/fig-01.png
```

The helper validates PNG files, appends a timestamp suffix when a remote path already exists, prints raw GitHub URLs, and optionally writes them to JSON for precise Markdown insertion.

```bash
# Manual fallback via GitHub API:
gh api repos/OWNER/REPO/contents/images/FILENAME \
  --method PUT \
  --field message="add image" \
  --field content="$(base64 < image.png)"

# Retrieve raw URL:
# https://raw.githubusercontent.com/OWNER/REPO/main/images/FILENAME
```

Failure modes:
- [ ] 422 Unprocessable Entity → file already exists at that path; use a unique filename (timestamp suffix)
- [ ] Image loads in browser but broken in WeChat → WeChat blocks non-HTTPS or certain CDN domains; always use `raw.githubusercontent.com` HTTPS URL
- [ ] Large image (>5 MB) rejected → compress first; WebP preferred
- [ ] Rate limit from GitHub API → wait 60 s; do not retry in a loop

---

## Stage 4: HTML Sanitization (Fallback Only)

Prefer direct Markdown publishing. Use this HTML sanitization path only when the user explicitly requests HTML publishing or when the Markdown API path is unavailable.

**Always sanitize HTML before HTML publishing. Unsanitized HTML causes WeChat to silently strip content or reject the draft.**

Required removals:

```javascript
// Strip all <svg>...</svg> blocks (WeChat renders them as broken boxes)
html = html.replace(/<svg[\s\S]*?<\/svg>/gi, '');

// Strip all hyperlinks but keep link text
html = html.replace(/<a\s[^>]*>([\s\S]*?)<\/a>/gi, '$1');

// Strip <script> and <style> blocks
html = html.replace(/<script[\s\S]*?<\/script>/gi, '');
html = html.replace(/<style[\s\S]*?<\/style>/gi, '');
```

Failure modes:
- [ ] SVG present in output → WeChat renders blank boxes; strip all SVG
- [ ] Hyperlinks present → WeChat strips links silently, breaking layout; strip all `<a>` tags
- [ ] Inline `style="..."` with `position:fixed` or `position:absolute` → strip or replace with static positioning
- [ ] `<iframe>` embeds → not supported; remove entirely
- [ ] Emoji in HTML entity form (`&#x1F600;`) → usually fine; raw emoji also fine; test renders both ways
- [ ] `<table>` with percentage widths → often collapses on mobile; use `width:100%` max

---

## Stage 5: Publish

### Preferred: Direct Markdown Publish

Read `$HOME/.baoyu-skills/baoyu-post-to-wechat/EXTEND.md` if present for local defaults. Resolve theme/color using the shared visual reference: explicit user, article and account preferences take precedence; otherwise start with `modern` and `#59766C`. Check supported renderer options and inspect local 375px/430px previews before upload, recording unsupported layout differences. Keep the final Markdown as the publication input; the following command shows the default starting point:

```bash
bun "$MUFENG_WECHAT_SCRIPT" \
  <article.md> \
  --account <account-alias> \
  --theme modern \
  --color '#59766C' \
  --author changyou \
  --cover <cover-url>
```

Before calling the script:
- Ensure frontmatter has `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and `coverImage`.
- Ensure `coverImage` and inline images use raw GitHub HTTPS URLs.
- Ensure the required WeChat ending hook exists exactly once.
- Include a title explicitly only if it cannot be reliably extracted from frontmatter or the first H1.

After `draft/add` returns `media_id`, call `POST https://api.weixin.qq.com/cgi-bin/draft/get` with body `{"media_id":"<returned-media-id>"}` using the same account's access token and configured transport (including remote-api when selected). Keep tokens out of logs. Inspect returned title, author, body, cover reference and image references against the final article. Save a redacted verification record in the project.

The current upload script does not perform this read-back check automatically; execute it separately. Do not create a duplicate draft when verification fails. Report “草稿上传成功，读取验证未完成” with the existing `media_id` and the concrete error.

For explicit public-publication requests only, verify the draft first, then use the supported publication API and query its final status. A submission receipt is not publication success. If unsupported or denied, report that blocker while preserving the verified draft.

Original declaration and platform topic tags unsupported by the selected API are pending manual settings, not prerequisites for draft upload.

### Fallback: HTML Publish

Use HTML only when Markdown rendering is unavailable or the user explicitly requests HTML. HTML does not bypass authentication, IP or permission errors. Use the same API script and selected account; sanitize HTML first and pass a non-empty title:

```bash
bun "$MUFENG_WECHAT_SCRIPT" \
  ./output.html \
  --account <account-alias> \
  --title "Article Title Here" \
  --author changyou \
  --cover <cover-url>
```

Read back and report the draft through API as in the Markdown path.

Failure modes:
- [ ] Missing `--title` → validate before upload; if an incorrect draft already exists, correct that draft through a supported API or report the issue, rather than creating a duplicate
- [ ] Title contains special characters (`<`, `>`, `"`) → escape or strip before passing
- [ ] `npx` used instead of `bun` → nvm/node conflicts; always use `bun`
- [ ] Draft created but not publicly published → expected for the default draft workflow. Do not automatically call `freepublish/submit`.
- [ ] Explicit public publication fails → inspect the actual permission/error response; do not assume a fixed follower threshold.
- [ ] Publish succeeds but images missing → image URLs were not publicly accessible at publish time; verify GitHub raw URLs return 200 before calling publish

---

## Full Pre-Publish Checklist

Run through this in order before every publish:

**Content strategy:**
- [ ] **Title**: 18-24 字，首词为 AI 热词，无标题党措辞，含数字或具体场景
- [ ] **Opening**: 前 150 字直接给出核心价值，无背景铺垫
- [ ] **Images**: 配图必须服务内容；优先真实截图、Mermaid/SVG/HTML 图解、代码截图；imagegen 只用于封面背景或少量章节氛围图
- [ ] **Cover**: 默认完整无字封面；标题仅在需要时独立排版；已按统一规范检查缩略图、横幅及中心方形裁切，避免无效留白和物件堆叠
- [ ] **Frontmatter**: Markdown has `title`, `slug`, `author`, `date`, `category`, `summary`, `tags`, and `coverImage`
- [ ] **Ending**: 结尾有主题相关 hook，且固定品牌 follow block 只出现一次
- [ ] **Original**: 已设置并验证，或明确记录为待手动设置（不阻塞草稿上传）
- [ ] **Tags**: 已设置并验证，或列出建议话题标签并记录为待手动设置（不阻塞草稿上传）
- [ ] **Timing**: 草稿随时上传；正式发布时间仅按用户明确要求处理

**Technical:**
- [ ] **IP**: Egress IP recorded where available; API error inspected without requiring backend UI pre-check
- [ ] **Images**: Provider follows current user instructions and applicable AGENTS.md; otherwise follows the host-specific tools in `references/platforms.md`, with no unapproved fallback. Prompts and adopted assets are stored in the project.
- [ ] **Images and layout**: Shared visual checks run on actual assets and local 375px/430px previews; any missing checks or unsupported theme values explicitly reported, with no claim of visual validation before preview.
- [ ] **Images**: Uploaded to `mf-blog/blogPictures/main/images/<article-slug>`; raw HTTPS URLs verified with `curl -I <url>` returning 200
- [ ] **Markdown publish**: Final `.md` file is used directly with `wechat-api.ts`
- [ ] **HTML fallback**: If HTML publishing is used, SVG blocks and `<a>`, `<script>`, `<style>`, `<iframe>` tags are sanitized
- [ ] **Command**: `bun` used (not `npx`)
- [ ] **Command**: HTML fallback includes non-empty `--title`; Markdown path has extractable frontmatter title or H1
- [ ] **Verify**: `draft/get` on the selected account confirms the uploaded draft; report read-back failures separately and do not duplicate uploads

---

## Quick Reference

| Stage | Key Rule | Common Mistake |
|-------|----------|----------------|
| Content strategy | 标题 18-26 字 + AI 热词前置；前 150 字直给价值；结尾引导"在看" | 用标题党措辞；从背景铺垫开篇 |
| Timing | 草稿随时上传；时段建议需账号数据验证 | 为等待推荐时段阻塞草稿上传 |
| IP check | 记录出口 IP，按实际 API 错误排查 | 强制打开后台，或把所有 401/403 当成白名单错误 |
| Image gen | 统一视觉规范；完整无字封面；正文按解释与证据需要配图；实际检查裁切和手机预览 | 无效留白、灰暗物件堆叠、伪 UI；未预览就声称验证通过 |
| Frontmatter | `slug/category/summary/tags/coverImage` present before publishing | Only putting summary/tags in body |
| GitHub upload | Fixed `mf-blog/blogPictures` path, helper script, HTTPS raw URL | Reusing filename manually → 422 error |
| HTML sanitize | Fallback only; strip SVG + `<a>` tags | Pre-converting Markdown unnecessarily |
| Publish | Markdown + API 上传草稿；同账号 `draft/get` 验证 | 默认走浏览器；把草稿上传说成正式发布；把手动设置当成上传阻塞项 |
