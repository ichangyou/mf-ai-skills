# Dan Koe 写作 Skill - Cursor 集成完整指南

## 📦 包含文件

1. `.cursorrules` - Cursor 项目级别规则文件
2. `dankoe-cursor-prompt.txt` - 可复制粘贴的 prompt 文本
3. `cursor-integration-guide.md` - 本指南

## 🎯 三种集成方法

### 方法 1：项目级别 .cursorrules 文件（推荐）✨

这是最推荐的方法，因为它会自动应用到项目中的所有文件。

#### 步骤：

1. **复制 .cursorrules 文件**
   ```bash
   # 将 .cursorrules 文件复制到你的项目根目录
   cp .cursorrules /path/to/your/project/
   ```

2. **或者手动创建**
   - 在项目根目录创建 `.cursorrules` 文件
   - 将我提供的内容粘贴进去
   - 保存文件

3. **重启 Cursor**
   - 关闭并重新打开 Cursor
   - 或者使用命令：`Cmd/Ctrl + Shift + P` → `Reload Window`

4. **验证**
   - 在 Cursor 中输入：`帮我写一篇关于时间管理的深度文章`
   - AI 应该会按照 Dan Koe 风格创作

#### 优点：
✅ 自动应用，无需每次手动指定
✅ 团队协作时可以共享规则
✅ 版本控制友好（可以提交到 Git）

---

### 方法 2：Cursor 全局设置（适合个人使用）

这个方法会在所有项目中应用这个写作风格。

#### 步骤：

1. **打开 Cursor 设置**
   - Mac: `Cmd + ,`
   - Windows/Linux: `Ctrl + ,`

2. **找到 Rules for AI**
   - 在设置搜索框输入 "Rules"
   - 找到 `Cursor > General > Rules for AI`

3. **添加规则**
   - 点击 `Edit in settings.json`
   - 或者直接在文本框中粘贴 `dankoe-cursor-prompt.txt` 的内容

4. **设置格式**
   在 `settings.json` 中添加：
   ```json
   {
     "cursor.general.rulesForAI": "你是一位深度思考者和写作者，写作风格类似 Dan Koe...[粘贴完整内容]"
   }
   ```

5. **保存并重启**

#### 优点：
✅ 在所有项目中都可用
✅ 一次设置，永久使用
✅ 适合个人工作流

#### 缺点：
❌ 可能会影响正常的代码编写
❌ 不适合团队协作

---

### 方法 3：通过 Composer/Chat 临时使用

每次需要时手动激活这个风格。

#### 步骤：

1. **打开 Cursor Composer**
   - 快捷键：`Cmd/Ctrl + I`

2. **在第一条消息中添加指令**
   ```
   请使用以下写作风格：
   [粘贴 dankoe-cursor-prompt.txt 的内容]
   
   现在，帮我写一篇关于 [你的话题] 的深度文章
   ```

3. **开始对话**

#### 优点：
✅ 灵活控制何时使用
✅ 不影响其他工作
✅ 可以随时调整

#### 缺点：
❌ 每次都需要手动粘贴
❌ 比较繁琐

---

## 🚀 快速开始（推荐工作流）

### 场景 1：写博客/文章（专门项目）

1. 创建写作专用项目文件夹
   ```bash
   mkdir my-blog-writing
   cd my-blog-writing
   ```

2. 复制 `.cursorrules` 到这个文件夹
   ```bash
   cp .cursorrules my-blog-writing/
   ```

3. 用 Cursor 打开这个文件夹
   ```bash
   cursor .
   ```

4. 创建新文件并开始写作
   ```bash
   # 在 Cursor 中创建新文件
   touch article-01.md
   ```

5. 在 Composer 中输入
   ```
   帮我写一篇关于「个人成长」的深度文章
   作者：changyou
   地点：北京
   时间：260204 150000
   ```

### 场景 2：偶尔写文章（混合项目）

1. 打开 Cursor Composer (`Cmd/Ctrl + I`)

2. 输入触发词
   ```
   用 Dan Koe 风格帮我写一篇关于 [话题] 的深度文章
   ```

3. Cursor 会检测到 `.cursorrules` 并自动应用风格

---

## 🔧 高级配置

### 自定义触发关键词

编辑 `.cursorrules` 文件，在开头的触发条件部分修改：

```markdown
## 触发条件
当用户请求以下内容时应用此规则：
- 包含 "深度文章" 或 "长文"
- 包含 "Dan Koe" 或 "DK风格"
- 包含你自定义的关键词
```

### 结合 Cursor 的其他功能

1. **使用 @ 符号引用文件**
   ```
   基于 @my-notes.md 写一篇 Dan Koe 风格的文章
   ```

2. **使用 Composer 的多文件编辑**
   - 可以同时编辑多篇文章
   - 保持统一的写作风格

3. **使用 Cursor 的 AI Review**
   - 写完后让 AI 检查是否符合风格
   - `Cmd/Ctrl + K` → "检查这篇文章是否符合 Dan Koe 风格"

---

## ✅ 验证安装

测试以下场景，确保 skill 正常工作：

### 测试 1：基础写作
```
帮我写一篇关于「为什么大多数人的时间管理都是错的」的深度文章
```

**期望输出**：
- 使用中文序号（一、二、三...）
- 挑衅性开场
- 5-7 个章节
- 理论 + 实践结合
- 个人化签名

### 测试 2：风格检测
```
这段文字是否符合 Dan Koe 风格？[粘贴一段文字]
```

**期望输出**：
- 分析文字的风格特点
- 指出哪些符合/不符合
- 提供改进建议

### 测试 3：续写
```
继续按照 Dan Koe 风格写下去：[粘贴前文]
```

**期望输出**：
- 延续相同的风格和节奏
- 保持对话感和挑衅性

---

## 🐛 常见问题

### Q1: Cursor 没有识别到 .cursorrules 文件？

**解决方案**：
1. 确保文件名完全正确（以点开头）
2. 文件必须在项目根目录
3. 重启 Cursor (`Reload Window`)
4. 检查文件编码是否为 UTF-8

### Q2: AI 的回复不符合 Dan Koe 风格？

**解决方案**：
1. 在请求中明确提到 "Dan Koe 风格" 或 "深度文章"
2. 检查 `.cursorrules` 内容是否完整
3. 尝试在 Composer 中第一条消息就说明："请严格遵循 .cursorrules 中的写作风格"

### Q3: 想要在代码项目中临时禁用这个规则？

**解决方案**：
1. 方法 1：将 `.cursorrules` 文件重命名为 `.cursorrules.bak`
2. 方法 2：在 Composer 中说明："这次不使用 Dan Koe 风格"
3. 方法 3：创建子目录，在子目录中创建空的 `.cursorrules` 覆盖父目录规则

### Q4: 可以同时使用多个 rules 吗？

**答案**：
- 可以！Cursor 支持多个 rules 文件
- 在项目根目录：`.cursorrules`（写作风格）
- 在代码目录：`src/.cursorrules`（代码规范）
- Cursor 会根据当前文件位置选择最近的 rules

---

## 📚 使用示例

### 示例 1：创业主题文章

**输入**：
```
用 Dan Koe 风格写一篇文章
话题：为什么大多数人创业都在第一年失败
作者：changyou
```

**预期章节结构**：
```
一、你被骗了：关于创业的三个谎言
二、失败不是因为缺钱，而是缺这个
三、传统商业计划的致命缺陷
四、真正的创业者都在做什么
五、第一年的唯一目标
六、实践协议：90天生存指南
```

### 示例 2：个人成长主题

**输入**：
```
Dan Koe 风格深度文章
话题：突破职业瓶颈的真相
```

**预期特点**：
- 开篇挑战职业发展的传统观念
- 每章用反问句引导思考
- 结合心理学理论和实践案例
- 提供可执行的行动清单

---

## 🎨 进阶技巧

### 1. 创建写作模板

在项目中创建 `templates/article-template.md`：

```markdown
# [文章标题]

作者：changyou  
地点：[地点]  
时间：[时间]  

---

[这里用 Cursor Composer 生成内容]
```

### 2. 批量生成大纲

```
为以下 5 个话题分别生成 Dan Koe 风格的文章大纲：
1. 时间管理的真相
2. 为什么学习无效
3. 注意力经济陷阱
4. 个人品牌迷思
5. 创作者困境
```

### 3. 风格一致性检查

创建一个 checklist.md：

```markdown
## Dan Koe 风格检查清单

- [ ] 使用"你"进行对话
- [ ] 开篇有挑衅性观点
- [ ] 使用中文序号（一、二、三...）
- [ ] 包含 5-7 个主要章节
- [ ] 有对比论证
- [ ] 有反问句
- [ ] 有短句强调
- [ ] 有实践步骤
- [ ] 有个人化签名
```

使用时：
```
检查这篇文章是否符合 @checklist.md 中的所有要点
```

---

## 🔄 更新与维护

### 更新 Rules

1. 编辑 `.cursorrules` 文件
2. 保存更改
3. 在 Cursor 中运行：`Cmd/Ctrl + Shift + P` → `Reload Window`

### 版本控制

如果你的项目使用 Git：

```bash
# 添加到版本控制
git add .cursorrules

# 或者添加到 .gitignore（如果是个人配置）
echo ".cursorrules" >> .gitignore
```

### 团队协作

1. 将 `.cursorrules` 提交到代码仓库
2. 团队成员 clone 后自动获得相同的写作风格
3. 统一输出质量

---

## 📞 获取帮助

如果遇到问题：

1. **检查 Cursor 版本**
   - 确保使用最新版本的 Cursor
   - Help → About Cursor

2. **查看 Cursor 日志**
   - Help → Toggle Developer Tools
   - 查看 Console 中的错误信息

3. **社区支持**
   - Cursor 官方 Discord
   - Cursor 论坛

---

## 🎯 下一步

1. ✅ 选择一个集成方法（推荐方法 1）
2. ✅ 复制 `.cursorrules` 到你的项目
3. ✅ 测试一篇文章验证效果
4. ✅ 根据需要调整和优化规则
5. ✅ 开始高效创作！

祝你写作愉快！🚀
