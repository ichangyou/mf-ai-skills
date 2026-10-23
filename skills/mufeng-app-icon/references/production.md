# 素材制作

## 选择真实可用的路径

| 情况 | 合适路径 | 如实交付 |
|---|---|---|
| 简洁几何、符号或字母形状 | 绘制真实 SVG/PDF 矢量并渲染检查 | 矢量源与栅格预览 |
| 复杂插画、拟物或材质探索 | 可用的生图/绘图工具 | 原始栅格及精修合成；分层按实际能力 |
| 已有图标局部调整 | 支持参考图的编辑工具或可编辑源文件 | 新版本与保留的原文件 |
| 没有生图工具 | 可执行的矢量方案，或明确标注的概念说明 | 实际完成的文件；提示词不算成图 |

工具由宿主能力决定，不强制用户更换供应商或安装另一个 skill。
在 Codex 可用时优先使用其内置生图能力；Claude Code 使用实际配置的生图工具。遵守当前工具关于编辑、参考图和输出的规则，不猜 API、模型名称或环境变量。

## 生图 brief

给工具的描述至少明确：核心意象、形状关系、产品气质、构图、色彩、背景，以及不应出现的内容。
需要前景层时明确要求孤立主体与透明背景；需要平面合成图时不要误要求整体透明。
按工具支持的尺寸和格式生成，不要求它提供实际不存在的原生分辨率、矢量或图层。

示例结构是任务变量，不是固定的美术风格：

```text
Create an app icon concept for [actual app purpose].
Use [chosen metaphor] with [distinctive silhouette or negative space].
Keep [brand constraint] and a clear primary focal point.
Use [palette and surface treatment] suited to [product personality].
Show the artwork directly, without a phone mockup, app name caption,
watermark, or a pre-baked operating-system corner mask.
Output [supported format/background]; preserve [features when editing].
```

不默认把平台阴影、遮罩和所有材质效果烘焙进源图；按实际导入流程决定哪些效果由系统生成。
需要多次调整时保留稳定的概念标识和参考图，避免每轮从零随机生成。

## 真实源文件

- SVG 内包含可编辑路径或形状，不能只嵌一张 PNG 就称矢量母版。
- 自动描摹后检查路径噪点、转角、空洞和小尺寸识别；转换成功不是设计验收。
- 分层源明确每层用途、顺序和透明条件。不能从一张平面图假称恢复了原始图层。
- 有文字时保留可编辑文字源；交付转曲版本时另存副本，记录字体来源。
- 前景透明可以合理；传统平面图标与分层背景的透明要求应按目标平台分别核实。

## 保存

采用目标项目已有素材目录。没有约定时，可用 `design/app-icon/` 放 brief、候选、源文件与 review；只创建本次确有需要的文件。
正式导入资源使用项目既有 Asset Catalog 或图标入口。不要将预览图误放到正式图标槽。
每次生成后先检查生成源非空，再复制采用结果到项目并验证副本；继续下一张前完成保存。
记录实际工具与素材来源，不随包携带第三方品牌标志；不复制现有 App 的可识别图标。
