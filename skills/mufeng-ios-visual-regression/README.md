# mufeng-ios-visual-regression

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

## 调用

Codex：

```text
$mufeng-ios-visual-regression [任务或素材]
```

Claude Code：

```text
/mufeng-ios-visual-regression [任务或素材]
```

## 依赖与执行范围

macOS + Xcode + iOS Simulator + Python 3 + Pillow；应用需要 DEBUG harness。

“支持”表示提供两端入口和执行说明；外部服务、账号认证及工具能力需单独配置。实际执行规则见 [SKILL.md](SKILL.md)。

运行脚本前，将 shell 变量 `SKILL_DIR` 设为实际安装目录（包含本文件和 `SKILL.md` 的目录）。相对资源路径均以该目录为准。

iOS 视觉回归测试（UIKit / SwiftUI 通用）。任何 UI 改动（布局、颜色、间距、字体、深色模式、本地化文案）之后，通过模拟器对每个顶层页面在所有支持语言和明暗外观下截图，与已提交的基线对比，产出框出差异区域的 HTML 报告。

本 skill 是共享引擎，每个项目自带 `VisualRegression/config.json` 和一个 DEBUG-only 的应用内 harness。

```bash
$SKILL_DIR/scripts/run.sh init       # 初始化新项目
$SKILL_DIR/scripts/run.sh check      # UI 改动后检查
$SKILL_DIR/scripts/run.sh baseline   # 接受当前 UI 为基线
```

需要 macOS + Xcode 模拟器。
