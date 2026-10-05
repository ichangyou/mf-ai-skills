# 两端工具配置

Codex 优先使用实际可用的内置生图工具。Claude Code 使用用户已安装、认证的生图 skill/MCP/工具；按其文档传入提示词与参考图。
工具必须提供可保存的图片。每次检查源文件、立即复制到当前项目的 `imgs/<article-slug>/`，验证副本后再继续或上传。
无生图工具时完成文章和提示词并报告缺失依赖，不制造假截图或占位插画，不自动切换服务商。

图床使用已认证 `gh` 和有写权限的仓库，上传脚本可用 `--repo` 指定自己的仓库。
发布前从已安装 `baoyu-post-to-wechat` 的真实目录找到 `scripts/wechat-api.ts`，设置 shell 变量：

```bash
export MUFENG_WECHAT_SCRIPT="/path/to/baoyu-post-to-wechat/scripts/wechat-api.ts"
```

需要 Bun 和发布工具要求的公众号凭据。变量本身不会安装脚本或认证账号。
有其他已配置的发布 MCP 时，按其实际文档执行相同发布阶段。
工具或凭据缺失时保留本地文章，明确未上传/未发布的阶段。
