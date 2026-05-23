# mufeng-codex-illustrated-wechat-publish

> Codex 图文微信发布 — 从素材到带插图的公众号文章一键发布  
> Codex Illustrated WeChat Publish — from source materials to illustrated WeChat article in one workflow

---

## 中文说明

### 功能描述

将指定目录中的素材自动转化为专业的微信公众号图文文章并发布。全流程涵盖：素材读取 → 文章生成（按 `mufeng-blog-writing` 规范）→ Codex 内置图像生成封面和插图 → GitHub 图床上传 → URL 插入文章 → 微信 API 发布。

**核心规则**：
- 所有图片使用 Codex 内置图像生成，不调用 OpenAI Images API、DashScope、Google 等外部图像 CLI（除非用户明确要求切换）
- 图片保存为 PNG 格式，不嵌入可读的中文文字、标注、水印
- 从 Markdown 直接发布，不预先转换为 HTML

### 安装与激活

本 skill 运行于 Codex 环境，依赖：
- Codex 内置图像生成能力
- GitHub CLI（已登录认证）
- 微信 API 发布脚本（baoyu-post-to-wechat）

环境变量配置：

```bash
export MUFENG_GITHUB_IMAGE_REPO=owner/repo
export MUFENG_GITHUB_IMAGE_BRANCH=main
export MUFENG_GITHUB_IMAGE_DIR=images/mufeng
```

在 Codex 环境中激活：

```
/mufeng-codex-illustrated-wechat-publish
```

### 使用方式

```
/mufeng-codex-illustrated-wechat-publish [目录路径]
```

**示例**：

```
# 使用当前目录的素材
/mufeng-codex-illustrated-wechat-publish

# 指定素材目录
/mufeng-codex-illustrated-wechat-publish ./my-article-materials
```

### 七步工作流程

**Step 1 — 读取素材，生成文章**

- 读取目录中所有 Markdown、文本笔记、大纲、代码片段等素材文件
- 跳过：build/cache/vendor 目录、图片生成目录、已有的 WeChat 输出目录
- 按 `mufeng-blog-writing` 的规范生成完整中文文章（含 frontmatter、摘要、标签、落款）
- 保存为 `.md` 文件；已存在时追加 `-v2`、`-v3` 后缀

**Step 2 — 制定图片方案**

- 1 张封面图（2.35:1 或 16:9 横版）
- 每 600-900 字或每个主要 H2 章节插入 1 张插图
- 短文（1 张封面 + 1-2 张插图），长文按章节配图
- 不在代码块、表格、列表、blockquote 或 YAML frontmatter 中插图

**Step 3 — 生成 PNG 图片**

```
图片存储路径：
imgs/<article-slug>/cover.png
imgs/<article-slug>/fig-01.png
imgs/<article-slug>/fig-02.png
```

- 封面：宽幅构图，有清晰焦点，无文字
- 插图：视觉化呈现对应章节的核心概念，不做纯装饰图

**Step 4 — 验证图片**

确认每张图片存在、非空、为 PNG 格式，单张不超过 5MB。

**Step 5 — 上传到 GitHub**

```bash
python3 "$HOME/.agents/skills/mufeng-codex-illustrated-wechat-publish/scripts/upload_github_images.py" \
  --repo "$MUFENG_GITHUB_IMAGE_REPO" \
  --branch "${MUFENG_GITHUB_IMAGE_BRANCH:-main}" \
  --remote-dir "${MUFENG_GITHUB_IMAGE_DIR:-images/mufeng}/<article-slug>" \
  --json-out "imgs/<article-slug>/github-image-urls.json" \
  imgs/<article-slug>/cover.png \
  imgs/<article-slug>/fig-01.png
```

注意：上传脚本使用 `gh api`，GitHub CLI 必须已安装并完成认证。

**Step 6 — 将图片 URL 插入文章**

- 在 frontmatter 中添加 `coverImage: <cover-url>`
- 在文章正文中按位置插入：

```markdown
![简洁描述](https://raw.githubusercontent.com/OWNER/REPO/main/images/mufeng/article/fig-01.png)
```

**Step 7 — 发布到微信**

```bash
bun ~/.claude/plugins/marketplaces/baoyu-skills/skills/baoyu-post-to-wechat/scripts/wechat-api.ts \
  <article.md> \
  --theme default \
  --author changyou \
  --cover <cover-url>
```

发布失败时先检查出口 IP 是否在微信公众平台白名单中。

### 完成报告

每次执行后输出：
- 使用的素材目录
- 生成文章的文件路径
- 封面 URL 和所有插图 URL
- 微信发布方式及结果（API 返回的草稿 `media_id`）
- 任何跳过的步骤或需要手动操作的事项

---

## English Guide

### Description

Converts source materials in a specified directory into a professional WeChat Official Account article with illustrations and publishes it. The full workflow covers: read materials → generate article (following `mufeng-blog-writing` conventions) → generate cover and inline illustrations using Codex → upload images to GitHub → insert URLs into article → publish via WeChat API.

**Core rules**:
- All images use Codex built-in image generation — does NOT call OpenAI Images API, DashScope, Google, or other external image CLIs (unless the user explicitly asks to switch)
- Images saved as PNG; no readable Chinese text, labels, or watermarks embedded
- Publishes directly from Markdown — does not pre-convert to HTML

### Installation & Activation

This skill runs in the Codex environment. Dependencies:
- Codex built-in image generation
- GitHub CLI (installed and authenticated)
- WeChat API publish script (baoyu-post-to-wechat)

Environment variable configuration:

```bash
export MUFENG_GITHUB_IMAGE_REPO=owner/repo
export MUFENG_GITHUB_IMAGE_BRANCH=main
export MUFENG_GITHUB_IMAGE_DIR=images/mufeng
```

Activate in Codex environment:

```
/mufeng-codex-illustrated-wechat-publish
```

### Usage

```
/mufeng-codex-illustrated-wechat-publish [directory path]
```

**Examples**:

```
# Use materials in the current directory
/mufeng-codex-illustrated-wechat-publish

# Specify a materials directory
/mufeng-codex-illustrated-wechat-publish ./my-article-materials
```

### Seven-Step Workflow

**Step 1 — Read materials, generate article**

- Read all Markdown, text notes, outlines, and code snippets from the directory
- Skip: build/cache/vendor folders, image generation folders, existing WeChat output folders
- Generate a complete Chinese WeChat article following `mufeng-blog-writing` conventions (frontmatter, summary, tags, footer)
- Save as `.md` file; append `-v2`, `-v3` suffix if file already exists

**Step 2 — Plan images**

- 1 cover image (2.35:1 or 16:9 landscape)
- 1 illustration per 600-900 Chinese characters or per major H2 section
- Short articles: 1 cover + 1-2 illustrations; long articles: one per major section
- Do not insert images inside code blocks, tables, lists, blockquotes, or YAML frontmatter

**Step 3 — Generate PNG images**

```
Storage path:
imgs/<article-slug>/cover.png
imgs/<article-slug>/fig-01.png
imgs/<article-slug>/fig-02.png
```

- Cover: wide-format editorial composition, clear focal point, no text
- Illustrations: visually represent the core idea of the nearby section — not generic decoration

**Step 4 — Validate images**

Verify each image exists, is non-empty, and is PNG format. Keep each PNG under 5MB.

**Step 5 — Upload to GitHub**

```bash
python3 "$HOME/.agents/skills/mufeng-codex-illustrated-wechat-publish/scripts/upload_github_images.py" \
  --repo "$MUFENG_GITHUB_IMAGE_REPO" \
  --branch "${MUFENG_GITHUB_IMAGE_BRANCH:-main}" \
  --remote-dir "${MUFENG_GITHUB_IMAGE_DIR:-images/mufeng}/<article-slug>" \
  --json-out "imgs/<article-slug>/github-image-urls.json" \
  imgs/<article-slug>/cover.png \
  imgs/<article-slug>/fig-01.png
```

Note: upload script uses `gh api` — GitHub CLI must be installed and authenticated.

**Step 6 — Insert image URLs into article**

- Add `coverImage: <cover-url>` to frontmatter
- Insert inline illustrations at the appropriate positions:

```markdown
![concise description](https://raw.githubusercontent.com/OWNER/REPO/main/images/mufeng/article/fig-01.png)
```

**Step 7 — Publish to WeChat**

```bash
bun ~/.claude/plugins/marketplaces/baoyu-skills/skills/baoyu-post-to-wechat/scripts/wechat-api.ts \
  <article.md> \
  --theme default \
  --author changyou \
  --cover <cover-url>
```

If publish fails with IP/auth errors, verify the current outbound IP is whitelisted in WeChat MP backend.

### Completion Report

After each run, outputs:
- Source material directory used
- Generated article file path
- Cover URL and all inline image URLs
- WeChat publishing method and result (draft `media_id` if API returns one)
- Any skipped steps or manual actions still required
