# mufeng-weread-x-writing

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

## 调用

Codex：

```text
$mufeng-weread-x-writing [任务或素材]
```

Claude Code：

```text
/mufeng-weread-x-writing [任务或素材]
```

## 依赖与执行范围

Python 3.10+；已配置的微信读书 skill/MCP，或用户提供的真实导出材料。

“支持”表示提供两端入口和执行说明；外部服务、账号认证及工具能力需单独配置。实际执行规则见 [SKILL.md](SKILL.md)。

运行脚本前，将 shell 变量 `SKILL_DIR` 设为实际安装目录（包含本文件和 `SKILL.md` 的目录）。相对资源路径均以该目录为准。

从微信读书笔记、批注和阅读材料提炼原创中文 X 推文，结合最近 7/30 天本地历史检查重复。默认生成候选并保存，不自动发布。

示例：

```text
从这份阅读导出生成 6 条推文候选，并检查最近 30 天历史。
```

历史默认保存在 `~/.local/share/mf-ai-skills/weread-x/history.jsonl`；已有旧历史时继续使用。脚本通过 `MUFENG_WEREAD_X_HOME` 或 `--history` 指定位置。
