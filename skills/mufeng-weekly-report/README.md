# mufeng-weekly-report

> 沐风周报生成器 / Weekly report generator for Joey (沐风)

---

## 中文说明

### 功能描述

根据本周的对话记录自动生成结构化周报，包含六大类别记录和亮点分析与改进建议。周期为自然周（周一至周日），格式统一，风格真实坦诚。

### 安装与激活

本 skill 通过 Claude Code 的 Skill 系统自动发现，无需单独安装。在 Claude Code 对话中输入以下命令激活：

```
/mufeng-weekly-report
```

### 使用方式

无需额外参数。skill 自动从当前及近期 session 的对话内容中提取信息：

```
/mufeng-weekly-report
```

**触发时机**：
- 周末复盘时
- 想要回顾本周工作内容
- 需要生成格式化周报

### 信息提取类别

| 类别 | 识别关键词/信号 |
|------|--------------|
| 技术成长 | 写代码、debug、架构、工具、技术方案 |
| 学习 | 读书、看文章、学新知识、研究 |
| 写作 | 写文章、公众号、博客、周报 |
| 身体健康 | 运动、锻炼、睡眠、饮食 |
| 生活探索 | 新体验、餐厅、旅行、兴趣爱好 |
| 想法/反思 | 总结、思考、复盘、计划 |

若某类别无内容，保留标题并标注「本周暂无记录」，不删除该类别。

### 输出格式

```
📅 2026年第XX周 - Claude周报（MM.DD - MM.DD）

✅ 本周最关键任务：
[1-3件，动词开头，简洁有力]

📌 技术成长
[具体内容 或 本周暂无记录]

📚 学习
[具体内容 或 本周暂无记录]

📝 写作
[具体内容 或 本周暂无记录]

🧘 身体健康
[具体内容 或 本周暂无记录]

☕ 生活探索
[具体内容 或 本周暂无记录]

🧠 想法/反思：
[1-3 条本周最值得记录的思考或感悟]

---
✨ 本周做得好的地方（2-4条，具体说明为什么值得肯定）
⚠️ 本周做得不好的地方（2-3条，诚实直接）
💡 改进建议（每条不足对应 1 条下周可立刻执行的动作）
```

### 输出规则

- 内容用**中文**输出
- 总字数控制在 500-800 字（不含分析部分）
- 亮点/不足/建议必须基于对话事实，不虚构
- 周期计算：使用当天日期确认本周一到周日的范围

---

## English Guide

### Description

Automatically generates a structured weekly summary from the current week's conversation history. Covers six topic categories plus highlights analysis and improvement suggestions. Covers the natural week (Monday to Sunday) with a consistent format and honest tone.

### Installation & Activation

This skill is auto-discovered by Claude Code's Skill system. No separate installation is required. Activate in Claude Code chat:

```
/mufeng-weekly-report
```

### Usage

No parameters needed. The skill auto-extracts information from the current and recent conversation sessions:

```
/mufeng-weekly-report
```

**When to trigger**:
- End-of-week review
- Reviewing what was accomplished this week
- Generating a formatted weekly report

### Information Categories

| Category | Recognition keywords/signals |
|----------|------------------------------|
| Technical growth | coding, debugging, architecture, tools, technical decisions |
| Learning | books, articles, new knowledge, research |
| Writing | articles, WeChat posts, blog, weekly report |
| Physical health | exercise, sleep, diet |
| Life exploration | new experiences, restaurants, travel, hobbies |
| Thoughts / Reflections | retrospective, thinking, planning |

If a category has no content, keep the heading and note "No records this week" — never delete the category.

### Output Format

```
📅 Week XX of 2026 - Claude Weekly Report (MM.DD - MM.DD)

✅ Most critical tasks this week:
[1-3 items, start with a verb, concise]

📌 Technical growth
[content or "No records this week"]

📚 Learning
[content or "No records this week"]

📝 Writing
[content or "No records this week"]

🧘 Physical health
[content or "No records this week"]

☕ Life exploration
[content or "No records this week"]

🧠 Thoughts / Reflections:
[1-3 most noteworthy thoughts from the week]

---
✨ What went well this week (2-4 items, explain why each is notable)
⚠️ What didn't go well (2-3 items, honest and direct)
💡 Improvement suggestions (1 immediately actionable suggestion per weakness)
```

### Output Rules

- Content in **Chinese**
- Total word count capped at 500-800 characters (excluding the analysis section)
- Highlights / weaknesses / suggestions must be grounded in actual conversation content, no fabrication
- Week range calculated from today's date (Monday through Sunday)
