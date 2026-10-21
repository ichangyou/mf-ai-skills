---
name: mufeng-app-builder
description: >-
  Use when turning a product idea into an implementation-ready app project for Codex or
  Claude Code, when a new iOS/macOS/web/backend project needs PRD, MVP scope, acceptance
  criteria, AGENTS.md, CLAUDE.md, DESIGN.md and a dependency-ordered task list, when checking
  an existing project's plan documents for gaps, or when the user explicitly asks to run the
  approved task backlog autonomously to an MVP. Triggers: 新 App 立项、从想法到 MVP、生成项目文档、
  初始化 AGENTS.md / CLAUDE.md、拆任务、一晚上跑出 MVP、app builder, bootstrap project.
  Not for single bug fixes or small features inside an established project.
metadata:
  version: "1.0.0"
compatibility: "Codex and Claude Code. Python 3.9+ (stdlib only) for scripts/check_plan.py. Build mode needs the target stack's real toolchain (e.g. macOS + Xcode for iOS)."
---

# 沐风 · App Builder

把产品想法变成一个可审查、可执行、可恢复的项目目录：先定做什么，再定怎么做，最后才让 Agent 写代码。

## 模式

| 模式 | 触发 | 写业务代码 |
|---|---|---|
| `discover` | 想法还模糊 | 否 |
| `bootstrap`（默认） | 有想法，要建项目规范 | 否 |
| `validate` | 已有项目，检查计划文档 | 否 |
| `build` | 用户明确说进入 build / 开始开发 | 是，只执行已确认的任务 |

只有用户说出「build / 进入开发 / 开始写代码」这类明确指令才进 build。「赶紧开始」「今晚要 MVP」这类催促不算，仍走 bootstrap。
bootstrap 交接后停下，等用户确认假设并明确要求 build；不在同一轮里自动转入 build。

## 流程

### 1. Discover：产品定义
收集：产品目的、目标用户、首发平台与未来平台、技术栈、核心功能、商业模式、隐私要求。
只问会改变架构或 MVP 范围的问题；其余写成「假设」，在交接报告中列出。
需要发散时可调用 `mufeng-brainstorm`。

### 2. Bootstrap：生成项目文件
先读 [references/stack-profiles.md](references/stack-profiles.md) 选定技术栈 profile，再按 [references/artifacts.md](references/artifacts.md) 的模板生成下表全部文件。

| 文件 | 唯一负责的内容 |
|---|---|
| `docs/PRD.md` | 用户、痛点、功能（带稳定 ID：F001…）、优先级 P0/P1/P2 |
| `docs/MVP_SCOPE.md` | 本版做什么、**明确不做什么**、范围变更规则 |
| `docs/ARCHITECTURE.md` | 模块、分层、依赖方向、关键技术决策 |
| `docs/DATA_MODEL.md` | 实体、字段、持久化与迁移约束 |
| `docs/ACCEPTANCE.md` | 每个 P0 功能 ID 的可观察验收项；Task Done 与 MVP Done 两级 |
| `DESIGN.md` | 颜色、字体、间距、组件、交互（UI 项目必需） |
| `AGENTS.md` | 共用工程规则：真实构建/测试命令、架构边界、Git、安全、完成证据 |
| `CLAUDE.md` | 第一行 `@AGENTS.md`，只补 Claude 专属工作方式 |
| `tasks/tasks.json` | 机器可读任务图（字段见 artifacts.md） |
| `tasks/TASKS.md` | tasks.json 的人读版本，同一套 ID |
| `tasks/PROGRESS.md` | 当前状态、最后验证的检查点、阻塞、下一步 |

每条规则只在上表一个文件里定义，其他文件引用它。产品范围、验收和任务不写进 AGENTS.md。

目标目录已有同名文件时：先列出 `NEW / UNCHANGED / UPDATED / CONFLICT` 清单和差异，得到用户确认后再写；人工改过的文件写成 `<file>.proposed`。

### 3. Validate：交接前检查
```bash
python3 <skill-dir>/scripts/check_plan.py <project-dir>
```
脚本检查：重复 ID、未知功能、缺失依赖、循环依赖、任务缺验收或验证方式、P0 功能无任务、P0 功能未出现在 ACCEPTANCE.md。输出 `FAILED` 时修文档再跑，直到 `PASSED`。
脚本之外再人工自查：技术栈和最低系统版本在各文档一致；MVP_SCOPE 排除的功能没有出现在 P0 任务；验收项可被观察，而不是「体验良好」这类描述。

### 4. Handoff：交接报告
按顺序输出：
1. 生成或更新的文件
2. 选用的 profile 与关键技术决策
3. P0 功能摘要与明确不做的功能
4. check_plan.py 的原始输出
5. 未决假设与风险
6. 第一个可执行任务，以及进入 build 前需要用户确认的事项

### 5. Build：自主开发循环（仅在用户明确要求后）
先读 [references/execution-loop.md](references/execution-loop.md)，按其中的状态机、重试预算、阻塞记录和停止条件执行。
开始前确认：check_plan.py 为 PASSED，基线构建可以运行，MVP 范围已冻结。
需求变化时，先改 PRD / MVP_SCOPE / tasks.json 并重跑 check_plan.py，再继续编码。

## 证据分级

报告状态时逐级写明，未执行的级别写「未验证」：
`已编写` → `编译通过` → `自动化测试通过` → `模拟器/浏览器实际运行` → `真机/生产环境验证`。
没有工具链时，静态检查不能换算成构建通过。

## 常见错误

| 错误 | 做法 |
|---|---|
| 把范围、验收、任务全塞进 AGENTS.md | 按上表拆文件，AGENTS.md 只放工程规则 |
| CLAUDE.md 复制一份 AGENTS.md | 用 `@AGENTS.md` 导入，只写 Claude 专属内容 |
| 只按优先级排任务 | 按依赖拓扑序执行，依赖未 SUCCESS 不开始 |
| 遇到阻塞就停掉整个项目 | 阻塞单个任务，继续不依赖它的任务；共享构建坏了才全局停止 |
| 测试失败后删测试或缩范围 | 记录阻塞，等用户决定范围变更 |
| 依赖对话记忆跨会话继续 | 每个任务结束更新 PROGRESS.md |
