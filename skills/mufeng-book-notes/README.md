# mufeng-book-notes

> 沐风读书笔记生成器 / Book notes generator for Joey (沐风)

---

## 中文说明

### 功能描述

沐风专属读书笔记生成器。基于用户提供的书籍内容、摘录或原文片段，生成一篇高质量、可落地、能指导行动的读书笔记。

**核心原则**：笔记不是摘要，不是复述，而是「写给未来自己的理解记录」。风格真实克制，不鸡汤，不口号。核心筛选标准是——这个观点能不能改变我的判断和行动。

### 安装与激活

本 skill 通过 Claude Code 的 Skill 系统自动发现，无需单独安装。在 Claude Code 对话中输入以下命令激活：

```
/mufeng-book-notes
```

也支持以下关键词自动触发：`读书笔记`、`书评`、`读后感`、`帮我总结这本书`

### 使用方式

```
/mufeng-book-notes
[粘贴书籍内容、摘录或原文片段]
```

**示例**：

```
/mufeng-book-notes
[粘贴《原则》第 5 章的摘录内容]
```

```
/mufeng-book-notes 书名：《纳瓦尔宝典》，我读完了，帮我生成读书笔记
```

```
/mufeng-book-notes 书名：《深度工作》，以下是我摘录的几段话：[粘贴内容]
```

### 输出结构

| 章节 | 内容 |
|------|------|
| 一、这本书真正想解决什么问题 | 底层问题 + 当下关联 + 带走的核心判断 |
| 二、核心概念（3-6个） | 解释 + 适用场景 + 用法 + 实践步骤 |
| 三、对我真正有用的 3-5 个点 | Insight + 个人理解 + 场景应用 |
| 四、经验、反直觉点和被忽略的细节 | 可包含批判性判断 |
| 五、可执行清单 | 一周行动 + 小实验 + 长期习惯 |
| 六、我应该避免什么 | 具体行为模式警示 |
| 七、一句话总结 | 写给未来自己的提醒 |

落款：系统时间（自动获取）+ 地点 + AI 辅助声明

### 注意事项

- 如提供内容不足以支撑某章节，自动跳过，不强行填充
- 落款时间通过 `date "+%Y.%m.%d %H:%M"` 自动获取系统时间
- 输出语言：中文
- 适用场景：开发工作、独立开发、写作、个人成长（以 Joey 的背景为参照系）

---

## English Guide

### Description

Joey's personal book notes generator. Given book content, excerpts, or raw text provided by the user, it produces high-quality, actionable book notes.

**Core principle**: These notes are not a summary or retelling — they are a "record of understanding written for your future self." Style is honest and restrained: no empty inspiration, no slogans. The core filter is whether a point can change your judgment or actions.

### Installation & Activation

This skill is auto-discovered by Claude Code's Skill system. No separate installation is required. Activate in Claude Code chat:

```
/mufeng-book-notes
```

Also triggered automatically by keywords: `读书笔记`, `书评`, `读后感`, `帮我总结这本书`

### Usage

```
/mufeng-book-notes
[Paste book content, excerpts, or raw text]
```

**Examples**:

```
/mufeng-book-notes
[Paste excerpts from Chapter 5 of "Principles"]
```

```
/mufeng-book-notes Book: "The Almanack of Naval Ravikant" — I've finished it, generate my notes
```

```
/mufeng-book-notes Book: "Deep Work" — here are some passages I highlighted: [paste content]
```

### Output Structure

| Section | Content |
|---------|---------|
| 1. What problem this book really solves | Core issue + relevance now + the one takeaway judgment |
| 2. Key concepts (3-6) | Explanation + use cases + how-to + action steps |
| 3. 3-5 points genuinely useful to me | Insight + personal interpretation + scenario application |
| 4. Counter-intuitive points and overlooked details | May include critical judgment |
| 5. Action checklist | Weekly actions + a small experiment + a long-term habit |
| 6. What I should avoid | Specific behavioral pattern warnings |
| 7. One-sentence summary | A note written to your future self |

Footer: system timestamp (auto-fetched) + location + AI-assist declaration

### Notes

- If provided content is insufficient for a section, that section is skipped rather than padded
- Footer timestamp is auto-fetched via `date "+%Y.%m.%d %H:%M"`
- Output language: Chinese
- Reference context: Joey's background in iOS/Java development, indie apps, writing, and personal growth
