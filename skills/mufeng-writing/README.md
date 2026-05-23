# mufeng-writing

> 沐风微信公众号写作助手 / WeChat blog writing assistant for Joey (沐风)

---

## 中文说明

### 功能描述

沐风（Joey）专属微信公众号写作助手。核心定位是面向微信公众号的 AI 技术博客，兼顾个人成长、读书笔记、传统文化、理财投资等类型。根据微信推荐算法（完读率、分享率、收藏率、搜索收录）优化文章结构与标题，同时保持作者个人写作风格。

### 安装与激活

本 skill 通过 Claude Code 的 Skill 系统自动发现，无需单独安装。确认已将 `mf-ai-skills` 项目路径添加到 Claude Code 的 skill 加载目录后，在对话中直接输入命令即可激活。

### 使用方式

```
/mufeng-writing [主题] / [类型] / [关键信息] / [篇幅]
```

**最简调用**（skill 会逐步询问缺失信息）：

```
/mufeng-writing
```

**完整调用示例**：

```
/mufeng-writing Claude Code 实测 / C / 用了3个月的真实体验，10个高频场景 / 中文
```

```
/mufeng-writing 我用 MCP 连接了数据库，效率提升了 5 倍 / C / 操作步骤和踩坑记录 / 长文
```

### 参数说明

| 参数 | 必填 | 可选值 |
|------|------|--------|
| 主题 | 是 | 任意文章主题 |
| 类型 | 否 | C（AI技术）/ B（个人成长）/ A（读书笔记）/ D（传统文化）/ E（理财） |
| 关键信息 | 否 | 核心内容、数据、实测结果、故事、观点 |
| 篇幅 | 否 | 短文（800字）/ 中文（1500字）/ 长文（2500字+） |

### 输出格式

输出完整的 Markdown 文章，包含：

- YAML frontmatter（title、date、tags、wechat\_topic、summary）
- 正文（符合微信格式规范：`##` 二级标题、短段落、移动端优化）
- 结尾互动引导语（自动生成，匹配文章类型）
- 落款（日期、地点、AI 辅助声明）

### 标题规则

标题长度 18-26 字，遵循四种结构公式之一：

- `[工具/场景] + 实测/亲测 + 结论`
- `[反常识结论] + 原因`
- `[数字/量化] + 行动 + 收益`
- `[读者痛点] + 解法`

### 注意事项

- 表格使用文字（"可"/"否"）代替 emoji，避免微信渲染问题
- 禁止使用「首先、其次、最后」「总的来说」等模板化表达
- 大段代码超过 20 行时自动截断并加说明

---

## English Guide

### Description

Joey's personal WeChat Official Account writing assistant. Primarily targets AI tech blog posts, with support for personal growth, book notes, traditional culture, and investing topics. Optimizes article structure and titles for WeChat's recommendation algorithm (completion rate, share rate, save rate, search indexing) while preserving the author's unique voice.

### Installation & Activation

This skill is auto-discovered by Claude Code's Skill system. No separate installation is needed. Once the `mf-ai-skills` project path is added to Claude Code's skill loading directory, type the command in the chat to activate it.

### Usage

```
/mufeng-writing [topic] / [type] / [key-info] / [length]
```

**Minimal invocation** (skill asks for missing info):

```
/mufeng-writing
```

**Full invocation examples**:

```
/mufeng-writing Claude Code real-world test / C / 3 months of genuine use, 10 high-frequency scenarios / medium
```

```
/mufeng-writing I connected a DB via MCP and got 5x efficiency / C / step-by-step + pitfalls / long
```

### Parameters

| Parameter | Required | Options |
|-----------|----------|---------|
| topic | Yes | Any article subject |
| type | No | C (AI tech) / B (personal growth) / A (book notes) / D (culture) / E (investing) |
| key-info | No | Core content, data, test results, stories, opinions |
| length | No | Short (800 ch) / Medium (1500 ch) / Long (2500+ ch) |

### Output Format

Complete Markdown article including:

- YAML frontmatter (title, date, tags, wechat\_topic, summary)
- Body text (WeChat-compatible: `##` headings, short paragraphs, mobile-optimized)
- Engagement prompt at the end (auto-generated, matched to article type)
- Footer (timestamp, location, AI-assist declaration)

### Title Rules

Titles are 18-26 Chinese characters, following one of four structural formulas:

- `[tool/scenario] + real-test + conclusion`
- `[counter-intuitive conclusion] + reason`
- `[number/quantity] + action + benefit`
- `[reader pain point] + solution`

### Notes

- Tables use text ("yes"/"no") instead of emoji for WeChat rendering compatibility
- Forbidden phrases: "firstly, secondly, finally", "in summary", passive voice
- Code blocks longer than 20 lines are automatically truncated with explanatory annotations
