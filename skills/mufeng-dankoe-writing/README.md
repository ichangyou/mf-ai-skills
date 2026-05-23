# mufeng-dankoe-writing

> Dan Koe 风格深度长篇写作 / Deep long-form writing in Dan Koe's style

---

## 中文说明

### 功能描述

深度长篇写作风格指南，模仿 Dan Koe 的写作风格。适用于创作挑衅性、对话式、需要深度思考的内容——思想领袖文章、系统化框架文章、反主流叙事内容。篇幅 1000-2000 字，值得收藏反复阅读。

**核心风格特征**：
- **对话式挑衅**：用「你」直接与读者对话，开篇挑战既有观念
- **理论 + 实践**：前半部分深入理论/心理学/哲学，后半给出可执行步骤
- **反主流叙事**：提供「你可能没听过」的独特视角
- **节奏变化**：长句阐述 + 短句冲击，关键点单独成段

### 安装与激活

本 skill 通过 Claude Code / Codex 的 Skill 系统自动发现，无需单独安装。

**Claude Code 中激活**：

```
/mufeng-dankoe-writing [话题]
```

**Codex 中激活**：

```
请使用 mufeng-dankoe-writing 写作风格，写一篇关于……的长文
```

也支持以下关键词自动触发：`长篇文章`、`深度写作`、`Dan Koe 风格`、`挑衅性写作`、`思想领袖内容`、`系统化框架文章`

### 使用方式

```
/mufeng-dankoe-writing [话题]
```

**示例**：

```
/mufeng-dankoe-writing 为什么大多数人永远无法成为 10x 程序员
```

```
/mufeng-dankoe-writing 你以为的"努力"其实是一种逃避
```

```
/mufeng-dankoe-writing 关于独立开发者如何在 AI 时代找到自己的位置
```

### 调用后会询问的信息

| 信息 | 必填 | 说明 |
|------|------|------|
| 作者名字 | 是 | 文章署名 |
| 写作地点 | 否 | 增加真实感（如「上海·赵巷」）|
| 时间 | 否 | 格式：yymmdd hhmmss |
| 话题 | 是 | 要写作的具体话题（如已在命令中提供则跳过）|

### 文章结构

```
开篇（10%）
  └── 挑衅性陈述或反常识观点 + 阅读价值声明 + 核心观点数量预告

主体章节（80%）
  └── 一、[挑衅性标题]
      二、[挑衅性标题]
      三、[挑衅性标题]
      ...（5-7 个章节）
      每章节：名言引用（可选）→ 案例/类比 → 对比论证 → 反问句 → 短句强调

实践部分（可选）
  └── 第一、第二、第三……可执行协议（含问题清单/时间节点/行动步骤）

结尾（10%）
  └── 简短总结或鼓励 + 个人化签名（– 作者名字）
```

### 禁忌

- 空洞励志话语（「加油」「相信自己」）
- 过度承诺（「保证」「一定」「100%」）
- 过时营销话术
- 回避复杂性和矛盾（真实感来自承认不确定性）

---

## English Guide

### Description

A deep long-form writing style guide modeled after Dan Koe's writing. Designed for creating provocative, conversational content that requires serious thinking — thought-leader articles, systematic framework pieces, and counter-mainstream narratives. Target length: 1000-2000 words, worth saving and re-reading.

**Core style characteristics**:
- **Conversational provocation**: Uses "you" to address the reader directly; opens by challenging existing beliefs
- **Theory + practice**: First half dives into theory / psychology / philosophy; second half gives actionable steps
- **Counter-mainstream narrative**: Provides perspectives "you probably haven't heard"
- **Rhythm variation**: Long explanatory sentences + short punchy ones; key points get their own paragraph

### Installation & Activation

This skill is auto-discovered by Claude Code / Codex's Skill system. No separate installation is required.

**Activate in Claude Code**:

```
/mufeng-dankoe-writing [topic]
```

**Activate in Codex**:

```
Please use the mufeng-dankoe-writing style to write a long-form article about...
```

Also triggered automatically by keywords: `长篇文章` (long-form article), `深度写作` (deep writing), `Dan Koe 风格`, `挑衅性写作` (provocative writing), `思想领袖内容` (thought leader content), `系统化框架文章` (systematic framework article)

### Usage

```
/mufeng-dankoe-writing [topic]
```

**Examples**:

```
/mufeng-dankoe-writing Why most people will never become 10x developers
```

```
/mufeng-dankoe-writing The "hard work" you think you're doing is actually a form of avoidance
```

```
/mufeng-dankoe-writing How indie developers can find their place in the AI era
```

### Information Requested on Invocation

| Info | Required | Notes |
|------|----------|-------|
| Author name | Yes | Used for article attribution |
| Writing location | No | Adds authenticity (e.g., "Shanghai · Zhaoxiang") |
| Timestamp | No | Format: yymmdd hhmmss |
| Topic | Yes | The specific topic to write about (skipped if already in the command) |

### Article Structure

```
Opening (10%)
  └── Provocative statement or counter-intuitive point + value declaration + chapter count preview

Main chapters (80%)
  └── I. [Provocative title]
      II. [Provocative title]
      III. [Provocative title]
      ... (5-7 chapters)
      Each chapter: quote (optional) → case/analogy → contrast argument → rhetorical question → short punchy emphasis

Practice section (optional)
  └── First, Second, Third... actionable protocols (with question checklists / timelines / steps)

Closing (10%)
  └── Brief summary or encouragement + personal signature (– Author name)
```

### Prohibitions

- Empty inspirational phrases ("you can do it", "believe in yourself")
- Overpromising ("guaranteed", "definitely", "100%")
- Outdated marketing copy
- Ignoring complexity and contradictions (authenticity comes from acknowledging uncertainty)
