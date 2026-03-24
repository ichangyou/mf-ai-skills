---
name: wechat-full
description: Use when publishing articles to WeChat Official Account (微信公众号), including tasks that involve generating images, uploading assets to GitHub, converting markdown to HTML, or calling the WeChat API. Also use when any step of a previous WeChat publish attempt failed.
---

# WeChat Full Publishing Workflow

## Overview

End-to-end skill for publishing articles to a WeChat Official Account. Covers every stage: IP verification, image generation (DashScope only), GitHub asset upload, HTML sanitization, and final publish. Follow stages in order — skipping any stage causes silent failures downstream.

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

## Stage 2: Image Generation — DashScope Only

**Always use DashScope. Do NOT use Google API (quota exhausts silently).**

Use the `content-skills:baoyu-image-gen` skill with explicit provider flag:

```bash
# Always pass --provider dashscope explicitly
bun run image-gen --provider dashscope --prompt "..." --aspect-ratio 16:9
```

Failure modes:
- [ ] Google API used instead of DashScope → regenerate with DashScope
- [ ] Chinese text in image is garbled/blurry → known limitation; use overlay text in HTML instead of embedding Chinese in the prompt
- [ ] DashScope quota exceeded → check DashScope console; switch model tier or wait
- [ ] Image returned but too small → specify `--quality 2k` or `--quality 4k`
- [ ] No image output, no error → DashScope endpoint timeout; retry once; if still failing, check API key

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

- [ ] **IP**: Current outbound IP is whitelisted in WeChat MP backend
- [ ] **Images**: Generated with DashScope (not Google); no Chinese text embedded in image
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
| IP check | Do before any API call | Assuming IP hasn't changed |
| Image gen | DashScope always | Using Google API (silent quota failure) |
| GitHub upload | Unique filename, HTTPS raw URL | Reusing filename → 422 error |
| HTML sanitize | Strip SVG + `<a>` tags | Forgetting SVG strips |
| Publish | `--title` required, use `bun` | Missing `--title`, using `npx` |
