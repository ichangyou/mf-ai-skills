# 沐风 · App Builder（mufeng-app-builder）

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

把一个产品想法变成可交给 Agent 执行的项目：产品文档、MVP 范围、验收标准、`AGENTS.md` / `CLAUDE.md` / `DESIGN.md`、带依赖的任务清单和进度文件。默认只做规划，不写业务代码；明确要求后才进入自主开发循环。

## 调用

Codex：

```text
$mufeng-app-builder 做一款极简离线待办 iOS App，SwiftUI + SwiftData，后续加 iCloud 同步和 Pro 买断
```

Claude Code：

```text
/mufeng-app-builder 做一款极简离线待办 iOS App，SwiftUI + SwiftData，后续加 iCloud 同步和 Pro 买断
```

其他用法：

- 检查已有项目：`/mufeng-app-builder validate 当前项目`
- 进入开发：`/mufeng-app-builder build，从第一个可执行任务开始`

## 模式

| 模式 | 做什么 | 写业务代码 |
|---|---|---|
| discover | 梳理痛点、核心功能、MVP 边界 | 否 |
| bootstrap（默认） | 生成项目文档、Agent 规则、任务图，并校验 | 否 |
| validate | 检查已有项目的计划文档 | 否 |
| build | 按任务依赖逐个实现、验证、提交，失败有重试上限和阻塞记录 | 是 |

## 产出

```text
<project>/
├── AGENTS.md            # 共用工程规则（Codex 直接读取）
├── CLAUDE.md            # @AGENTS.md + Claude 专属说明
├── DESIGN.md
├── docs/  PRD.md  MVP_SCOPE.md  ARCHITECTURE.md  DATA_MODEL.md  ACCEPTANCE.md
└── tasks/ tasks.json  TASKS.md  PROGRESS.md  blockers/
```

已有同名文件时，先展示差异并等你确认，不会静默覆盖。

## 依赖与执行范围

- 规划与校验：Python 3.9+，只用标准库。
- build 模式：目标技术栈的真实工具链。iOS / macOS 需要 macOS + 完整 Xcode；Web 需要 Node 与包管理器；后端按 profile 需要 JDK、Docker 或 Python。
- 内置 profile：iOS/macOS SwiftUI、Vue 3 + TS、Spring Boot、Python FastAPI；其他技术栈按同样字段临时生成并标为未验证。

“支持”表示提供两端入口和执行说明。一晚上跑出 MVP 是目标，不是保证：会话中断、权限、构建环境都会让执行停下，进度靠 `tasks/PROGRESS.md` 恢复。实际执行规则见 [SKILL.md](SKILL.md)。

## 单独使用校验脚本

```bash
python3 scripts/check_plan.py <project-dir>
```

检查重复 ID、缺失或循环依赖、任务缺少验收或验证方式、P0 功能没有任务或没有出现在 `docs/ACCEPTANCE.md`。通过时输出任务的依赖顺序。语义是否一致（例如需求是否真的被验收项覆盖）仍需人工审查。

## 测试

```bash
python3 -m unittest discover -s tests -v
```
