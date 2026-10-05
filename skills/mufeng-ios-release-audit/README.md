# mufeng-ios-release-audit

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

## 调用

Codex：

```text
$mufeng-ios-release-audit [任务或素材]
```

Claude Code：

```text
/mufeng-ios-release-audit [任务或素材]
```

## 依赖与执行范围

iOS 项目；编译检查需要 macOS + Xcode。

“支持”表示提供两端入口和执行说明；外部服务、账号认证及工具能力需单独配置。实际执行规则见 [SKILL.md](SKILL.md)。

iOS App Store 上线前完整发布审计。逐项核验权限文案、托管 EULA/条款 URL 及违禁内容条款、硬编码价格、`.lproj` 本地化完整性、App 图标、版本号与 build 号、数据层强制解包、零编译警告、多语言商店元数据，并产出微信 / X / Reddit 上线文案。

清单的每一项都来自真实的拒审或事故，不是通用最佳实践的罗列。全程只读，发现问题先报告根因和修复方案。

```
/mufeng-ios-release-audit
```

仅适用于 iOS / App Store 项目。
