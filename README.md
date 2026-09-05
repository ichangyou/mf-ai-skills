# mf-ai-skills

沐风（Joey）的 Claude Code / Codex 个人 AI Skill 集合，共 15 个。

---

## 项目简介

本项目收录了沐风日常在用的 Agent Skills，覆盖五类场景：内容写作与发布、周期复盘、结构化思考、iOS 工程质量、研究分析。全部按 Joey 的个人风格和工作流深度定制，不是通用模板的堆砌。

**GitHub**：`ichangyou/mf-ai-skills`

---

## Skills 列表

### 写作与发布

| Skill | 用途 | 平台 |
|-------|------|------|
| [`mufeng-blog-writing`](#mufeng-blog-writing) | mufeng.blog 技术博客写作（含 SEO 元数据） | Claude Code |
| [`mufeng-dankoe-writing`](#mufeng-dankoe-writing) | Dan Koe 风格深度长篇写作 | Claude Code / Codex |
| [`mufeng-wechat-publish-full`](#mufeng-wechat-publish-full) | 微信公众号端到端发布（生图 → 上传 → 发布） | Claude Code |
| [`mufeng-materials-to-wechat-publish`](#mufeng-materials-to-wechat-publish) | 目录素材转微信公众号图文并发布 | Codex |
| [`mufeng-bilingual-storybook`](#mufeng-bilingual-storybook) | 中英双语 AI 绘本生成（输出 PDF） | Codex |

### 复盘与笔记

| Skill | 用途 | 平台 |
|-------|------|------|
| [`mufeng-weekly-report`](#mufeng-weekly-report) | 从对话记录自动生成周报 | Claude Code |
| [`mufeng-monthly-report`](#mufeng-monthly-report) | 从对话记录自动生成月报 | Claude Code |
| [`mufeng-book-notes`](#mufeng-book-notes) | 基于素材生成可落地的读书笔记 | Claude Code |

### 思考与决策

| Skill | 用途 | 平台 |
|-------|------|------|
| [`mufeng-brainstorm`](#mufeng-brainstorm) | 结构化头脑风暴（发散 → 收敛 → 深挖 → 反驳） | Claude Code |
| [`mufeng-virtual-team`](#mufeng-virtual-team) | CTO / 产品经理 / 用户三角色功能评审 | Claude Code |
| [`mufeng-uxreview`](#mufeng-uxreview) | 资深 UI/UX 设计评审，只给方案不改代码 | Claude Code |

### iOS 工程

| Skill | 用途 | 平台 |
|-------|------|------|
| [`mufeng-ios-release-audit`](#mufeng-ios-release-audit) | App Store 上线前发布审计 + 上线文案 | Claude Code |
| [`mufeng-ios-visual-regression`](#mufeng-ios-visual-regression) | 多语言 / 深色模式截图视觉回归对比 | Claude Code |
| [`mufeng-parallel-root-cause`](#mufeng-parallel-root-cause) | 调查卡住时的并行证伪式根因排查 | Claude Code |

### 研究分析

| Skill | 用途 | 平台 |
|-------|------|------|
| [`mufeng-stock-research`](#mufeng-stock-research) | 股票研究报告（8 项分析，导出 PDF/HTML） | Claude Code |

---

## 安装方式

### 方式一：GitHub 远程安装（推荐）

在 `~/.claude/settings.json` 的 `extraKnownMarketplaces` 中添加以下配置：

```json
{
  "extraKnownMarketplaces": {
    "mf-ai-skills": {
      "source": {
        "source": "github",
        "repo": "ichangyou/mf-ai-skills"
      }
    }
  }
}
```

保存后，在 Claude Code 中运行 `/plugins` 命令，找到 `mf-ai-skills` 市场，启用需要的 Skills。

### 方式二：本地目录安装

先 clone 到本地：

```bash
git clone git@github.com:ichangyou/mf-ai-skills.git ~/path/to/mf-ai-skills
```

在 `~/.claude/settings.json` 中配置本地路径：

```json
{
  "extraKnownMarketplaces": {
    "mf-ai-skills": {
      "source": {
        "source": "directory",
        "path": "/Users/你的用户名/path/to/mf-ai-skills"
      }
    }
  }
}
```

### 验证安装

在 Claude Code 对话中输入任意 skill 名称（带斜杠前缀），如果可以激活则安装成功：

```
/mufeng-blog-writing
```

---

## 使用说明

### mufeng-blog-writing

mufeng.blog 技术博客写作助手。输出含可运行代码、SEO 元数据的 Markdown 文件，自动保存到当前目录。

```
/mufeng-blog-writing [话题描述]
```

**示例**：

```
/mufeng-blog-writing SwiftUI @State 和 @Binding 的区别
/mufeng-blog-writing Spring Boot 整合 Redis 缓存，包含完整代码
```

---

### mufeng-dankoe-writing

Dan Koe 风格深度长篇写作（1000-2000 字）。对话式挑衅开篇，前半理论后半实践，节奏张弛有度，适合思想领袖内容和反主流叙事。

```
/mufeng-dankoe-writing [话题]
```

**示例**：

```
/mufeng-dankoe-writing 为什么大多数人永远无法成为 10x 程序员
/mufeng-dankoe-writing 关于独立开发者如何在 AI 时代找到自己的位置
```

---

### mufeng-wechat-publish-full

微信公众号端到端发布工作流，共 6 个阶段：内容策略优化 → IP 白名单检查 → DashScope 生图 → GitHub 图床 → HTML 净化 → 微信 API 发布。任何阶段失败后可重新触发定向修复。

```
/mufeng-wechat-publish-full
[粘贴 Markdown 文章内容]
```

**修复失败步骤**：

```
/mufeng-wechat-publish-full
上次 Stage 3 GitHub 上传失败了，文章如下：[内容]
```

---

### mufeng-materials-to-wechat-publish

将目录素材自动转化为带插图的微信公众号图文并发布。全流程：素材读取 → 文章生成 → 图片生成 → GitHub 图床 → URL 插入 → 微信 API 发布。运行于 Codex 环境。

```
/mufeng-materials-to-wechat-publish
```

---

### mufeng-bilingual-storybook

基于 Markdown 素材生成中英双语 AI 绘本，输出中文版和英文版 PDF。运行于 Codex 环境，使用 Codex 内置图像生成，不需要外部图像 API。

```
/mufeng-bilingual-storybook
[提供故事 Markdown 文件或内容]
```

---

### mufeng-weekly-report

从当前及近期 session 对话记录自动提取信息，生成结构化周报（技术成长、学习、写作、健康、生活、想法六大类别），附亮点分析与改进建议。

```
/mufeng-weekly-report
```

无需参数，在周末复盘时触发即可。

---

### mufeng-monthly-report

月报版本，比周报更聚焦趋势和规律提炼，含七大类别、月度深度分析、下月行动建议和展望。

```
/mufeng-monthly-report
```

---

### mufeng-book-notes

基于提供的书籍摘录或内容，生成可落地、能指导行动的读书笔记（7 个固定章节结构），风格真实克制，不鸡汤。

```
/mufeng-book-notes
[粘贴书籍摘录或内容]
```

**示例**：

```
/mufeng-book-notes 书名：《纳瓦尔宝典》，帮我生成读书笔记
/mufeng-book-notes 书名：《深度工作》，以下是我摘录的几段话：[内容]
```

也支持关键词自动触发：`读书笔记`、`书评`、`帮我总结这本书`

---

### mufeng-brainstorm

结构化头脑风暴框架，自动识别四类场景（产品功能 / 技术选型 / 内容策略 / 项目规划）并执行对应流程：发散 → 收敛（价值/成本矩阵）→ 深挖 Top 3 → 子 Agent 反驳 Top 1。

```
/mufeng-brainstorm [问题描述]
```

**四类场景示例**：

```
# 产品功能
/mufeng-brainstorm 新功能：用户想要离线模式，有哪些实现方案

# 技术选型
/mufeng-brainstorm 我要做实时聊天，WebSocket 还是 SSE 还是 Long Polling

# 内容策略
/mufeng-brainstorm 这个月公众号选题太难了，帮我想 15 个 AI 相关的选题

# 项目规划
/mufeng-brainstorm 我想为独立开发者做一个 AI 助手 App，不知道从哪个功能入手
```

---

### mufeng-virtual-team

让 AI 依次扮演 CTO、产品经理、普通用户，对同一个功能做三视角评审，最后综合裁决。目的不是给答案，而是暴露一个人开发时看不到的盲区。全程只做分析和建议，不写实现代码。

```
/mufeng-virtual-team [功能描述]
```

**示例**：

```
/mufeng-virtual-team 我想给笔记 App 加一个 AI 自动打标签功能，值不值得做
```

评审前会先追问目标用户、现状、技术上下文、项目阶段，信息不全不会硬评。

---

### mufeng-uxreview

以资深产品设计师身份评审指定页面或界面。读真实组件代码（Tailwind / SwiftUI）后，按层级、间距、文案、可供性、设计系统违规五个维度分组汇报，按影响排序。只给方案，批准前不改代码。

```
/mufeng-uxreview [页面或组件路径]
```

**示例**：

```
/mufeng-uxreview src/pages/Settings.tsx
/mufeng-uxreview 看看 ShotZen 的相册选择页有什么问题
```

---

### mufeng-ios-release-audit

iOS App Store 上线前完整发布审计。逐项核验权限文案、托管 EULA/条款 URL 及违禁内容条款、硬编码价格、`.lproj` 本地化完整性、App 图标、版本号与 build 号、数据层强制解包、零编译警告、多语言商店元数据，并产出微信 / X / Reddit 上线文案。

清单的每一项都来自真实的拒审或事故，不是通用最佳实践的罗列。全程只读，发现问题先报告根因和修复方案。

```
/mufeng-ios-release-audit
```

仅适用于 iOS / App Store 项目。

---

### mufeng-ios-visual-regression

iOS 视觉回归测试（UIKit / SwiftUI 通用）。任何 UI 改动（布局、颜色、间距、字体、深色模式、本地化文案）之后，通过模拟器对每个顶层页面在所有支持语言和明暗外观下截图，与已提交的基线对比，产出框出差异区域的 HTML 报告。

本 skill 是共享引擎，每个项目自带 `VisualRegression/config.json` 和一个 DEBUG-only 的应用内 harness。

```bash
~/.claude/skills/mufeng-ios-visual-regression/run.sh init       # 初始化新项目
~/.claude/skills/mufeng-ios-visual-regression/run.sh check      # UI 改动后检查
~/.claude/skills/mufeng-ios-visual-regression/run.sh baseline   # 接受当前 UI 为基线
```

需要 macOS + Xcode 模拟器。

---

### mufeng-parallel-root-cause

并行证伪式根因调查。用于调查已经卡住的硬 bug：两条以上线索已经追死、故障横跨多层（应用代码 / 配置 / 第三方服务 / 系统 / 本地工具链）、或者症状和最显然的解释相互矛盾。

核心原则不是并行找证据支持猜想，而是并行地**杀死**猜想。每个子代理的任务是证伪自己的假设，活到最后的假设才配谈修复。

```
/mufeng-parallel-root-cause [问题描述]
```

不适用于第一次看这个 bug，或 stack trace 已直接指向某个文件的情况。

---

### mufeng-stock-research

股票研究与市场分析（仅用于教育和信息目的，不构成投资建议）。可独立通过网络搜索运行，接入 Financial Datasets MCP 后可获取实时结构化数据。执行 8 项分析：基本面、风险、DCF 估值、同业对比、催化剂、技术面、情绪面、研究总结，默认导出 PDF + HTML，也支持 Word。中英文均可。

```
/mufeng-stock-research [公司名或代码]
```

**示例**：

```
/mufeng-stock-research NVDA
/mufeng-stock-research 分析一下腾讯控股，用中文出报告
```

---

## 许可证

MIT © Chang You
