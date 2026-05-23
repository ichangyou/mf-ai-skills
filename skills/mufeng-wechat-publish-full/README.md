# mufeng-wechat-publish-full

> 微信公众号全流程发布工作流 / End-to-end WeChat Official Account publishing workflow

---

## 中文说明

### 功能描述

覆盖微信公众号发布全流程的完整工作流，从内容策略优化到最终发布，共 6 个阶段。任何阶段失败后均可重新触发此 skill 进行定向修复。

包含功能：
- 微信推荐算法内容策略优化（Stage 0）
- IP 白名单检查（Stage 1）
- DashScope 图片生成（Stage 2）
- GitHub 图床上传（Stage 3）
- HTML 净化（Stage 4）
- 微信 API 发布（Stage 5）

### 安装与激活

本 skill 通过 Claude Code 的 Skill 系统自动发现，无需单独安装。在 Claude Code 对话中输入以下命令激活：

```
/mufeng-wechat-publish-full
```

### 使用方式

**完整流程发布**：

```
/mufeng-wechat-publish-full
[粘贴 Markdown 文章内容]
```

**修复之前失败的步骤**：

```
/mufeng-wechat-publish-full
上次 Stage 3 GitHub 上传失败了，文章如下：[内容]
```

### 六阶段工作流

| 阶段 | 内容 | 关键规则 |
|------|------|---------|
| Stage 0 | 内容策略（推荐曝光优化） | 标题 18-24 字，首词为 AI 热词；前 150 字直给核心价值；结尾引导「在看」 |
| Stage 1 | IP 白名单检查 | 任何 API 调用前必须先检查当前出口 IP 是否在白名单中 |
| Stage 2 | 图片生成（DashScope） | 必须用 DashScope；中文文字不能嵌入图片（会乱码）|
| Stage 3 | GitHub 图片上传 | 文件名必须唯一；使用 HTTPS raw URL；图片 < 5MB |
| Stage 4 | HTML 净化 | 去除 SVG、`<a>` 标签、`<script>`、`<style>`、`<iframe>` |
| Stage 5 | 发布 | `--title` 必填；使用 `bun`，不用 `npx` |

### 发布前检查清单

**内容策略**

- 标题 18-24 字，首词为 AI 热词，无标题党措辞
- 前 150 字直接给出核心价值，不铺垫背景
- 每 400-600 字有一张图（降低跳出率）
- 结尾有引导「在看」或留言的句子
- 已开启原创标识
- 已添加 2-3 个话题标签（#人工智能 等）
- 发布时间在工作日 20:00-22:00 或 12:00-13:00

**技术**

- 当前出口 IP 已在微信公众平台白名单中
- 图片使用 DashScope 生成（不用 Google API）
- GitHub raw HTTPS URL 已通过 `curl -I` 验证返回 200
- HTML 已去除 SVG、所有 `<a>` 标签、`<script>`、`<style>`、`<iframe>`
- 发布命令使用 `bun`（不用 `npx`）
- `--title` 参数已提供且非空

### 常见故障处理

| 错误 | 原因 | 解决 |
|------|------|------|
| 401/403（无明显 auth 错误）| IP 未白名单 | 检查出口 IP，添加到白名单 |
| Stage 2 图片中文乱码 | DashScope 不支持中文文字生成 | 改用 HTML 文字叠加层 |
| Stage 3 返回 422 | 文件名已存在 | 使用时间戳后缀生成唯一文件名 |
| 草稿已创建但未发布 | `freePublish.submit` 未调用 | 检查是否完成了两步：addDraft → submit |

---

## English Guide

### Description

A complete end-to-end WeChat Official Account publishing workflow covering six stages, from content strategy optimization to final publication. Can be re-triggered at any point to fix a failed step.

Capabilities:
- WeChat recommendation algorithm content strategy optimization (Stage 0)
- IP whitelist check (Stage 1)
- DashScope image generation (Stage 2)
- GitHub image hosting upload (Stage 3)
- HTML sanitization (Stage 4)
- WeChat API publish (Stage 5)

### Installation & Activation

This skill is auto-discovered by Claude Code's Skill system. No separate installation is required. Activate in Claude Code chat:

```
/mufeng-wechat-publish-full
```

### Usage

**Full workflow publish**:

```
/mufeng-wechat-publish-full
[Paste Markdown article content]
```

**Fix a previously failed step**:

```
/mufeng-wechat-publish-full
Stage 3 GitHub upload failed last time. Article content below: [content]
```

### Six-Stage Workflow

| Stage | Content | Key Rule |
|-------|---------|----------|
| Stage 0 | Content strategy (recommendation optimization) | Title 18-24 chars, AI hot word first; first 150 chars deliver core value; end with "Wow" prompt |
| Stage 1 | IP whitelist check | Verify current outbound IP is whitelisted before any API call |
| Stage 2 | Image generation (DashScope) | DashScope only; no Chinese text embedded in images (renders garbled) |
| Stage 3 | GitHub image upload | Unique filename required; HTTPS raw URL; image < 5MB |
| Stage 4 | HTML sanitization | Strip SVG, `<a>` tags, `<script>`, `<style>`, `<iframe>` |
| Stage 5 | Publish | `--title` required; use `bun`, not `npx` |

### Pre-Publish Checklist

**Content strategy**

- Title 18-24 chars, AI hot word first, no clickbait phrasing
- First 150 chars deliver core value without background buildup
- One image per 400-600 chars (reduces drop-off rate)
- Ending contains a prompt to "Wow" or leave a comment
- Original mark (原创) enabled
- 2-3 topic tags added (#人工智能, etc.)
- Publish time: weekday 20:00-22:00 or 12:00-13:00

**Technical**

- Current outbound IP is whitelisted in WeChat MP backend
- Images generated with DashScope (not Google API)
- GitHub raw HTTPS URLs verified with `curl -I` returning 200
- HTML stripped of SVG, all `<a>` tags, `<script>`, `<style>`, `<iframe>`
- Publish command uses `bun` (not `npx`)
- `--title` parameter is present and non-empty

### Common Error Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| 401/403 (no obvious auth error) | IP not whitelisted | Check outbound IP, add to whitelist |
| Stage 2 Chinese text garbled in image | DashScope can't render Chinese in generated images | Use HTML text overlay instead |
| Stage 3 returns 422 | Filename already exists | Use timestamp suffix to generate a unique filename |
| Draft created but not published | `freePublish.submit` not called | Ensure both steps run: addDraft → submit |
