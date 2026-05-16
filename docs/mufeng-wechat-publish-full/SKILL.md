---
name: mufeng-wechat-publish-full
description: Use when publishing articles to WeChat Official Account (微信公众号), including tasks that involve generating images, uploading assets to GitHub, converting markdown to HTML, or calling the WeChat API. Also use when any step of a previous WeChat publish attempt failed. Includes AI tech blog content strategy for maximizing WeChat platform recommendation (推荐曝光).
---

# Mufeng WeChat Full Publishing Workflow

## Overview

End-to-end skill for publishing AI tech blog articles to a WeChat Official Account. Covers every stage: content strategy for platform recommendations, IP verification, image generation (Google with DashScope fallback), GitHub asset upload, HTML sanitization, and final publish. Follow stages in order — skipping any stage causes silent failures downstream.

---

## Stage 0: Content Strategy — AI Tech Blog for Maximum Recommendation (推荐曝光)

WeChat's recommendation system (看一看/搜一搜/流量主) surfaces articles based on **completion rate (完读率)**, **share rate**, and **Wow/Like signals**. For AI tech content, follow these rules to optimize for each signal.

### Title Formula (标题)

WeChat's algorithm weights the title heavily for initial distribution. For AI tech:

**四种有效结构（四选一）：**
- `[具体工具/场景] + 实测/亲测 + 结论` — e.g., "我用 Claude 做了三个月 AI 助手，说几句真实感受"
- `[反常识结论] + 原因` — e.g., "别急着学提示词，先搞清楚这件事"
- `[数字/量化] + 行动 + 收益` — e.g., "10 个让 Claude Code 效率翻倍的使用习惯"
- `[读者痛点] + 解法` — e.g., "AI 工具用了一年，我踩过的最贵的坑"

带数字的标题完读率高于无数字标题（如"5 个技巧"优于"一些技巧"）。

**Title rules:**
- 长度：18-26 个汉字（含标点），不超过 30 字
- 避免标题党措辞（微信会降权）：不用"震惊""万万没想到""99% 的人不知道""赶紧转"
- AI 技术类关键词前置：Claude、MCP、Agent、Cursor、提示词、大模型等核心词放标题前半段，利于搜索收录
- 不用问号结尾——微信算法对疑问句标题分发更保守
- 每次输出 3 个标题备选（利益驱动型 / 反常识型 / 代入感型），让作者选择

**Bad → Good examples:**
- ❌ "分享一些 AI 工具使用心得" → ✓ "用了 3 个月 Cursor，整理出这 8 个真正提效的用法"
- ❌ "关于大模型 Prompt 的思考" → ✓ "我的 Prompt 从 3 句话精简到 1 句，效果反而更好——原因在这里"

### Content Structure for High Completion Rate (完读率)

完读率是微信推荐算法最重要的信号。目标：读者打开后读完全文。

**Opening (前 150 字，最关键):**
- 第一段必须直接给出"为什么值得读"——一句话说清本文价值
- 不要用背景铺垫开头；不要从历史讲起
- 直接给结论或最有冲击力的发现，再往回解释

**Body structure:**
- 每 400-600 字插入一张图（降低跳出率）
- 段落不超过 4 行（移动端阅读节奏）
- 每个 H2/H3 小标题要能独立成句，让快速浏览者也能获得价值
- 代码块要有上下文说明——纯代码块会造成完读率骤降
- 实测数据 > 理论描述（截图、benchmark、具体数字）

**Ending (结尾 驱动分享/在看):**
- 最后一段给出"行动号召"或总结句，引导点击"在看"
- 不要用"感谢阅读"结尾——用有信息量的总结句
- 可加："如果你也在用 [工具]，欢迎留言你的用法"——激活评论信号

### Timing (发布时间)

微信推荐窗口在发布后的 2-4 小时内最关键。选择：
- **最佳时间段**：周二至周四，20:00-22:00（用户活跃 + 竞争文章相对少）
- **次选**：工作日 12:00-13:00（午休）
- **避开**：周一早晨、周五下午、节假日（竞争高或用户分散）

### Cover Image (封面图)

封面图决定分享卡片点击率：
- **比例**：2.35:1（横版）用于文章列表；1:1 用于分享卡片
- **AI 科技主题风格**：深色背景 + 高对比度文字 + 科技感视觉元素（电路、粒子、代码片段）
- **文字要求**：封面图上必须有标题关键词（3-6 个字）；用 HTML text overlay 而非 AI 生成文字
- 避免纯文字封面（低视觉吸引力）；避免人脸过多（微信审核敏感）

### Tags & Category (话题标签)

发布时选择话题标签（#话题）影响搜一搜收录：
- AI 相关优先选：`#人工智能` `#大模型` `#AI工具` `#程序员` `#Claude` `#ChatGPT` `#Cursor`
- 每篇文章添加 2-3 个话题标签（过多稀释权重）
- 话题名与文章关键词一致时搜索权重更高

### Original Mark (原创标识)

- 每篇文章必须开启"原创"标识——原创文章获得微信额外分发权重
- 原创文章可被其他账号转载（并标注来源），增加曝光
- 转载他人文章不得标原创；AI 辅助写作的原创内容可标原创（只要主要内容是自己的）

### What WeChat's Algorithm Rewards (算法加分项)

| 信号 | 权重 | 如何优化 |
|------|------|---------|
| 完读率 | 极高 | 精简开头、段落短、图文穿插 |
| 分享率 | 高 | 结尾引导、内容有"值得分享"价值 |
| 在看（Wow）率 | 高 | 结尾引导点"在看" |
| 评论数 | 中 | 结尾提问、观点有争议性 |
| 收藏率 | 中 | 提供"工具性"内容（清单、对比表、命令速查） |
| 打开率 | 中 | 标题 + 封面图优化 |

**AI 内容加分项**：
- 有实际可运行的 Prompt 或代码（读者会收藏）
- 涉及最近 2 周内发布的新模型/新工具（时效性加权）
- 有横向对比（Claude vs GPT vs Gemini）——争议性驱动评论
- 揭示"反直觉"结论——驱动分享

---

---

## Stage 1: Pre-flight — IP Whitelist Check

**Do this before any API call. A 401/403 with no obvious auth error is almost always an IP issue.**

```bash
# Check current outbound IP
curl -s https://api.ipify.org

# Compare against whitelisted IPs in WeChat MP backend:
# Settings > Developer Tools > IP Whitelist
```

Failure modes:
- [ ] IP not whitelisted → add it in WeChat MP backend before continuing
- [ ] VPN or proxy active → current IP differs from whitelisted IP; disable or whitelist VPN IP
- [ ] Dynamic IP changed since last session → re-check; do not assume yesterday's IP is still valid

**Never retry API calls until IP is confirmed whitelisted.**

---

## Stage 2: Image Generation

**Prefer Google API (Gemini); fallback to DashScope if Google fails or quota is exhausted.**

Use the `content-skills:baoyu-image-gen` skill. By default, it will use your preferred provider. To force a fallback:

```bash
# Try Google first (default behavior or explicit)
bun run image-gen --prompt "..." --aspect-ratio 16:9

# Fallback to DashScope if Google fails
bun run image-gen --provider dashscope --prompt "..." --aspect-ratio 16:9
```

Failure modes:
- [ ] Google API fails/quota exceeded → fallback to DashScope
- [ ] Chinese text in image is garbled/blurry → known limitation; use overlay text in HTML instead of embedding Chinese in the prompt
- [ ] DashScope quota exceeded → check DashScope console; switch model tier or wait
- [ ] Image returned but too small → specify `--quality 2k` or `--quality 4k`
- [ ] No image output, no error → API endpoint timeout; retry once; if still failing, check API key

---

## Stage 3: GitHub Image Upload

Upload images to a GitHub repo so WeChat can reference stable CDN URLs. WeChat rejects direct local paths and many third-party CDNs.

```bash
# Upload via GitHub API (replace vars):
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

## Stage 4: HTML Sanitization

**Always sanitize HTML before publishing. Unsanitized HTML causes WeChat to silently strip content or reject the draft.**

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

## Stage 5: Publish — Required Parameters

**`--title` is mandatory every time. A publish call without `--title` will either fail or create an untitled draft that cannot be recovered without manual editing.**

```bash
# Correct form — always include --title:
bun run wechat-publish \
  --title "Article Title Here" \
  --html "./output.html" \
  --author "changyou"

# WRONG — missing --title:
bun run wechat-publish --html "./output.html"   # DO NOT DO THIS
```

Failure modes:
- [ ] Missing `--title` → draft created with empty title; must manually fix in WeChat MP backend
- [ ] Title contains special characters (`<`, `>`, `"`) → escape or strip before passing
- [ ] `npx` used instead of `bun` → nvm/node conflicts; always use `bun`
- [ ] Draft created but not published → check if publish step is separate from draft upload; WeChat API has two calls: `addDraft` then `freePublish.submit`
- [ ] Article appears in draft list but not published → `freePublish.submit` may not have been called, or account lacks publish permission (requires 100+ followers for some account types)
- [ ] Publish succeeds but images missing → image URLs were not publicly accessible at publish time; verify GitHub raw URLs return 200 before calling publish

---

## Full Pre-Publish Checklist

Run through this in order before every publish:

**Content strategy:**
- [ ] **Title**: 18-24 字，首词为 AI 热词，无标题党措辞，含数字或具体场景
- [ ] **Opening**: 前 150 字直接给出核心价值，无背景铺垫
- [ ] **Images**: 每 400-600 字有一张图；封面图有文字 overlay 关键词
- [ ] **Ending**: 结尾有引导"在看"或留言的句子
- [ ] **Original**: 已开启原创标识
- [ ] **Tags**: 已添加 2-3 个相关话题标签（#人工智能 等）
- [ ] **Timing**: 发布时间在 20:00-22:00 或 12:00-13:00 工作日

**Technical:**
- [ ] **IP**: Current outbound IP is whitelisted in WeChat MP backend
- [ ] **Images**: Generated with Google (primary) or DashScope (fallback); no Chinese text embedded in image
- [ ] **Images**: Uploaded to GitHub; raw HTTPS URLs verified with `curl -I <url>` returning 200
- [ ] **HTML**: SVG blocks stripped
- [ ] **HTML**: All `<a href>` hyperlinks stripped (text preserved)
- [ ] **HTML**: `<script>`, `<style>`, `<iframe>` removed
- [ ] **HTML**: No `position:fixed/absolute` inline styles
- [ ] **Command**: `bun` used (not `npx`)
- [ ] **Command**: `--title` parameter present and non-empty
- [ ] **Verify**: Draft visible in WeChat MP backend before triggering publish

---

## Quick Reference

| Stage | Key Rule | Common Mistake |
|-------|----------|----------------|
| Content strategy | 标题 18-26 字 + AI 热词前置；前 150 字直给价值；结尾引导"在看" | 用标题党措辞；从背景铺垫开篇 |
| Timing | 工作日 20:00-22:00 发布 | 周一早晨或节假日发 |
| IP check | Do before any API call | Assuming IP hasn't changed |
| Image gen | Google/DashScope | Skipping fallback when Google fails |
| GitHub upload | Unique filename, HTTPS raw URL | Reusing filename → 422 error |
| HTML sanitize | Strip SVG + `<a>` tags | Forgetting SVG strips |
| Publish | `--title` required, use `bun`; enable 原创 + 话题标签 | Missing `--title`; forgetting 原创 mark |
