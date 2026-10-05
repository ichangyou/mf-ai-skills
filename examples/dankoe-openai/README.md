# 可选 OpenAI API 示例

这里保留 `write_article.py` 作为独立 API 示例，不属于 Codex / Claude Code 的 skill 加载与安装流程。
两端 skill 使用方法见 [mufeng-dankoe-writing](../../skills/mufeng-dankoe-writing/README.md)。

运行这个示例需要单独安装 OpenAI Python SDK、设置 `OPENAI_API_KEY` 并核对当前账号可用模型。
脚本中的模型默认值是历史示例，不作为当前模型推荐。本次结构优化未执行真实 API 请求。

```bash
python write_article.py "话题" "作者" "地点" "时间"
```

脚本有独立提示词，修改主 skill 不会自动改变这个示例。若希望严格复用主 skill 的行为，请直接在宿主调用主 skill。
旧文档曾列出的 Cursor/Copilot/Node/Shell 集成文件并未包含在仓库中，不能按那些路径安装。
