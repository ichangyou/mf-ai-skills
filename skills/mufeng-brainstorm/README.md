# mufeng-brainstorm

> 结构化头脑风暴框架 / Structured brainstorming framework

---

## 中文说明

### 功能描述

适用于项目初期探索阶段的结构化头脑风暴框架。流程遵循：先发散（越多越奇越好）→ 再收敛（价值/成本矩阵）→ 深挖 Top 3 → 子 Agent 反驳 Top 1，系统性避免确认偏差。

支持四类场景，自动识别：

| 场景 | 适用关键词 |
|------|-----------|
| Phase A：产品功能 | 新功能、用户需求、产品设计 |
| Phase B：技术选型 | 架构、框架、迁移、性能 |
| Phase C：内容策略 | 文章、选题、公众号、传播 |
| Phase D：项目规划 | 新项目、方向、市场、调研 |

### 安装与激活

本 skill 通过 Claude Code 的 Skill 系统自动发现，无需单独安装。在 Claude Code 对话中输入以下命令激活：

```
/mufeng-brainstorm [问题描述]
```

如需直接进入特定场景，可使用子 skill：

- `/mufeng-brainstorm-feature` — 产品功能头脑风暴
- `/mufeng-brainstorm-tech-stack` — 技术选型分析
- `/mufeng-brainstorm-content` — 内容策略头脑风暴

### 使用方式

```
/mufeng-brainstorm [问题描述]
```

**通用调用**（自动识别场景）：

```
/mufeng-brainstorm 我想为独立开发者做一个 AI 助手 App，不知道从哪个功能入手
```

**功能设计类**：

```
/mufeng-brainstorm 新功能：用户想要离线模式，有哪些实现方案
```

**技术选型类**：

```
/mufeng-brainstorm 我要做实时聊天，WebSocket 还是 SSE 还是 Long Polling？
```

**内容策略类**：

```
/mufeng-brainstorm 这个月公众号选题太难了，帮我想 15 个 AI 相关的选题
```

### 各场景流程

**Phase A（产品功能）**

1. 发散：列出 20 个方向（常规 5 + 竞品 5 + 反常识 5 + 理想态 5）
2. 收敛：4 象限矩阵（高/低价值 × 高/低成本）
3. 深挖：Top 3 分析（核心假设 + 最大风险 + 2 周 MVP）
4. 反驳：子 Agent 给出 Top 1 最有力的 3 个反对理由 + 应对策略

**Phase B（技术选型）**

1. 摸底：明确约束（团队、并发、时间、维护预期）
2. 候选：列出 5-8 个方案（技术栈 + 适合场景 + 成功案例）
3. 对比：表格对比（效率/性能/学习曲线/生态/维护成本/兼容性）
4. 推荐：首选 + 备选 + 切换信号 + 1 年后重新评估条件
5. 风险：最容易踩的 3 个坑 + 规避方式

**Phase C（内容策略）**

1. 受众：定义 3 类读者（核心/潜在/意外）
2. 发散：15 个选题方向（硬核干货 5 + 共鸣情感 5 + 热点借势 5）
3. 筛选：Top 3 按身份匹配度/差异化/传播潜力评分
4. 框架：Top 1 的 3 个标题变体 + 摘要 + 钩子 → 核心 → 行动号召
5. 发布：平台建议 + 最佳时机 + 配套素材

**Phase D（项目规划）**

1. 背景：目标用户 + 痛点 + 现有方案缺陷 + 己方优势
2. 发散：4 视角各 3-5 个方向（用户/竞争/技术/商业）
3. 对比：每条路径评估（时间/资源/成功标志）
4. 聚焦：推荐 1 个方向 + 4 周验证计划
5. 死亡预演：6 个月后失败的 3 个最可能死因 + 提前规避

### 输出格式

每次头脑风暴结束后附决策摘要：

```markdown
## 决策摘要
- 推荐方向：[Top 1]
- 核心理由：[一句话]
- 最大风险：[一句话]
- 下一步行动：[具体可执行的第一步，最晚本周内可以开始]
```

### 适用场景 vs 不适用场景

**适用**：项目初期、功能多方向、技术选型未决、内容选题困难、任何"我们可以怎么做"的问题

**不适用**：已有明确方向只需执行的任务（直接执行效率更高）

---

## English Guide

### Description

A structured brainstorming framework for early-stage exploration. The process: Diverge (more and wilder is better) → Converge (value/cost matrix) → Deep-dive Top 3 → Sub-agent Devil's Advocate on Top 1. Systematically prevents confirmation bias.

Supports four scenario types, auto-detected:

| Scenario | Keywords |
|----------|----------|
| Phase A: Product features | new feature, user needs, product design |
| Phase B: Tech stack | architecture, framework, migration, performance |
| Phase C: Content strategy | article, topic, WeChat, reach |
| Phase D: Project planning | new project, direction, market, research |

### Installation & Activation

This skill is auto-discovered by Claude Code's Skill system. No separate installation is required. Activate in Claude Code chat:

```
/mufeng-brainstorm [problem description]
```

To jump directly into a specific scenario, use a sub-skill:

- `/mufeng-brainstorm-feature` — product feature brainstorm
- `/mufeng-brainstorm-tech-stack` — tech stack analysis
- `/mufeng-brainstorm-content` — content strategy brainstorm

### Usage

```
/mufeng-brainstorm [problem description]
```

**General invocation** (auto-detects scenario):

```
/mufeng-brainstorm I want to build an AI assistant app for indie developers — not sure which feature to start with
```

**Feature design**:

```
/mufeng-brainstorm New feature: users want offline mode — what are the implementation options?
```

**Tech stack**:

```
/mufeng-brainstorm I need real-time chat — WebSocket vs SSE vs Long Polling?
```

**Content strategy**:

```
/mufeng-brainstorm I'm stuck on topics this month — help me brainstorm 15 AI article ideas
```

### Output Format

A decision summary is appended after each brainstorm:

```markdown
## Decision Summary
- Recommended direction: [Top 1]
- Core reason: [one sentence]
- Biggest risk: [one sentence]
- Next action: [specific first step, executable within this week]
```

### When to Use vs When to Skip

**Use**: Early in a project, multiple possible directions, undecided tech stack, stuck on content topics, any "what could we do?" question

**Skip**: When you already have a clear direction and just need to execute — brainstorming adds unnecessary overhead
