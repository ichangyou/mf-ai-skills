# mufeng-app-icon

独立的 App icon 设计 Skill，默认面向 iOS/iPadOS，支持新图标、重做和局部精修。
Codex 与 Claude Code 共用同一份流程：真实上下文 → 比较方向 → 统一规则 → 制作适配 → 实际验证。
页面 UI、操作图标与独立 logo 请使用相应设计工作流。

## 安装

在本仓库根目录执行：

```bash
python3 scripts/install.py --platform both --scope user --skill mufeng-app-icon
```

安装器不覆盖同名资源。项目级与复制安装见[安装文档](../../docs/installation.md)。安装后重新加载 skills 或重启客户端。

## 使用

Codex：

```text
$mufeng-app-icon 为当前 iOS App 设计图标。先读产品与现有品牌，比较三个不同方向，自主推荐并精修，交付源文件和小尺寸预览。
```

Claude Code：

```text
/mufeng-app-icon 优化这个已有 App icon，保留核心轮廓，解决小尺寸细节不清楚的问题，并按项目工具链检查导入方式。
```

需要先选方向时加“先给可视候选，等我选择再精修”；只要素材时加“不集成 App”。

## 能力和依赖

- 概念、形状、负空间、光学重心、色彩和小尺寸辨识检查。
- 几何矢量、生图或已有素材编辑，按宿主实际能力选择；不会安装生图服务。
- 平面图标或分层流程的适配；系统外观与格式按当前官方文档核实。
- 多尺寸预览脚本需要 Python 3.10+ 和 Pillow（`python3 -m pip install Pillow`，使用自己的 Python 环境）。
- App 集成验证需要 macOS、Xcode、可运行项目和模拟器/设备；缺少时可以交付素材，但标注未验证。
- 不依赖其他 skill、BaoCut 或固定 MCP。两端拥有的生图和自动化工具可能不同。

## 多尺寸预览

将 `SKILL_DIR` 设为实际加载的 Skill 目录，然后运行：

```bash
python3 "$SKILL_DIR/scripts/preview.py" path/to/icon.png --output path/to/project/icon-review/preview.png
```

接受单帧方形 PNG/JPEG/WebP；SVG/PDF 先用现有工具渲染。
脚本生成实际像素大小的平面预览，报告源尺寸、实际透明度和是否放大，不修改源文件，也不覆盖已有输出。
它不是官方遮罩、Icon Composer 或商店验证器；需实际查看图片，深背景不等于深色图标变体。

## 输出和限制

按任务交付采用方向、真实源文件/图层（能力允许时）、栅格导出、预览和检查结果。
所有采用图片保存在目标项目。仅有栅格时不声称已有矢量母版；仅有提示词时不声称已生成图标。
不自动上传、发布或做转化实验，亦不承诺商标可注册或商店审核通过。

入口见 [SKILL.md](SKILL.md)，许可见仓库 [MIT](../../LICENSE)。本工作流独立编写，不附带第三方品牌素材。
