# 项目文件模板

模板中的 `<...>` 按项目填写。示例以离线待办 iOS App（ZenTasks）为例，换栈时替换命令和术语，结构保持不变。

## 目录

```text
<project>/
├── AGENTS.md
├── CLAUDE.md
├── DESIGN.md
├── docs/
│   ├── PRD.md
│   ├── MVP_SCOPE.md
│   ├── ARCHITECTURE.md
│   ├── DATA_MODEL.md
│   └── ACCEPTANCE.md
└── tasks/
    ├── tasks.json
    ├── TASKS.md
    ├── PROGRESS.md
    └── blockers/          # build 模式按需创建
```

多端项目（如 Vue + Spring Boot）在 `frontend/`、`backend/` 下各放一个 `AGENTS.md` 写局部规则，根目录 `AGENTS.md` 只写公共规则；接口约定放 `docs/API_SPEC.md`。

## docs/PRD.md

```markdown
# <产品名> PRD

## 问题与用户
- 目标用户：<谁>
- 痛点：<现在怎么做，哪里难受>
- 核心价值：<一句话>

## 功能
| ID | 功能 | 优先级 | 平台 | 说明 |
|---|---|---|---|---|
| F001 | 新增任务 | P0 | ios | 标题必填 |
| F004 | AI 解析任务 | P1 | ios | 首版不做 |

## 商业模式与隐私
<免费/买断/订阅；数据存在哪里，是否联网>

## 假设（待确认）
- <未经用户确认的判断>
```

P0 的判断标准：缺了它，就无法验证本版的核心价值。核心卖点必须是 P0；不能因为难做就降成 P1。

## docs/MVP_SCOPE.md

```markdown
# MVP 范围

## 本版包含
F001, F002, F003

## 本版明确不做
- 登录、云同步（F005）：首版只验证离线记录
- AI 解析（F004）：P1

## 范围变更规则
变更先改 PRD、本文件和 tasks/tasks.json，再运行 check_plan.py，最后继续编码。
执行中的 Agent 不得自行增删 P0。
```

## docs/ACCEPTANCE.md

每个 P0 功能 ID 必须出现，check_plan.py 会检查。

```markdown
# 验收标准

## F001 新增任务
- [ ] 输入标题并保存后，列表出现该记录
- [ ] 空标题无法保存，并显示提示
- 验证方式：单元测试 + 模拟器手动路径

## F003 本地保存
- [ ] 新增记录后杀进程重开，记录仍在

## Task Done
任务的验收项全部通过，相关构建与测试实际运行成功，证据写入 PROGRESS.md。

## MVP Done
- 所有 P0 任务为 SUCCESS
- <构建命令> 成功
- 核心用户路径在模拟器/浏览器实际走通
- UI 符合 DESIGN.md
- 没有 MVP_SCOPE 之外的功能
```

## docs/ARCHITECTURE.md 与 docs/DATA_MODEL.md

ARCHITECTURE：模块列表、分层与依赖方向、关键决策及理由（如「SwiftData 而非 Core Data：最低 iOS 17」）、外部服务、可扩展点（如为 CloudKit 预留的约束）。

DATA_MODEL：每个实体的字段、类型、默认值、可空性、唯一约束，持久化方式，迁移策略。字段约束要与未来平台兼容（如 CloudKit 要求属性可选或有默认值）——没有核实的兼容性写成假设。

## DESIGN.md

颜色 token、字体层级、间距尺度、圆角、核心组件（按钮、列表行、输入框、空状态、错误提示）、动效原则、深色模式、无障碍要求。
DESIGN.md 不会被 Agent 自动加载，必须由 AGENTS.md 写明「UI 任务先读 DESIGN.md」。

## AGENTS.md

只写所有 Agent 共同遵守的工程规则，每条要能在代码审查中验证。

```markdown
# Project Agent Instructions

## 项目
<一句话>。产品范围见 docs/PRD.md 与 docs/MVP_SCOPE.md，不在本文件重复。

## 技术栈
<语言、框架、最低系统版本、包管理>

## 命令
- 构建：<真实命令，如 xcodebuild -scheme ZenTasks -destination 'platform=iOS Simulator,name=iPhone 16' build>
- 测试：<真实命令>
- Lint：<若有>

## 架构规则
- <可验证的边界，如：View 不包含业务逻辑；Repository 是唯一的持久化入口>

## UI
UI 相关任务先读 DESIGN.md，只使用其中定义的 token 和组件。

## 测试与完成标准
- Task Done / MVP Done 以 docs/ACCEPTANCE.md 为准
- 区分：已编写 / 编译通过 / 测试通过 / 实际运行 / 真机验证；未执行的写「未验证」
- 不得删除或弱化测试、断言、验收项来获得通过

## 任务执行
- 任务来源：tasks/tasks.json；进度：tasks/PROGRESS.md
- 依赖全部 SUCCESS 后才开始任务
- 每个任务验证通过后作为一个独立提交点；是否自动 git commit 服从用户的 Git 规则，未授权时只列出建议的提交点

## 安全
- 不提交密钥；涉及生产密钥、付费服务、破坏性数据操作、发布时等待人工确认
- 不覆盖用户未提交的改动
```

## CLAUDE.md

```markdown
# Claude Code Project Instructions

@AGENTS.md

AGENTS.md 是共用规则的唯一来源，本文件不重复、不放宽其中任何规则。

## 上下文加载
按任务读取：PRD 相关段落、改架构时读 docs/ARCHITECTURE.md、UI 任务读 DESIGN.md、持久化读 docs/DATA_MODEL.md、开始前读 tasks/PROGRESS.md。

## 工作方式
- 复杂改动（数据迁移、支付、跨模块重构）先用 Plan Mode 提出计划
- 上下文压缩或会话交接前，把当前任务、验证结果、阻塞、下一步写入 tasks/PROGRESS.md

## 收尾报告
Completed / Files / Verification（命令与真实结果）/ Remaining / Next
```

Claude Code 较新版本在没有 CLAUDE.md 时也会读取 AGENTS.md；两者同时存在时加载行为与版本有关，所以显式写 `@AGENTS.md`。Codex 读取 AGENTS.md，并支持子目录的 AGENTS.md。

## tasks/tasks.json

check_plan.py 读取此文件。字段为必填，除非标注可选。

```json
{
  "features": [
    {"id": "F001", "name": "新增任务", "priority": "P0"}
  ],
  "tasks": [
    {
      "id": "T001",
      "title": "定义 Task 数据模型",
      "feature_id": "F001",
      "priority": "P0",
      "status": "PENDING",
      "dependencies": [],
      "files": ["App/Models/TaskItem.swift"],
      "deliverables": ["SwiftData 模型 TaskItem"],
      "acceptance": ["模型字段与 DATA_MODEL.md 一致"],
      "verification": ["单元测试：创建并读取 TaskItem"],
      "complexity": "small"
    }
  ]
}
```

- 工程搭建、基线构建这类不属于用户功能的任务，挂到 `F000 工程基础`（P0），并在 ACCEPTANCE.md 写 F000 的验收（如基线构建成功）
- `status` 取值：PENDING / RUNNING / VERIFYING / RECOVERING / SUCCESS / BLOCKED / SKIPPED
- `files`、`deliverables`、`complexity` 为可选
- 一个任务应能在一个 Agent 会话内理解、修改并验证；需要同时改十几个模块就继续拆
- 拆分顺序：功能 → 交付物 → 架构层（模型 → 存储 → 状态/ViewModel → UI → 测试）→ 依赖 → 验收映射

## tasks/TASKS.md

按 check_plan.py 输出的 ORDER 排列，每个任务一节：ID、标题、功能、优先级、依赖、验收、验证方式。与 tasks.json 冲突时以 tasks.json 为准，并修正 TASKS.md。

## tasks/PROGRESS.md

```markdown
# Execution Progress

## 当前状态
<NOT_STARTED / RUNNING / RUNNING_WITH_BLOCKERS / STOPPED / MVP_DONE>

## 最后验证的检查点
commit: <hash>，验证：<命令与结果>

## 已完成
- T001：<证据>

## 阻塞
- T014：见 tasks/blockers/BLOCK-001.md

## 下一个可执行任务
- T016

## 关键决策
- <日期>：<决策与理由>
```
