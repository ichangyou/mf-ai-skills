# mufeng-monthly-report

> 沐风月报生成器 / Monthly report generator for Joey (沐风)

---

## 中文说明

### 功能描述

根据过去一个月的对话记录自动生成结构化月报。比周报更注重**趋势和规律的提炼**，含七大类别记录、月度深度分析（规律与趋势）、下月行动建议和展望。

### 安装与激活

本 skill 通过 Claude Code 的 Skill 系统自动发现，无需单独安装。在 Claude Code 对话中输入以下命令激活：

```
/mufeng-monthly-report
```

### 使用方式

无需额外参数。skill 自动确定当月周期（1 日到最后一天）并分析对话记录：

```
/mufeng-monthly-report
```

**触发时机**：
- 月末复盘时
- 需要生成月度总结
- 需要跨越整月的趋势分析

### 与周报的区别

| 维度 | 周报 | 月报 |
|------|------|------|
| 关注点 | 单周事件记录 | 月度趋势与规律 |
| 分析深度 | 亮点 + 不足 + 建议 | 额外增加「规律与趋势」模块 |
| 目标追踪 | 无 | 有（月初目标的完成情况） |
| 字数 | 500-800 字 | 800-1200 字 |
| 认知记录 | 无 | 有「本月最重要的认知升级」 |

### 信息提取类别

| 类别 | 月报关注点 |
|------|-----------|
| 技术成长 | 掌握了哪些新技能、完成了哪些项目 |
| 学习 | 读完了哪些书、学了哪些系统性知识 |
| 写作 | 发布了多少篇内容、哪篇反响最好 |
| 身体健康 | 运动频率和规律性如何 |
| 生活探索 | 有哪些值得记录的新体验 |
| 目标追踪 | 月初设定的目标完成情况如何 |
| 想法/反思 | 本月最重要的认知升级是什么 |

### 输出格式

```
📅 2026年XX月 - Claude月报（MM.01 - MM.DD）

🏆 本月最重要的 3 件事：
1. [动词开头，简洁有力]
2. [动词开头，简洁有力]
3. [动词开头，简洁有力]

📌 技术成长
📚 学习
📝 写作
🧘 身体健康
☕ 生活探索
🎯 目标追踪
🧠 本月最重要的认知升级：

---
✨ 本月做得好的地方（3-5条）
⚠️ 本月做得不好的地方（2-4条）
📊 本月规律与趋势（2-3条行为规律分析）
💡 下月行动建议（3条，含执行频率/数量/截止时间）
🔭 下月展望（50字以内）
```

### 输出规则

- 内容用**中文**输出
- 月报正文总字数控制在 800-1200 字（不含分析部分）
- 分析部分聚焦规律而非孤立事件，比周报更深入
- 亮点/不足/建议必须基于对话事实，不虚构
- 改进建议必须是下月可立刻执行的具体动作，含执行标准

---

## English Guide

### Description

Automatically generates a structured monthly summary from the past month's conversations. More focused on **trend and pattern extraction** than the weekly report. Includes seven topic categories, in-depth monthly analysis (patterns and trends), next-month action recommendations, and an outlook.

### Installation & Activation

This skill is auto-discovered by Claude Code's Skill system. No separate installation is required. Activate in Claude Code chat:

```
/mufeng-monthly-report
```

### Usage

No parameters needed. The skill auto-determines the current month's date range (1st through last day) and analyzes conversation history:

```
/mufeng-monthly-report
```

**When to trigger**:
- End-of-month retrospective
- Generating a monthly summary
- Analyzing trends spanning a full month

### Difference from Weekly Report

| Dimension | Weekly | Monthly |
|-----------|--------|---------|
| Focus | Single-week event logging | Monthly trends and behavioral patterns |
| Analysis depth | Highlights + weaknesses + suggestions | Adds "Patterns & Trends" module |
| Goal tracking | None | Yes — tracks goals set at month start |
| Word count | 500-800 ch | 800-1200 ch |
| Mindset record | None | Yes — "Most important mindset shift this month" |

### Output Format

```
📅 Month XX of 2026 - Claude Monthly Report (MM.01 - MM.DD)

🏆 Top 3 most important things this month:
1. [verb-led, concise]
2. [verb-led, concise]
3. [verb-led, concise]

📌 Technical growth
📚 Learning
📝 Writing
🧘 Physical health
☕ Life exploration
🎯 Goal tracking
🧠 Most important mindset shift this month:

---
✨ What went well this month (3-5 items)
⚠️ What didn't go well (2-4 items)
📊 Patterns and trends this month (2-3 behavioral pattern analyses)
💡 Next month's action recommendations (3 items, with frequency/quantity/deadline criteria)
🔭 Next month outlook (under 50 characters)
```

### Output Rules

- Content in **Chinese**
- Main report capped at 800-1200 characters (excluding the analysis section)
- Analysis focuses on patterns rather than isolated events — deeper than the weekly report
- Highlights / weaknesses / suggestions must be grounded in actual conversation content, no fabrication
- Improvement recommendations must be immediately actionable next month, with specific execution criteria
