 **Codex 里使用技能** 的标准方式（适用于 Codex app/CLI/IDE）：

1. **创建/导入 Codex 技能**  
   Codex 技能是一个文件夹，核心是 `SKILL.md`（包含 name/description/说明），还可以带 `scripts/`、`references/`、`assets/` 等可选内容。([developers.openai.com](https://developers.openai.com/codex/skills?utm_source=openai))  
2. **在 Codex app 中管理**  
   Codex app 有 Skills 入口，可以创建/管理技能，也能在项目间复用。([openai.com](https://openai.com/index/introducing-the-codex-app/?utm_source=openai))  
3. **在对话里显式调用**  
   Codex 只会默认载入技能的名称和描述，**只有当你在对话中显式请求使用该技能时**，才会加载技能正文并执行。([developers.openai.com](https://developers.openai.com/codex/skills/create-skill/?utm_source=openai))  
4. **跨环境可用**  
   Codex 技能在 app、CLI 和 IDE 扩展中都可以使用。([developers.openai.com](https://developers.openai.com/codex/app/features/?utm_source=openai))  


**使用方式**
在 Codex 对话里直接触发即可，例如：
- “请使用 `dankoe-writing` 写作风格，写一篇关于……的长文”
- “用 Dan Koe 风格写一篇深度文章，主题是……”

该技能会按说明先询问：作者名字、写作地点（可选）、时间（可选）、话题。
