# mufeng-blog-writing

> 沐风技术博客写作助手（mufeng.blog）/ Technical blog writing assistant for mufeng.blog

---

## 中文说明

### 功能描述

面向 mufeng.blog 的技术博客写作助手。按 Joey 友好专业的写作风格输出技术文章，涵盖 iOS（Swift/Objective-C）、Java/Spring Boot、Vue.js、JavaScript/TypeScript 等技术栈。输出含可运行代码示例（附中文注释）、SEO 元数据，默认保存为本地 Markdown 文件。

### 安装与激活

本 skill 通过 Claude Code 的 Skill 系统自动发现，无需单独安装。在 Claude Code 对话中输入以下命令激活：

```
/mufeng-blog-writing
```

### 使用方式

```
/mufeng-blog-writing [话题描述]
```

**示例**：

```
/mufeng-blog-writing 写一篇 SwiftUI @State 和 @Binding 区别的文章
```

```
/mufeng-blog-writing Spring Boot 整合 Redis 缓存 — 教程类，包含完整代码
```

```
/mufeng-blog-writing iOS App 上架后 IAP 一直报错 StoreKit，如何排查
```

如果话题描述不完整，skill 会询问缺失信息并说明假设前提。

### 写作流程

1. 确认话题、文章类型（技术分享 / 教程 / 问题排查）、目标技术栈和深度
2. 依据 `references/templates.md` 选择对应文章结构
3. 按 `references/identity.md` 风格撰写正文，确保代码可运行
4. 使用 `references/seo-checklist.md` 生成优化标题、摘要（150-200 字）、标签（4-8 个）
5. 追加落款（日期、地点、AI 辅助声明）
6. 将生成文章保存为 `.md` 文件到当前工作目录

### 输出格式

```markdown
---
title: 文章标题
author: changyou
date: YYYY-MM-DD
---

# 标题

摘要：...

标签：...

[正文]

YYYY.MM.DD HH:mm
沪 · 赵巷

📌 声明：本文由 AI 辅助完成
```

### 文件保存规则

- 文件名默认使用文章标题
- 若目标文件已存在，自动追加 `-v2`、`-v3` 后缀，不覆盖原文件
- 如需指定路径，在命令中说明即可

### 注意事项

- 代码示例附中文注释，保证可直接运行
- SEO 检查清单自动执行，不需要手动触发
- 引用文件：`references/identity.md`（风格）、`references/templates.md`（模板）、`references/code-standards.md`（代码规范）

---

## English Guide

### Description

Technical blog writing assistant for mufeng.blog. Produces articles in Joey's friendly, professional tone, covering iOS (Swift/Objective-C), Java/Spring Boot, Vue.js, and JavaScript/TypeScript. Output includes runnable code examples with Chinese comments, SEO metadata, and is saved as a local Markdown file by default.

### Installation & Activation

This skill is auto-discovered by Claude Code's Skill system. No separate installation is required. Activate in Claude Code chat:

```
/mufeng-blog-writing
```

### Usage

```
/mufeng-blog-writing [topic description]
```

**Examples**:

```
/mufeng-blog-writing Write an article on the difference between SwiftUI @State and @Binding
```

```
/mufeng-blog-writing Spring Boot with Redis caching — tutorial style with full code
```

```
/mufeng-blog-writing Debugging StoreKit IAP errors after iOS App Store submission
```

If the topic description is incomplete, the skill will ask clarifying questions and state its assumptions.

### Writing Workflow

1. Confirm topic, article type (tech share / tutorial / troubleshooting), target stack, and depth
2. Select a structure template from `references/templates.md`
3. Draft the article in the style defined by `references/identity.md`, ensuring code is runnable
4. Generate an optimized title, summary (150-200 Chinese chars), and tags (4-8) using `references/seo-checklist.md`
5. Append footer (timestamp, location, AI-assist declaration)
6. Save the generated article as a `.md` file in the current working directory

### Output Format

```markdown
---
title: Article Title
author: changyou
date: YYYY-MM-DD
---

# Title

Summary: ...

Tags: ...

[body]

YYYY.MM.DD HH:mm
沪 · 赵巷

📌 声明：本文由 AI 辅助完成
```

### File Saving Rules

- Filename defaults to the article title
- If the target file already exists, appends `-v2`, `-v3`, etc. — never overwrites without explicit instruction
- Specify a custom path in the command if needed

### Notes

- Code examples include Chinese comments and are verified runnable
- SEO checklist runs automatically — no manual trigger needed
- Reference files: `references/identity.md` (style), `references/templates.md` (templates), `references/code-standards.md` (code conventions)
