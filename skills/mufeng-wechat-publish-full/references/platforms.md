# 两端工具配置

Codex 优先使用实际可用的内置生图工具；Claude Code 使用用户已配置的生图 skill/MCP/工具。
没有生图工具时可保留已有真实图片，完成文章整理并报告缺口，不伪造图片、不自动换服务商。
采用的每张图片都要检查源文件，立即保存到当前项目并验证副本，再执行上传。

GitHub 图床需要已认证 `gh` 和仓库写权限；上传脚本的 `--repo` 可覆盖作者默认仓库。
发布依赖已安装的 `baoyu-post-to-wechat`、Bun 和公众号认证配置。
从该 skill 的实际目录定位 `scripts/wechat-api.ts`：

```bash
export MUFENG_WECHAT_SCRIPT="/path/to/baoyu-post-to-wechat/scripts/wechat-api.ts"
```

两端使用同一脚本；其他已配置发布 MCP 可按其文档完成相同阶段。
变量不提供安装或账号认证。依赖缺失时保留本地文件，明确未执行的阶段，不声明发布成功。
