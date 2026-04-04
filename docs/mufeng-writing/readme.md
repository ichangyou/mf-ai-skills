# 沐风写作 Skill

基于沐风 7 篇博客文章提炼的 AI 写作指令集，覆盖**读书笔记、个人成长、技术工具、理财投资、书法艺术**五大主题，适配 Claude Code、Cursor、VS Code、Obsidian、Notion 五个平台。

---

## 文件结构

```
mufeng-writing skill/
│
├── readme.md                        ← 本文件
├── cursor-settings-rules.txt        ← Cursor 全局设置粘贴版
├── vscode-settings-snippet.jsonc    ← VS Code settings.json 配置片段
├── .clinerules                      ← VS Code Cline 项目级规则（自动加载）
│
├── .claude/
│   └── commands/
│       └── mufeng-writing-skill.md  ← Claude Code Skill（完整版）
│
├── .cursor/
│   └── rules/
│       └── mufeng-writing-skill.mdc ← Cursor 项目规则（编辑 .md 自动加载）
│
├── .github/
│   └── copilot-instructions.md      ← VS Code Copilot 项目级指令（自动加载）
│
├── Templates/                       ← Obsidian 模板目录
│   ├── 沐风博客模板.md               ← 新建文章脚手架（Templater）
│   ├── 沐风AI写作提示词.md           ← AI 插件系统提示词 + 快捷指令
│   └── 沐风写作检查清单.md           ← 发布前逐项检查
│
└── Notion/                          ← Notion 导入文件目录
    ├── 沐风写作风格指南.md            ← 常驻参考页（完整风格说明）
    ├── 沐风博客文章模板.md            ← 数据库模板（含元信息 + 检查清单）
    └── Notion-AI-自定义指令.md       ← Notion AI 两栏配置 + 快捷指令
```

---

## 写作风格摘要

### 核心原则

- **真实体验先行**：所有内容从个人亲历出发，不空泛说教
- **知行合一**：每篇结尾必须有可落地的行动建议
- **雅俗共赏**：古今典故与现代口语自然融合

### 语言风格

| 维度 | 规则 |
|---|---|
| 句式 | 短句打节奏 + 长句作解释，善用排比和反问 |
| 口语词 | 丝滑到离谱、强到不像话、我傻了、天啊！ |
| 书面雅词 | 见字如晤、张弛有度、知行合一 |
| 英文 | 专有名词保持英文（Claude Code、MCP、index fund） |
| 情感 | 科技类热情紧迫 / 读书类沉静深思 / 成长类温暖鼓励 / 文化类诗意浪漫 |

### 文章结构

```
开篇（钩子，三选一）
  ├── 个人故事式：讲发现这件事的具体场景（时间+地点+心情）
  ├── 反直觉式：先抛出颠覆常识的结论
  └── 悬念式：提出读者心里有但说不清的问题

主体（三层递进）
  ├── 第一层：背景 / 是什么（1-2 段）
  ├── 第二层：核心内容（### 分段，配引用/数据/故事）
  └── 第三层：个人视角 / 为什么重要

结尾（三选一）
  ├── 行动号召："赶紧去做 XXX，从今天起…"
  ├── 哲思留白：一句意味深长的话
  └── 自我剖白：分享自己接下来的计划

页脚（每篇必须有）
  └── YYYY.MM.DD HH:MM / 城市 · 地点
```

### 五类文章模板

| 类型 | 结构要点 |
|---|---|
| A 读书笔记 | 遇见这本书 → 作者背景（≤200字）→ 3-5 核心观点（含原文引用）→ 与自身连接 → 行动 |
| B 个人成长 | 踩过的坑 → 转折点 → 方法论（步骤化）→ 坚持感悟 → 鼓励行动 |
| C 技术工具 | "发现神器"开篇 → 痛点 → 使用步骤 → 3 个最佳场景 → 局限性 → 推荐 |
| D 传统文化 | 诗文 / 历史故事开篇 → 人物生平 → 当代意义 → 个人连接 → 诗意收尾 |
| E 理财投资 | 数据开篇（具体数字）→ 核心策略 → 误区破解 → 操作步骤 → 长期主义收尾 |

### 禁止事项

❌ "首先、其次、最后" ｜ ❌ "总的来说" / "综上所述" ｜ ❌ 被动语态 ｜ ❌ 无个人视角的信息堆砌 ｜ ❌ "希望本文对你有帮助"

---

## Claude Code

**文件：** `.claude/commands/mufeng-writing-skill.md`

在此项目目录下运行 Claude Code，输入 `/mufeng-writing-skill` 调用。告诉 Claude 主题、类型（A-E）和关键信息，即可输出完整文章。

---

## Cursor

**项目级规则（推荐）**

`.cursor/rules/mufeng-writing-skill.mdc` 会在编辑 `.md` 文件时自动加载，无需手动触发，支持 Cursor 0.43+。

**全局设置**

`Settings → General → Rules for AI`，将 `cursor-settings-rules.txt` 内容粘贴进去，对所有项目生效。

| | `.mdc` 项目规则 | Settings 文本 |
|---|---|---|
| 生效范围 | 仅当前项目 | 所有项目 |
| 触发方式 | 打开 `.md` 文件自动加载 | 每次对话都生效 |
| 详细程度 | 完整版（含示例） | 精简版（节省 token） |

---

## VS Code

**GitHub Copilot（项目级，自动加载）**

`.github/copilot-instructions.md`，在此项目中打开 Copilot Chat 时自动读取，无需任何配置。

**全局设置（Copilot + Cline）**

`Cmd+Shift+P → Preferences: Open User Settings (JSON)`，将 `vscode-settings-snippet.jsonc` 中对应字段合并进去。

**Cline（项目级，自动加载）**

`.clinerules` 位于项目根目录，Cline 扩展打开项目时自动识别加载。

---

## Obsidian

**配置步骤**

1. **启用 Templater**：`Settings → Community Plugins` 搜索安装 → 设置 Template Folder 为 `Templates`
2. **新建文章**：`Cmd+P → Templater: Create new note from template` → 选择「沐风博客模板」，按注释框架填写
3. **配置 AI 插件**：打开 `Templates/沐风AI写作提示词.md`，按下表粘贴提示词

| 插件 | 设置路径 |
|---|---|
| Copilot | Settings → Copilot → System Prompt |
| Smart Connections | Settings → Smart Chat → System Prompt |
| BMO Chatbot | Settings → BMO → System Role Prompt |
| Text Generator | Settings → Text Generator → System Prompt |

4. **发布前检查**：在文章末尾插入「沐风写作检查清单」模板，逐项打勾后再发

---

## Notion

**配置步骤**

1. **导入风格指南**：侧边栏 → Import → Upload file → 选择 `沐风写作风格指南.md` → 设为 Favorite，写作时随时参考
2. **创建文章数据库模板**：导入 `沐风博客文章模板.md` → 页面右上角 `···` → Turn into template → 之后新建文章直接套用
3. **配置 Notion AI**：头像 → Settings → AI → Custom instructions → 将 `Notion-AI-自定义指令.md` 中两个输入框的内容分别粘贴进去，一次配置永久生效

---

## 五平台对照

| 平台 | 核心文件 | 触发方式 |
|---|---|---|
| Claude Code | `.claude/commands/mufeng-writing-skill.md` | `/mufeng-writing-skill` |
| Cursor | `.cursor/rules/mufeng-writing-skill.mdc` | 打开 `.md` 文件自动加载 |
| VS Code Copilot | `.github/copilot-instructions.md` | Copilot Chat 自动加载 |
| VS Code Cline | `.clinerules` | 打开项目自动加载 |
| Obsidian | `Templates/` 三件套 | Templater 插入 + AI 插件粘贴 |
| Notion | `Notion/` 三件套 | 导入页面 + AI 设置粘贴 |
