# mufeng-materials-to-wechat-publish

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

## 调用

Codex：

```text
$mufeng-materials-to-wechat-publish [任务或素材]
```

Claude Code：

```text
/mufeng-materials-to-wechat-publish [任务或素材]
```

## 依赖与执行范围

网络检索、mufeng-blog-writing、生图工具、已认证 gh；发布还需要 Bun、baoyu-post-to-wechat 和公众号凭据。

“支持”表示提供两端入口和执行说明；外部服务、账号认证及工具能力需单独配置。实际执行规则见 [SKILL.md](SKILL.md)。

运行脚本前，将 shell 变量 `SKILL_DIR` 设为实际安装目录（包含本文件和 `SKILL.md` 的目录）。相对资源路径均以该目录为准。

将目录素材自动转化为带插图的微信公众号图文并发布。全流程：素材读取 → 文章生成 → 图片生成 → GitHub 图床 → URL 插入 → 微信 API 发布。在两端配置依赖后运行。

```
/mufeng-materials-to-wechat-publish
```

## 发布结果与验证

默认通过 API 上传指定公众号的草稿箱，并用同账号 API 读取验证，不自动使用浏览器或 Computer Use。只有明确要求“正式发布”或“群发”才进入公开发布流程。原创标识和平台话题标签若接口不支持，列为待手动设置，不阻塞草稿上传。读取验证失败时保留已有草稿并报告，不重复上传。具体规则见 [完整发布 skill](../mufeng-wechat-publish-full/SKILL.md)。
