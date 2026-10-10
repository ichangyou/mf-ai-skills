# mufeng-wechat-publish-full

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

## 调用

Codex：

```text
$mufeng-wechat-publish-full [任务或素材]
```

Claude Code：

```text
/mufeng-wechat-publish-full [任务或素材]
```

## 依赖与执行范围

已认证 gh；生图需要已配置工具；发布需要 Bun、baoyu-post-to-wechat 和公众号凭据。

“支持”表示提供两端入口和执行说明；外部服务、账号认证及工具能力需单独配置。实际执行规则见 [SKILL.md](SKILL.md)。

运行脚本前，将 shell 变量 `SKILL_DIR` 设为实际安装目录（包含本文件和 `SKILL.md` 的目录）。相对资源路径均以该目录为准。

面向微信公众号的完整发布工作流 skill。它覆盖从文章策略、Markdown 元数据、封面和配图、GitHub 图床上传，到微信 API 草稿上传、读取验证和 HTML 兜底的全过程。默认不正式发布或群发。

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
- 默认全程使用 API，不打开公众号后台或调用 Computer Use；只有用户明确要求浏览器操作时才使用。
- “发布到公众号”默认是上传草稿箱。只有明确要求“正式发布”或“群发”才进入公开发布流程。
- 先记录出口 IP，再按实际 API 错误排查；无需预先打开后台检查白名单。
- 上传后用同账号 `draft/get` 验证。原创标识和平台话题标签若 API 不支持，记录为待手动设置，不阻塞上传。

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
- API 请求的实际出口 IP 需符合白名单配置；无需预先打开后台核对。可先记录本机出口 IP：

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
9. 用同账号 API `draft/get` 读取返回的 `media_id`，核对标题、正文、封面和图片引用。
10. 分别报告文章完成、草稿上传、读取验证和正式发布状态；默认到验证草稿即完成。

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
python3 "$SKILL_DIR/scripts/upload_github_images.py" \
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

先按 [平台配置](references/platforms.md) 设置实际发布脚本与凭据。

优先使用 Markdown 发布路径：

```bash
bun "$MUFENG_WECHAT_SCRIPT" \
  <article.md> \
  --account <account-alias> \
  --theme default \
  --author changyou \
  --cover <cover-url>
```

沐风iOS 使用 `--account mufeng-ios`。这个脚本只调用 `draft/add`，读取验证需要另行执行。验证失败时保留已有 `media_id`，不重复上传草稿。

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

- 明确的无效 IP 错误（如 `40164`）：报告账号、出口 IP 和脱敏错误，等待白名单修复，或使用已配置的授权 remote-api 路径。
- HTTP `401` / `403`：检查具体返回错误，不能直接断定是 IP 白名单问题。
- GitHub API `422`：远程文件已存在；让 helper 自动追加时间戳，或使用 `--overwrite`。
- 微信草稿图片缺失：先用 `curl -I <raw-url>` 确认图片返回 `200`。
- 封面出现乱码中文或假 UI：不要让 imagegen 生成文字；用 HTML/CSS 或后期工具叠字。
- HTML 发布后样式丢失：检查是否包含 SVG、链接、脚本、iframe 或微信不支持的定位样式。

## 维护说明

更新发布规则时，优先修改 `SKILL.md`。如果变更会影响人工使用方式、命令参数或前置条件，也同步更新本 README。
