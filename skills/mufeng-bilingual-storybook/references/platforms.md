# Codex / Claude Code 图片配置

Codex 优先使用可用的内置 ImageGen，来源默认是 `${CODEX_HOME:-$HOME/.codex}/generated_images/`。
Claude Code 使用用户明确安装、认证的生图 skill、MCP 或工具。需要 PNG 保存、参考图输入、局部编辑和宿主图片查看能力。
没有工具时只输出文字与提示词计划，不生成假图片，不报告最终 PDF 完成。

非默认工具设置其真实专用输出目录，并在整个流程中保持一致：

```bash
export MUFENG_IMAGE_ROOT="/path/to/dedicated-image-output"
```

变量不会安装生图服务，不得指向 `/` 或主目录。按实际工具文档映射 frozen prompt 和任务参考图，不臆造通用参数。
每次记录开始/返回事件，使用调用的精确 PNG 路径：

```bash
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" --output-dir <project-build-dir> --import-candidate <exact-generated-png> --task-id <task-id>
```

每次生成后检查源 PNG 非空并可解码，立即导入项目内候选区，验证副本后再继续下一张。
全部视觉 QA 通过后才进入最终 `images/` 和 PDF；用真实审核者标识替换 `pending-reviewer`。
无法确定调用与图片一一对应时使用串行模式。目录、哈希和日志不是服务商身份认证。
