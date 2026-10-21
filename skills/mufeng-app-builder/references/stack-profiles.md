# 技术栈 Profile

一个 skill 加多个 profile，不为每种技术栈单独做 skill。下表是起点，生成 AGENTS.md 前要在目标机器上确认命令真实可用（如 `xcodebuild -list`、`pnpm -v`）；无法确认时，在 AGENTS.md 标注「待验证」。

## iOS / macOS · SwiftUI

| 项 | 默认 |
|---|---|
| 语言 / UI | Swift / SwiftUI |
| 持久化 | SwiftData（需 iOS 17 / macOS 14+）；更低版本用 Core Data |
| 并发 | Swift Concurrency，遵守 actor 隔离 |
| 架构 | 小型 App 用 View + @Observable 模型；逻辑多时 MVVM；协议注入便于测试 |
| 目录 | `App/` `Features/` `Core/` `Services/` `Resources/` `Tests/` |
| 测试 | Swift Testing 或 XCTest |
| 构建 | `xcodebuild -scheme <S> -destination 'platform=iOS Simulator,name=<设备>' build` |
| 测试命令 | `xcodebuild ... test` |
| 运行验证 | 模拟器走核心路径并截图；IAP、推送、后台任务等需真机 |
| 工程创建 | Xcode 模板（需人工）或 XcodeGen `project.yml`（需安装 xcodegen） |
| 规则 | 业务逻辑不进 View；避免强制解包；优先系统框架；StoreKit 2 用本地 .storekit 配置测试 |

需要 macOS + 完整 Xcode。只有 `/usr/bin/xcodebuild` 入口、没有 Xcode.app 时无法构建，构建状态记为「未验证」。
macOS 作为后续平台时，在 PRD 的功能表用 `平台` 列区分，不重写整份 PRD。

## Web · Vue 3 + TypeScript

| 项 | 默认 |
|---|---|
| 构建 / 状态 / 路由 | Vite / Pinia / Vue Router |
| 目录 | `src/app` `src/features` `src/components` `src/composables` `src/services` `src/types` `tests/` |
| 验证 | `pnpm typecheck`、`pnpm test`（Vitest）、`pnpm build`、Playwright 冒烟 |
| 规则 | Composition API + `<script setup>`；strict TS，禁止隐式 any；API 调用与 UI 分离 |

React / Next.js 结构相同，替换框架术语和命令。

## Backend · Spring Boot

| 项 | 默认 |
|---|---|
| 持久化 / 迁移 | Spring Data JPA / Flyway |
| 架构 | 模块化单体 |
| 验证 | `./mvnw test`（JUnit 5）、集成测试（Testcontainers，需要 Docker）、`./mvnw package` |
| 规则 | 构造器注入；Controller 薄；明确事务边界；不直接暴露 JPA 实体；校验入参 |

## Backend · Python FastAPI

| 项 | 默认 |
|---|---|
| 环境 | uv 或 venv，`pyproject.toml` |
| 持久化 / 迁移 | SQLAlchemy 2 / Alembic |
| 验证 | `pytest`、`ruff check`、`mypy`（若启用） |
| 规则 | Pydantic 模型做入参校验；路由层不写业务逻辑；配置走环境变量 |

## 组合

多个 profile 同时使用时（如 Vue + Spring Boot + MySQL）：

- 在 ARCHITECTURE.md 写一段 integration：通信方式（REST / OpenAPI）、数据库、认证方案（未定则写「待定」）。
- 接口契约放 `docs/API_SPEC.md`，前后端任务都依赖其中的接口定义任务。
- 两个 profile 对同一项给出不同值（如 Node 版本、端口）时列出冲突让用户选，不让后加载的 profile 静默覆盖。
- 根 AGENTS.md 写公共规则，`frontend/AGENTS.md`、`backend/AGENTS.md` 写各自的命令和规则。

## 没有匹配的 profile

按上述字段（语言、框架、目录、测试、构建、运行验证、规则）为新栈临时写一段，放进 ARCHITECTURE.md，并在交接报告中标为「未经验证的 profile」。
