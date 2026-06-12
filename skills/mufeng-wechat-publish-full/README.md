# mufeng-wechat-publish-full

面向微信公众号的完整发布工作流 skill。它覆盖从文章策略、Markdown 元数据、封面和配图、GitHub 图床上传，到微信 API 发布和 HTML 兜底发布的全过程。

`SKILL.md` 是给 agent 执行时读取的详细规则；本 README 是给人快速理解和维护用的入口说明。

## 适用场景

- 发布 AI 技术博客到微信公众号。
- 给待发布 Markdown 补齐 SEO/GEO 友好的 frontmatter。
- 生成或整理封面图、正文配图、截图、图解。
- 将图片上传到固定 GitHub 图床。
- 使用 Markdown 直发微信，或在必要时走 HTML fallback。
- 处理上一次微信发布失败后的排查和重试。

## 核心原则

- 优先从最终 Markdown 文件直接发布，不要默认预转 HTML。
- 每篇文章发布前必须有完整 frontmatter：`title`、`slug`、`author`、`date`、`category`、`summary`、`tags`、`coverImage`。
- 统一使用同一个 `article-slug`，贯穿本地图片目录、GitHub 远程目录、frontmatter 和完成报告。
- 图片固定上传到 `mf-blog/blogPictures` 的 `main` 分支。
- 生成式图片主要用于无文字封面背景；正文优先使用真实截图、确定性图表、代码截图。
- 发布前先确认当前出口 IP 已加入微信公众号后台 IP 白名单。

## 目录结构

```text
mufeng-wechat-publish-full/
├── README.md
├── SKILL.md
└── scripts/
    └── upload_github_images.py
```

## 前置条件

- `bun`：用于调用微信发布脚本。
- `python3`：用于运行图片上传 helper。
- `gh`：GitHub CLI，且已登录有权限写入 `mf-blog/blogPictures`。
- 微信公众号 API 凭据和本机默认配置应已在本地发布脚本环境中可用。
- 当前出口 IP 已配置到微信公众号后台：

```bash
curl -s https://api.ipify.org
```

## 推荐发布流程

1. 准备最终 Markdown。
2. 补齐或校验 YAML frontmatter。
3. 确定统一的 `article-slug`。
4. 准备封面和正文图片。
5. 上传图片到 GitHub 图床。
6. 将 Markdown 中的本地图片路径替换为 GitHub raw HTTPS URL。
7. 检查结尾互动 hook 和固定关注文案。
8. 用 Markdown 直发微信。
9. 到微信公众号后台确认草稿和发布状态。

## Frontmatter 模板

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

注意：字段名使用 `category`，不要写成 `categery`。

## 上传图片

推荐用内置 helper 上传 PNG 图片：

```bash
python3 "$HOME/.agents/skills/mufeng-wechat-publish-full/scripts/upload_github_images.py" \
  --repo "mf-blog/blogPictures" \
  --branch "main" \
  --remote-dir "images/<article-slug>" \
  --json-out "imgs/<article-slug>/github-image-urls.json" \
  imgs/<article-slug>/cover.png \
  imgs/<article-slug>/fig-01.png
```

脚本会：

- 校验 PNG 文件。
- 发现远程同名文件时自动追加时间戳，避免 GitHub API 422。
- 输出 `raw.githubusercontent.com` 图片 URL。
- 可选写入 JSON，方便回填 Markdown。

如需覆盖远程同名图片，显式加 `--overwrite`。

## Markdown 直发微信

优先使用 Markdown 发布路径：

```bash
bun /Users/changyou/.claude/plugins/marketplaces/baoyu-skills/skills/baoyu-post-to-wechat/scripts/wechat-api.ts \
  <article.md> \
  --theme default \
  --author changyou \
  --cover <cover-url>
```

发布前确认：

- `cover-url` 是公开可访问的 HTTPS 图片。
- Markdown 中所有图片都已替换为 GitHub raw URL。
- 标题可以从 frontmatter 或第一个 H1 稳定提取。
- 结尾互动 hook 只出现一次。

## HTML fallback

只有在 Markdown API 路径不可用，或用户明确要求 HTML 发布时才走 HTML fallback。

HTML 发布前必须清理不兼容内容：

- 移除 `<svg>`。
- 移除 `<script>` 和 `<style>`。
- 移除 `<iframe>`。
- 去掉 `<a>` 标签但保留链接文本。
- 避免 `position:fixed` 或 `position:absolute` 等微信可能剥离的样式。

HTML fallback 发布时必须显式传 `--title`。

## 常见故障

- `401` / `403`：优先检查 IP 白名单，不要盲目重试 API。
- GitHub API `422`：远程文件已存在；让 helper 自动追加时间戳，或使用 `--overwrite`。
- 微信草稿图片缺失：先用 `curl -I <raw-url>` 确认图片返回 `200`。
- 封面出现乱码中文或假 UI：不要让 imagegen 生成文字；用 HTML/CSS 或后期工具叠字。
- HTML 发布后样式丢失：检查是否包含 SVG、链接、脚本、iframe 或微信不支持的定位样式。

## 维护说明

更新发布规则时，优先修改 `SKILL.md`。如果变更会影响人工使用方式、命令参数或前置条件，也同步更新本 README。
