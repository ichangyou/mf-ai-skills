# 原生界面

## 保持原生行为

- 先读实际 View / ViewController、导航容器、共享样式与状态管理；不要根据截图猜组件架构。
- 改视觉不顺带改变导航层级、业务状态或数据流。确需改变时解释它与用户目标的关系。
- 沿用原生导航、列表、sheet、菜单和输入行为；自绘替代需要明确的体验收益。
- 检查最低系统版本，再采用较新的 API、材质或控件；需要时提供与项目一致的可用性分支。
- 避免把系统设计风格强加到所有内容容器。材质、动效与装饰服务于层级和任务。

## 可读性与布局

- 先用系统语义文字样式和项目既有字体。自定义字体也要支持缩放，不能只改固定字号。
- 按内容优先级决定标题、说明和主要操作的视觉权重，避免所有卡片都同样突出。
- 使用布局约束、内容优先级和安全区域；不要把某一张手机画板的固定尺寸写进真实页面。
- 触控区域与可见图形分开考虑，通常以约 44×44 pt 的舒适目标设计，按实际控件与平台指南核实。
- 尽量用语义颜色覆盖明暗模式。正文、辅助文字、图标与焦点都要在实际背景上可辨认。
- SF Symbols 或项目既有图标优先，匹配文字权重；不拿 emoji 当通用操作图标。

## 状态和辅助功能

对当前改动涉及的状态检查即可，不凭空添加产品功能：

- 正常、选中、禁用；数据相关页面的加载、空、错误和长内容。
- VoiceOver 的名称、值、提示和朗读顺序；装饰图形避免重复朗读。
- 大字体换行、主要操作可达性、键盘出现与关闭、安全区域遮挡。
- 长译文和项目实际支持的文字方向；颜色之外还有可识别的状态提示。
- 涉及动画时检查 Reduce Motion；涉及透明材质时考虑 Reduce Transparency。

截图不能证明 VoiceOver 或键盘行为正确，实际交互需要单独检查。

## 使用当前平台文档

采用陌生或新 API、系统外观及导出规范前查询官方资料；无法访问时报告版本假设，不编造参数。

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [SF Symbols](https://developer.apple.com/sf-symbols/)

这些链接是按需核查入口，不代表已为当前项目验证全部要求。
