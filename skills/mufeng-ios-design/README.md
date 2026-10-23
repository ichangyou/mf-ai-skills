# mufeng-ios-design

为自己使用的原生 iOS 设计工作流：读取真实上下文 → 比较方向 → 统一规范 → 实现 → 实际验证。
支持 SwiftUI/UIKit UI 优化、App icon、界面图标和原创 logo，Codex 与 Claude Code 共用同一份内容。

## 安装与调用

在本仓库根目录执行，只安装这个 skill 到两端用户目录：

```bash
python3 scripts/install.py --platform both --scope user --skill mufeng-ios-design
```

安装器不覆盖已有同名目录。项目安装及复制安装见[安装文档](../../docs/installation.md)。
安装后重新加载 skills 或重启客户端。

Codex：

```text
$mufeng-ios-design 优化这个 SwiftUI 设置页，沿用品牌和导航结构，先检查现有实现，再修改并验证大字体和深色模式。
```

Claude Code：

```text
/mufeng-ios-design 为这个 App 设计原创 icon，比较三个不同隐喻的方向，再交付可编辑源文件和小尺寸预览。
```

也可明确要求使用 `mufeng-ios-design`，例如“设计一个同时能用于品牌 logo 和 App icon 的图形，并分别适配”。
若希望先决定方向再改代码，在请求中加“先给候选，等我选定”。局部修改不强制多方案。

## 依赖与边界

- 设计与源码分析需要项目代码或真实参考；只有截图时可以评审，不能声称已修改原生 App。
- 原生构建、运行和截图需要 macOS、Xcode、可运行项目及模拟器或设备；视觉判断还需要查看图片的能力。
- 简单几何标志可直接制作 SVG；复杂图像生成依赖宿主实际配置的生图工具。本 skill 不安装模型或服务。
- Codex 与 Claude Code 不保证拥有相同的生图或自动化工具。缺少能力时明确报告未完成项。
- 不要求 BaoCut、专用画布格式、MCP 或其他 skill，也不携带第三方品牌素材。

## 输出

按请求交付设计取舍、项目内的实现或图形源文件，以及真实检查结果和未验证项。
UI 优化保持项目架构；App icon 按目标系统/Xcode 适配；logo 按需交付单色、反白和字标组合。
采用图片必须保存到目标项目，临时生成路径不作为交付位置。

## 维护与来源

执行入口见 [SKILL.md](SKILL.md)，细则按需读取 `references/`。
本工作流重新编写，以项目上下文、原生平台约束与可验证交付为核心；没有复制 BaoCut Skill 正文、编辑器实现或 Anthropic 品牌素材。
平台规则以 [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) 和目标工具链当前文档为准。
文件按本仓库 [MIT 许可](../../LICENSE)提供；工具和外部素材遵守各自条件。
