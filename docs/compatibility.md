# Codex 与 Claude Code 兼容性

全部 16 个 skill 共用同一份正文，并提供两端入口。`compatibility` 元数据声明执行条件，不安装依赖，也不表示已完成端到端测试。

| 能力 | Codex | Claude Code | 缺失时 |
|---|---|---|---|
| Markdown 工作流 | 共用正文 | 共用正文 | 说明缺少的素材 |
| 本地脚本 | 使用实际加载路径 | 使用实际加载路径 | 报告环境或依赖缺失 |
| 生图 | 优先可用的内置 ImageGen | 用户明确配置的生图 skill/MCP/工具 | 输出文字与提示词，注明未生成图片 |
| 视觉检查 | 当前图片查看能力 | 当前图片查看能力 | 不伪造 QA 通过记录 |
| 公众号发布 | 用户配置的发布工具 | 同样的发布工具 | 保留本地文章，注明未发布 |
| 微信读书 | 账号工具或导出材料 | 同样的数据来源 | 处理真实导出，不假装读取账号 |
| 独立子代理 | 宿主提供的子代理能力 | 宿主的 Agent 能力 | 顺序检查并说明不独立/不并行 |
| 历史会话 | 用户提供或配置的记录 | 同样的数据来源 | 报告覆盖范围和缺口 |

## 脚本路径

AI 从实际加载的 `SKILL.md` 路径确定 `SKILL_DIR`，再运行 `$SKILL_DIR/scripts/...`。
手动执行时由用户设置 shell 变量，例如 Codex 用户级绘本安装：

```bash
export SKILL_DIR="$HOME/.agents/skills/mufeng-bilingual-storybook"
python3 "$SKILL_DIR/scripts/mufeng_storybook.py" --help
```

Claude Code 用户级目录为 `$HOME/.claude/skills/<name>`；项目级与复制安装按实际位置设置。
`SKILL_DIR` 不是宿主自动替换宏。其他 skill 通过宿主发现列表定位，不假设同一安装目录。

## 生图配置

先选择实际可用的工具，检查认证、参考图输入、编辑和 PNG 保存能力。
安装本仓库不会给 Claude Code 增加内置 ImageGen，设置环境变量也不会启用服务。按工具实际文档调用，不猜测 API 或工具名。
绘本默认图片来源是 `${CODEX_HOME:-$HOME/.codex}/generated_images/`，其他工具设置实际使用的专用输出目录：

```bash
export MUFENG_IMAGE_ROOT="/path/to/dedicated-image-output"
```

流程中保持变量一致。脚本拒绝主目录和文件系统根目录；每次导入精确调用路径，保留目录边界、事件日志、PNG 校验、项目内复制和逐页 QA。
来源目录和日志不能独立认证服务商；完成报告应记录实际工具和调用证据。
不自动切换服务商，不用占位图冒充结果，所有采用图片必须保存在目标项目中。

## 公众号发布

图床需要 `gh` 登录及仓库写权限。上传脚本支持 `--repo`；默认 `mf-blog/blogPictures` 是作者配置，其他用户应指定自己的仓库。
API 发布需要已安装的 `baoyu-post-to-wechat`、Bun 和该工具要求的公众号凭据及网络配置，它们不包含在本仓库。
从实际安装位置定位 `scripts/wechat-api.ts`：

```bash
export MUFENG_WECHAT_SCRIPT="/path/to/baoyu-post-to-wechat/scripts/wechat-api.ts"
```

两端使用相同脚本；有其他已配置发布 MCP 时按其文档执行相同阶段。
缺少脚本、凭据或授权时，保留本地成果并报告实际完成阶段，不声明发布成功。

## 阅读历史与报告数据

新历史默认在 `~/.local/share/mf-ai-skills/weread-x/history.jsonl`，两端共用。旧历史存在且新位置不存在时继续使用旧版文件。
通过 `MUFENG_WEREAD_X_HOME` 或 `--history` 选择位置；切换前迁移旧记录，避免生成两套历史。
微信读书由已配置的 `weread-skills` 或 MCP 提供，仓库不包含它们。导出材料模式不需要账号接口。
周报、月报只读取实际可访问材料；skill 指令不能自动获取其他会话历史。

## 环境与验证边界

iOS 视觉回归需要 macOS、Xcode、Simulator 和项目专用 harness，这是系统和项目依赖。
绘本当前默认使用 macOS 的 Songti/Times 字体。股票报告需要 Pandoc，PDF 脚本通过 macOS Chrome/Chromium 路径发现浏览器。
双平台支持不表示已经支持所有操作系统。

自动校验检查结构和元数据；行为测试只证明实际执行的本地行为。
外部生图、账号读取、图床上传、公众号发布和真实 iOS 截图仍需已配置环境验证，不把本地测试通过写成外部服务已通过。
