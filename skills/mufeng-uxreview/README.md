# mufeng-uxreview

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

## 调用

Codex：

```text
$mufeng-uxreview [任务或素材]
```

Claude Code：

```text
/mufeng-uxreview [任务或素材]
```

## 依赖与执行范围

目标页面代码，必要时提供截图。

“支持”表示提供两端入口和执行说明；外部服务、账号认证及工具能力需单独配置。实际执行规则见 [SKILL.md](SKILL.md)。

以资深产品设计师身份评审指定页面或界面。读真实组件代码（Tailwind / SwiftUI）后，按层级、间距、文案、可供性、设计系统违规五个维度分组汇报，按影响排序。只给方案，批准前不改代码。

```
/mufeng-uxreview [页面或组件路径]
```

**示例**：

```
/mufeng-uxreview src/pages/Settings.tsx
/mufeng-uxreview 看看 ShotZen 的相册选择页有什么问题
```
