Draw.io 官方 MCP 实测：AI 自动生成架构图，丝滑到离谱

![](https://upload-images.jianshu.io/upload_images/130752-15bbca3e5a8a8f1d.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

最近绘图神器 draw.io 发布了官方 MCP Server。真是喜大普奔（喜闻乐见、大快人心、普天同庆、奔走相告）。

我们现在可以在 Cursor、Claude Desktop 等支持 MCP 的编辑器里让 draw.io 帮忙画图，画完后，它会直接弹出网页编辑器，我们可以基于已绘制的图进行再次编辑，体验非常酷。

接下来我们一起看看怎么使用它。

### 安装与配置

#### 一、在 Cursor 中配置 MCP server：

1. 打开 Cursor，进入 **Settings → Cursor Settings → MCP**（或直接 `Cmd + Shift + J`）

2. 点击 **+ Add new global MCP server**，这会打开配置文件 `~/.cursor/mcp.json`

3. 填入：

```json
{
  "mcpServers": {
    "drawio-mcp": {
      "command": "npx",
      "args": ["-y", "@drawio/mcp"]
    }
  }
}
```

4. 保存后回到 MCP 设置页面，应该能看到 `drawio-mcp` 已列出，状态显示为绿色即表示连接成功。

> **提示**：如果状态显示红色/失败，可以点旁边的刷新按钮重试。同样注意 npx 路径问题，必要时用完整路径替代。

####  二、在 Claude 添加 drawio-mcp

##### 1）、在 Claude Mac 客户端中添加 MCP server 的步骤：

1. 打开 Claude 桌面客户端，点击菜单栏 **Claude → Settings → Developer → Edit Config**

2. 这会打开配置文件 `claude_desktop_config.json`，路径通常是：
   `~/Library/Application Support/Claude/claude_desktop_config.json`

3. 在文件中添加：

```jsonc
{
  "mcpServers": {
    "drawio-mcp": {
      "command": "npx",
      "args": ["-y", "@drawio/mcp"]
    }
  }
}
```

如果已有其他 MCP server，把 `"drawio-mcp": {...}` 加到 `mcpServers` 对象里即可。

4. 保存文件后**重启 Claude 客户端**。

5. 重启后在对话输入框左下角应该能看到 MCP 工具图标（🔨），点击可确认 drawio-mcp 的 tools 是否加载成功。

> **注意**：确保你的系统已安装 Node.js 和 npm，因为 `npx` 依赖它们。在 M1 Mac 上如果用 nvm 管理 Node，可能需要把 `command` 改为 npx 的完整路径（`which npx` 查看），避免 Claude 找不到命令。

#####  2）、Claude 网页端（claude.ai）目前**不支持直接添加自定义 MCP server**。

MCP server 配置只支持以下客户端：

- **Claude 桌面客户端** — 通过 `claude_desktop_config.json`
- **Claude Code**（CLI）— 通过 `claude mcp add` 命令
- **Cursor / Windsurf** 等第三方 IDE

如果你想在网页端使用 draw.io 功能，有两个替代方案：

1. **使用 Claude 桌面客户端**：按之前的方法配置。

2. **使用 Claude in Chrome 扩展**：集成 drawio-mcp 工具，让扩展生成 draw.io 图表。比如告诉扩展你想画什么图，扩展可以直接调用 `open_drawio_mermaid` 或 `open_drawio_xml` 来生成。


### 实战：画一个 SSO 时序图

在 Cursor 或者 Claude 客户端中向 AI 发出命令：

> 使用 draw.io MCP 工具 open_drawio_mermaid 制作展示 SSO 流程的时序图

![](https://upload-images.jianshu.io/upload_images/130752-2805a861c59cebfa.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

生成后，可以保存文档到 Google Drive。这样方便后续随时再次编辑。再也不用担心找不到历史编辑文件了。

![](https://upload-images.jianshu.io/upload_images/130752-bd1d1e96c2b83d06.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### draw.io MCP Server 技术原理与限制

##### 核心功能与流程

- draw.io MCP 工具将 AI 生成的 Mermaid/CSV/XML 逻辑转成 draw.io 专用链接，从而实现快速绘图
-  绘图流程为用户发指令→AI生成结构化数据→工具压缩编码→浏览器打开可编辑 draw.io 页面

##### 支持的核心转换模式
- Mermaid 转图（open_drawio_mermaid）：AI 写 Mermaid逻辑，draw.io 渲染编辑
- CSV 转图（open_drawio_csv）：适合组织架构等树状图，AI 处理人员关系生成
- XML原生格式（open_drawio_xml）：支持现成 draw.io XML 或AI 生成复杂图表

##### 技术原理与限制
- 实现原理为生成带压缩编码数据的 URL，本地浏览器解析，隐私性好
- 存在 URL 长度限制，超复杂图表可能因 URL 过长无法打开

### 小结

draw.io 发布官方 MCP Server，支持在 Cursor、Claude 等编辑器中通过 AI 生成可编辑图表，覆盖 Mermaid/CSV/XML 模式，虽然存在 URL 长度限制但隐私性好，体现传统工具拥抱 AI Agent 生态的大趋势。

工欲善其事，必先利其器。
技术人员很有必要折腾一下这个工具。
花点时间把这个工具配置好了，一次配置，接下来的所有时间里都可以使用这个得心应手的好工具了。

尤其是经常绘各种图的架构师同学们，有了这个，简直不能再爽！

AI  时代已经到来，必须拥抱 AI！ 个人，无论技术能力有多强，已经很难与 AI 的效率相比。必须充分利用 AI，让 AI 更多地为我们做事。这样才能如虎添翼。


参考：
1. [drawio-mcp](https://github.com/jgraph/drawio-mcp)
2. [终于等到！Draw.io 官方发布 MCP，这体验丝滑得不像话！](https://mp.weixin.qq.com/s/C4NBNl13_W4e-fxR-e_pdA)


2026.02.14 18:34
沪 · 汇金路KFC
