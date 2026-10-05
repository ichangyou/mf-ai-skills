# mufeng-bilingual-storybook

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

## 调用

Codex：

```text
$mufeng-bilingual-storybook [任务或素材]
```

Claude Code：

```text
/mufeng-bilingual-storybook [任务或素材]
```

## 依赖与执行范围

Python 3.10+、Pillow、pypdfium2、生图与图片查看工具；当前 PDF 默认字体需要 macOS 的 Songti/Times 字体。

“支持”表示提供两端入口和执行说明；外部服务、账号认证及工具能力需单独配置。实际执行规则见 [SKILL.md](SKILL.md)。

## 使用示例

```text
读取当前故事目录，先生成中英文分镜与旁白，再生成参考图一致的插画。
每页通过视觉检查后，输出中文和英文两份 PDF。
```

## 生图配置

Codex 优先使用可用的内置 ImageGen。Claude Code 需要已安装、已认证且支持参考图和编辑的生图工具。
参见 [平台配置](references/platforms.md)。辅助脚本不调用图片 API，也不会因为安装 skill 而自动获得生图权限。

## 脚本使用

先把 `SKILL_DIR` 设为实际安装目录。从目标故事项目运行：

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" --help
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" --project-dir . --output-dir build/storybook --prompts-only
```

`--prompts-only` 只生成计划；`--dry-run` 只生成带标记的布局占位图。两者都不是最终插画。
真正的图片必须逐张复制到故事项目、通过 QA 后才能组装 PDF。

完整流程见 [workflow.md](references/workflow.md)，已有章节修订与最终发布见 [revision-release.md](references/revision-release.md)。
