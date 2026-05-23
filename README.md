# mf-ai-skills

沐风（Joey）的 Claude Code 个人 AI Skill 集合。

---

## 项目简介

本项目收录了沐风日常使用的 Claude Code Skills，覆盖微信公众号写作、技术博客、周报月报、读书笔记、头脑风暴等场景，均按 Joey 的个人风格和工作流深度定制。

**GitHub**：`ichangyou/mf-ai-skills`

---

## Skills 列表

| Skill | 用途 | 平台 |
|-------|------|------|
| [`mufeng-writing`](#mufeng-writing) | 微信公众号文章生成（含算法优化） | Claude Code |
| [`mufeng-blog-writing`](#mufeng-blog-writing) | mufeng.blog 技术博客写作 | Claude Code |
| [`mufeng-wechat-publish-full`](#mufeng-wechat-publish-full) | 微信公众号端到端发布（生图→上传→发布） | Claude Code |
| [`mufeng-weekly-report`](#mufeng-weekly-report) | 从对话记录自动生成周报 | Claude Code |
| [`mufeng-monthly-report`](#mufeng-monthly-report) | 从对话记录自动生成月报 | Claude Code |
| [`mufeng-book-notes`](#mufeng-book-notes) | 基于素材生成可落地的读书笔记 | Claude Code |
| [`mufeng-brainstorm`](#mufeng-brainstorm) | 结构化头脑风暴（四类场景自动识别） | Claude Code |
| [`mufeng-dankoe-writing`](#mufeng-dankoe-writing) | Dan Koe 风格深度长篇写作 | Claude Code / Codex |
| [`mufeng-bilingual-storybook`](#mufeng-bilingual-storybook) | 中英双语 AI 绘本生成（输出 PDF） | Codex |
| [`mufeng-codex-illustrated-wechat-publish`](#mufeng-codex-illustrated-wechat-publish) | Codex 图文微信发布（带插图） | Codex |

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
/mufeng-writing
```

---

## 使用说明

### mufeng-writing

微信公众号文章生成器。针对微信推荐算法（完读率、分享率、收藏率）优化标题和结构，保持作者真实风格。

```
/mufeng-writing [主题] / [类型] / [关键信息] / [篇幅]
```

**示例**：

```
/mufeng-writing Claude Code 实测 / C / 用了3个月的真实体验，10个高频场景 / 长文
```

```
/mufeng-writing
```
（无参数时，skill 会逐步询问）

**文章类型**：`C` AI技术 / `B` 个人成长 / `A` 读书笔记 / `D` 传统文化 / `E` 理财

---

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

基于提供的书籍摘录或内容，生成可落地、能指导行动的读书笔记（7个固定章节结构），风格真实克制，不鸡汤。

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

结构化头脑风暴框架，自动识别四类场景并执行对应流程：发散 → 收敛 → 深挖 Top 3 → 反驳 Top 1。

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

**直接进入特定场景**：

```
/mufeng-brainstorm-feature      # 产品功能
/mufeng-brainstorm-tech-stack   # 技术选型
/mufeng-brainstorm-content      # 内容策略
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

### mufeng-bilingual-storybook

基于 Markdown 素材生成中英双语 AI 绘本，输出中文版和英文版 PDF。运行于 Codex 环境，使用 Codex 内置图像生成，不需要外部图像 API。

```
/mufeng-bilingual-storybook
[提供故事 Markdown 文件或内容]
```

---

### mufeng-codex-illustrated-wechat-publish

将目录素材自动转化为带插图的微信公众号图文并发布。全流程：素材读取 → 文章生成 → 图片生成 → GitHub 图床 → URL 插入 → 微信 API 发布。运行于 Codex 环境。

```
/mufeng-codex-illustrated-wechat-publish
```

---

## 许可证

MIT © Chang You
