# mufeng-bilingual-storybook Skill 使用说明

## 简介

`mufeng-bilingual-storybook` 是一个可在 Codex 中复用的 AI skill，用于把项目中的 Markdown 故事材料制作成中英文绘本。

它适合这类任务：

- 读取项目内所有 Markdown 文件
- 根据故事内容拆分绘本分镜
- 生成中文旁白、英文旁白和图片提示词
- 使用 Codex 内置生图能力生成每页插图
- 生成中文版 PDF 和英文版 PDF

核心原则：不调用 OpenAI Images API，不依赖 `OPENAI_API_KEY`，图片由 Codex 内置生图能力完成。

## Skill 信息

- Skill 名称：`mufeng-bilingual-storybook`
- Skill 路径：`$HOME/.codex/skills/mufeng-bilingual-storybook`
- 主说明文件：`$HOME/.codex/skills/mufeng-bilingual-storybook/SKILL.md`
- 辅助脚本：`$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py`
- 流程参考：`$HOME/.codex/skills/mufeng-bilingual-storybook/references/workflow.md`

## 在 Codex 中调用

在 Codex 中可以这样说：

```text
Use $mufeng-bilingual-storybook to read all markdown files and generate a bilingual picture-book PDF.
```

中文也可以：

```text
使用 $mufeng-bilingual-storybook 读取当前项目所有 Markdown，生成中英文绘本 PDF。
```

如果要指定页数：

```text
使用 $mufeng-bilingual-storybook 生成 12 页中英文绘本，每页一张图和两三句旁白。
```

## 自动页数策略

默认使用：

```bash
--scene-count auto
```

自动模式会根据 Markdown 内容长度和结构复杂度选择页数：

- 短文 / 单个小故事：12 页
- 中等章节 / 几个清晰情节点：16 页
- 正式绘本章节：20 页
- 长章节 / 情节复杂：24 页

自动判断会记录在输出目录的 `manifest.json` 中，字段为 `scene_count_info`。

如果传入 `--scene-plan`，则以 scene plan JSON 的条目数量为准。

## 推荐工作流

### 1. 生成分镜和图片提示词

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto \
  --scene-count auto \
  --prompts-only
```

输出：

- `build/storybook_auto/scenes.parsed.md`
- `build/storybook_auto/prompts.generated.md`
- `build/storybook_auto/manifest.json`

### 2. 使用 Codex 内置生图能力生成图片

打开 `prompts.generated.md`，逐个使用每页 prompt 生成图片。

每张图片保存到：

```text
build/storybook_auto/images/
```

文件名必须与 `manifest.json` 或 `prompts.generated.md` 中的 expected image 一致，例如：

```text
scene_01_混沌初开.png
scene_02_仙石孕育.png
```

注意：图片中不要出现可读文字、标题、字幕、水印、边框、牌匾文字或气泡文字。

### 3. 用已有图片生成中英文 PDF

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto \
  --scene-count auto \
  --use-existing-images \
  --language both
```

输出：

- 中文版：`build/storybook_auto/storybook.pdf`
- 英文版：`build/storybook_auto/storybook_en.pdf`

## 固定页数示例

生成 12 页：

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_12 \
  --scene-count 12 \
  --prompts-only
```

生成 20 页：

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_20 \
  --scene-count 20 \
  --prompts-only
```

## Dry-run 布局测试

如果只是检查 PDF 版式，不想先生成真实图片，可以使用 dry-run：

```bash
python "$HOME/.codex/skills/mufeng-bilingual-storybook/scripts/mufeng_storybook.py" \
  --project-dir . \
  --output-dir build/storybook_auto_dryrun \
  --scene-count auto \
  --dry-run \
  --language both
```

dry-run 会生成占位图和 PDF，用来验证：

- 页数是否合理
- 图片区域是否正常
- 中英文旁白是否溢出
- 页码和页脚是否正常

## 输出目录结构

典型输出如下：

```text
build/storybook_auto/
├── scenes.parsed.md
├── prompts.generated.md
├── manifest.json
├── images/
│   ├── scene_01_xxx.png
│   ├── scene_02_xxx.png
│   └── ...
├── storybook.pdf
└── storybook_en.pdf
```

## 生成质量建议

- 每页只表达一个清晰情节点。
- 中文旁白控制在两三句以内。
- 英文旁白不要逐字硬译，要适合儿童阅读。
- 图片 prompt 要保持角色、场景和画风连续。
- 遇到石碑、牌匾、卷轴等元素，只要求抽象装饰纹理，不要求真实文字。
- 如果某页中文字体显示不自然，优先改写为更常见的汉字表达。

## 校验命令

检查 PDF 页数：

```bash
file build/storybook_auto/storybook.pdf build/storybook_auto/storybook_en.pdf
```

检查图片数量：

```bash
find build/storybook_auto/images -maxdepth 1 -type f -name '*.png' | wc -l
```

如果安装了 `pdftoppm`，可以导出预览页：

```bash
mkdir -p build/storybook_auto/preview
pdftoppm -f 1 -l 1 -png -r 100 build/storybook_auto/storybook.pdf build/storybook_auto/preview/page_zh
pdftoppm -f 1 -l 1 -png -r 100 build/storybook_auto/storybook_en.pdf build/storybook_auto/preview/page_en
```

## 注意事项

- 这个 skill 的脚本只处理确定性的文本、提示词、图片校验和 PDF 生成。
- 生图步骤由 Codex 内置生图能力完成，不由脚本调用外部图片 API。
- 中英文 PDF 共用同一批图片，不会重复生成两套图片。
- 如果已有 `--scene-plan`，最终页数由 JSON 条目数量决定。
- 如果手动指定 `--scene-count 12`、`16`、`20` 或 `24`，会覆盖自动判断。

