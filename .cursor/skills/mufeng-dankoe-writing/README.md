# Dan Koe 写作风格 - Cursor 集成包

## 📦 文件清单

| 文件名 | 用途 | 推荐使用场景 |
|--------|------|--------------|
| `.cursorrules` | Cursor 项目级别规则文件 | 写作专用项目（最推荐） |
| `dankoe-cursor-prompt.txt` | 纯文本 prompt | 复制到 Cursor 全局设置或临时使用 |
| `cursor-integration-guide.md` | 完整集成指南 | 查看详细的安装和使用说明 |
| `dankoe-writing.skill` | Claude.ai 原始 skill 文件 | 在 Claude.ai 或 Claude Desktop 中使用 |

## 🚀 快速开始（3 步搞定）

### 方法 1：项目级别集成（推荐）⭐

```bash
# 1. 将 .cursorrules 复制到你的项目根目录
cp .cursorrules /path/to/your/writing-project/

# 2. 用 Cursor 打开项目
cd /path/to/your/writing-project/
cursor .

# 3. 开始写作
# 在 Cursor 中按 Cmd/Ctrl + I 打开 Composer
# 输入：帮我写一篇关于「时间管理」的深度文章
```

### 方法 2：全局设置

```bash
# 1. 打开 Cursor 设置（Cmd/Ctrl + ,）
# 2. 搜索 "Rules for AI"
# 3. 复制 dankoe-cursor-prompt.txt 的内容粘贴进去
# 4. 保存并重启 Cursor
```

## 🎯 使用示例

### 基础使用

```
帮我写一篇关于「个人成长」的深度文章
作者：changyou
```

### 指定详细信息

```
用 Dan Koe 风格写一篇文章
话题：为什么大多数人的学习方法都是错的
作者：changyou
地点：北京
时间：260204 150000
```

### 续写/修改

```
继续按照 Dan Koe 风格写第三章
```

## 📖 预期效果

文章会包含：

✅ **挑衅性开场**：反常识观点
✅ **中文序号**：一、二、三...
✅ **5-7 个章节**：递进式结构
✅ **对话式风格**：大量使用"你"
✅ **理论+实践**：既有深度思考，又有行动步骤
✅ **短句冲击**：单独成段的关键观点
✅ **反问引导**：引发读者思考
✅ **个人化签名**：– [作者名]

## 🔧 配置选项

### 只在特定文件夹启用

```bash
# 创建写作专用目录
mkdir blog-writing
cp .cursorrules blog-writing/

# 代码目录不受影响
mkdir my-code-project
# 不复制 .cursorrules
```

### 临时禁用

```bash
# 重命名 .cursorrules
mv .cursorrules .cursorrules.bak

# 需要时再改回来
mv .cursorrules.bak .cursorrules
```

## 🐛 常见问题

### Q: Cursor 没有应用规则？

**解决方案**：
1. 确保 `.cursorrules` 在项目根目录
2. 文件名以点开头（`.cursorrules`）
3. 重启 Cursor：`Cmd/Ctrl + Shift + P` → `Reload Window`

### Q: 想要同时用于代码和写作？

**解决方案**：
- 在项目根目录：保持通用规则
- 在 `blog/` 子目录：放置 `.cursorrules`（写作专用）
- 在 `src/` 子目录：放置另一个 `.cursorrules`（代码规范）

### Q: 如何验证是否生效？

**测试命令**：
```
帮我写一篇关于时间管理的深度文章
```

**检查点**：
- 是否使用中文序号（一、二、三...）
- 是否有挑衅性开场
- 是否有 5-7 个章节

## 📚 更多资源

- **完整指南**：查看 `cursor-integration-guide.md`
- **原始 Skill**：`dankoe-writing.skill` 可用于 Claude.ai
- **纯文本版本**：`dankoe-cursor-prompt.txt` 可用于其他场景

## 🎨 高级技巧

### 1. 批量生成大纲

```
为以下话题生成 Dan Koe 风格的文章大纲：
1. 个人品牌建设
2. 创作者经济
3. 注意力管理
```

### 2. 风格检查

```
检查这篇文章是否符合 Dan Koe 风格：
[粘贴你的文章]
```

### 3. 结合文件引用

```
基于 @my-notes.md 写一篇 Dan Koe 风格的文章
```

## 🚀 下一步

1. ✅ 选择一个集成方法
2. ✅ 复制相应文件到项目
3. ✅ 重启 Cursor
4. ✅ 测试一篇文章
5. ✅ 开始高效创作！

---

## 💡 提示

- **首次使用**：建议先阅读 `cursor-integration-guide.md` 了解详细信息
- **团队协作**：可以将 `.cursorrules` 提交到 Git，团队成员自动获得相同风格
- **个性化**：可以根据自己的需求修改 `.cursorrules` 中的规则

祝写作愉快！🎉
