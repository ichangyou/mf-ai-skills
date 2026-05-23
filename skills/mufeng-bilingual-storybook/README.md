# mufeng-bilingual-storybook

> 中英双语 AI 绘本生成器 / Bilingual AI picture book generator (Chinese & English)

---

## 中文说明

### 功能描述

基于 Markdown 素材生成中英双语 AI 绘本，输出可交付的中文版和英文版 PDF。适用于儿童绘本创作、经典故事改编、教育内容制作等场景。

**核心规则**：
- 使用 Codex 内置图像生成，不调用 OpenAI Images API，不需要 `OPENAI_API_KEY`
- 使用 `mufeng_storybook.py` 辅助脚本处理文本和 PDF 构建
- 图片中不嵌入任何可读文字（包括中文题目、标注、水印）

### 安装与激活

本 skill 运行于 Codex 环境，使用 Codex 内置图像生成能力。确认 `CODEX_HOME` 环境变量已设置（默认 `$HOME/.codex`）：

```bash
# 验证辅助脚本可用
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" --help
```

在支持 Codex 的环境中，通过以下命令激活 skill：

```
/mufeng-bilingual-storybook
```

### 使用方式

**基本调用**（自动判断页数）：

```
/mufeng-bilingual-storybook
[提供故事 Markdown 文件或内容]
```

### 页数选择规则

| 故事类型 | 推荐页数 |
|---------|---------|
| 短篇 / 单章节 | 12 页 |
| 中篇 / 多个情节节点 | 16 页 |
| 正式绘本章节 | 20 页 |
| 长篇 / 复杂章节 | 24 页 |

未指定时自动判断，使用 `--scene-count auto`。

### 常用命令

**仅生成场景和提示词文件**：

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto \
  --scene-count auto \
  --prompts-only
```

**从已生成图片构建 PDF**：

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto \
  --scene-count auto \
  --use-existing-images \
  --language both
```

**布局验证（不生成图片）**：

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto_dryrun \
  --scene-count auto \
  --dry-run \
  --language both
```

**指定固定页数**：

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_12 \
  --scene-count 12 \
  --prompts-only
```

### 工作流程

1. 加载项目中所有 Markdown 文件（跳过 build/cache/vendor 目录）
2. 自动选择页数（或使用用户指定值）
3. 生成 `scenes.parsed.md`、`prompts.generated.md`、`manifest.json`
4. 使用 Codex 内置图像生成，每个场景生成一张全页插图
5. 将图片复制到 `<output-dir>/images/`
6. 构建中文版（`storybook.pdf`）和英文版（`storybook_en.pdf`）
7. 验证页数、图片数量和渲染效果

### 翻译规范

- 每页双句旁白，精简清晰
- 中文旁白自然流畅，避免生僻字（防止字体渲染问题）
- 英文翻译面向儿童，保留情节和情感，不逐字直译
- 页面标题保持简短

### 注意事项

- 图片内不嵌入任何可读文字（包括牌匾、碑文等故事中的文字场景）
- 每个场景独立生成一张图，不将多个场景合并为变体
- 详细流程参考 `references/workflow.md`

---

## English Guide

### Description

Generates bilingual AI picture books (Chinese and English) from Markdown source material, producing deliverable Chinese (`storybook.pdf`) and English (`storybook_en.pdf`) PDFs. Suitable for children's book creation, classic story adaptation, and educational content production.

**Core rules**:
- Uses Codex built-in image generation — does NOT call OpenAI Images API, does NOT require `OPENAI_API_KEY`
- Uses `mufeng_storybook.py` helper script for deterministic text/PDF work
- No readable text embedded in images (including Chinese titles, labels, or watermarks)

### Installation & Activation

This skill runs in the Codex environment using Codex's built-in image generation. Verify the `CODEX_HOME` environment variable is set (defaults to `$HOME/.codex`):

```bash
# Verify the helper script is available
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" --help
```

In a Codex-enabled environment, activate the skill with:

```
/mufeng-bilingual-storybook
```

### Usage

**Basic invocation** (auto-determines page count):

```
/mufeng-bilingual-storybook
[Provide story Markdown files or content]
```

### Page Count Rules

| Story type | Recommended pages |
|------------|------------------|
| Short story / compact single episode | 12 pages |
| Medium chapter / several clear beats | 16 pages |
| Formal picture-book chapter | 20 pages |
| Long or complex chapter | 24 pages |

Defaults to `--scene-count auto` when not specified.

### Common Commands

**Generate scene and prompt files only**:

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto \
  --scene-count auto \
  --prompts-only
```

**Build PDFs from already-generated images**:

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto \
  --scene-count auto \
  --use-existing-images \
  --language both
```

**Dry layout check without generating images**:

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto_dryrun \
  --scene-count auto \
  --dry-run \
  --language both
```

**Force an exact page count**:

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_12 \
  --scene-count 12 \
  --prompts-only
```

### Workflow

1. Load all Markdown files in the project (skip build/cache/vendor folders)
2. Auto-select page count (or use user-specified value)
3. Generate `scenes.parsed.md`, `prompts.generated.md`, `manifest.json`
4. Use Codex built-in image generation — one full-page illustration per scene
5. Copy images to `<output-dir>/images/`
6. Build both PDFs: Chinese (`storybook.pdf`) and English (`storybook_en.pdf`)
7. Verify page count, image count, and sample rendered pages

### Translation Guidelines

- Two short sentences of narration per page, clear and simple
- Chinese narration uses natural language; avoid rare glyphs (prevents font rendering issues)
- English translation targets children — preserve plot and emotion, do not translate literally
- Page titles kept short

### Notes

- No readable text inside any image, even when the source story references tablets, plaques, or inscriptions
- Each scene gets its own distinct image — do not merge multiple scenes into one prompt
- For detailed workflow guidance, see `references/workflow.md`
