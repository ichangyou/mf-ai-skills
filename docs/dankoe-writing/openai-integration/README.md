# Dan Koe 写作风格 - OpenAI API 集成包

## 📦 包含内容

这个集成包提供了多种方式来使用 OpenAI API 生成 Dan Koe 风格的文章：

```
openai-integration/
├── README.md                          # 本文件
├── multi-platform-guide.md            # 多平台集成完整指南
├── .github/
│   └── copilot-instructions.md        # GitHub Copilot 配置
└── examples/
    ├── python/
    │   └── write_article.py           # Python 实现
    ├── nodejs/
    │   ├── write_article.js           # Node.js 实现
    │   └── package.json               # Node.js 依赖
    └── shell/
        └── write-article.sh           # Shell 脚本包装器
```

---

## 🚀 快速开始

### 前提条件

1. **OpenAI API Key**
   - 访问 https://platform.openai.com/api-keys
   - 创建一个新的 API key
   - 将 key 保存到环境变量

2. **安装依赖**
   - Python: `pip install openai`
   - Node.js: `npm install openai`

### 方法 1：使用 Python（推荐）

```bash
# 设置 API Key
export OPENAI_API_KEY='your-api-key-here'

# 运行脚本
python examples/python/write_article.py "时间管理的真相" "changyou"
```

### 方法 2：使用 Node.js

```bash
# 设置 API Key
export OPENAI_API_KEY='your-api-key-here'

# 安装依赖
cd examples/nodejs
npm install

# 运行脚本
node write_article.js "个人成长的误区" "changyou"
```

### 方法 3：使用 Shell 脚本（最简单）

```bash
# 设置 API Key
export OPENAI_API_KEY='your-api-key-here'

# 赋予执行权限
chmod +x examples/shell/write-article.sh

# 运行
./examples/shell/write-article.sh "创业者的困境" "changyou" "北京" "260204 150000"
```

---

## 📖 详细使用说明

### Python 版本

#### 基础使用

```bash
python write_article.py "文章话题"
```

#### 完整参数

```bash
python write_article.py "话题" "作者" "地点" "时间"
```

#### 示例

```bash
# 最简单
python write_article.py "为什么大多数人的学习方法都是错的"

# 指定作者
python write_article.py "个人品牌建设" "changyou"

# 完整参数
python write_article.py "创作者经济" "changyou" "上海" "260204 150000"
```

#### 环境变量

```bash
# 必需
export OPENAI_API_KEY='your-api-key-here'

# 可选 - 指定模型
export OPENAI_MODEL='gpt-4-turbo'  # 或 gpt-3.5-turbo
```

#### 在代码中使用

```python
from write_article import write_article

# 生成文章
article = write_article(
    topic="时间管理的真相",
    author="changyou",
    location="北京",
    timestamp="260204 150000",
    model="gpt-4"
)

print(article)
```

### Node.js 版本

#### 基础使用

```bash
node write_article.js "文章话题"
```

#### 完整参数

```bash
node write_article.js "话题" "作者" "地点" "时间"
```

#### 在代码中使用

```javascript
import { writeArticle } from './write_article.js';

// 生成文章
const article = await writeArticle(
  '个人成长的误区',
  'changyou',
  '深圳',
  '260204 150000',
  'gpt-4'
);

console.log(article);
```

---

## 🎯 集成到你的项目

### 作为 Python 模块

```python
# 将 write_article.py 复制到你的项目
import sys
sys.path.append('./path/to/examples/python')

from write_article import write_article

# 使用
article = write_article("你的话题", "作者名")
```

### 作为 Node.js 模块

```javascript
// 将 write_article.js 复制到你的项目
import { writeArticle } from './path/to/examples/nodejs/write_article.js';

// 使用
const article = await writeArticle('你的话题', '作者名');
```

### 作为 CLI 工具

```bash
# 添加到 PATH
export PATH="$PATH:/path/to/examples/shell"

# 在任何地方使用
write-article.sh "文章话题" "作者名"
```

---

## 🔧 高级配置

### 自定义 System Prompt

编辑 `write_article.py` 或 `write_article.js` 中的 `DANKOE_SYSTEM_PROMPT` 变量：

```python
DANKOE_SYSTEM_PROMPT = """
你是一位深度思考者和写作者...
[在这里修改或扩展 prompt]
"""
```

### 调整生成参数

```python
response = client.chat.completions.create(
    model="gpt-4",
    temperature=0.7,      # 创造性 (0-2, 越高越有创意)
    max_tokens=3000,      # 最大输出长度
    top_p=1.0,            # 核采样 (0-1)
    frequency_penalty=0.3,  # 重复惩罚 (0-2)
    presence_penalty=0.3    # 话题多样性 (0-2)
)
```

### 批量生成

创建 `batch_generate.py`：

```python
from write_article import write_article

topics = [
    "时间管理的真相",
    "个人品牌建设",
    "创作者经济",
    "学习方法论",
    "注意力管理"
]

for topic in topics:
    print(f"正在生成: {topic}")
    article = write_article(topic, "changyou")
    
    # 保存到文件
    filename = f"{topic}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article)
    
    print(f"已保存: {filename}\n")
```

---

## 💰 成本估算

### Token 使用

- **System Prompt**: ~500 tokens
- **User Prompt**: ~200 tokens
- **输出文章**: ~1500-2000 tokens
- **单篇文章总计**: ~2200-2700 tokens

### 价格参考（截至 2024）

| 模型 | Input (每 1M tokens) | Output (每 1M tokens) | 单篇成本 |
|------|---------------------|----------------------|---------|
| GPT-4 | $30 | $60 | ~$0.15-0.20 |
| GPT-3.5 Turbo | $1.5 | $2 | ~$0.005-0.008 |

> 💡 提示：使用 GPT-3.5 Turbo 进行测试，确认效果后再使用 GPT-4

---

## 📊 输出示例

生成的文章将包含：

```markdown
# 为什么大多数人的时间管理都是错的

作者: changyou
生成时间: 2026-02-04 15:00:00

---

你以为你在管理时间。

实际上，你只是在假装自己很忙。

这不是你的错。传统的时间管理理论从一开始就错了...

一、时间管理的最大谎言

[深度内容...]

二、你真正需要管理的不是时间

[深度内容...]

三、从时间管理到注意力管理的范式转变

[深度内容...]

[...更多章节...]

实践协议：

第一步：...
第二步：...
第三步：...

– changyou
```

---

## 🐛 故障排除

### 问题 1：API Key 无效

```bash
❌ 错误: Incorrect API key provided
```

**解决方案**：
1. 检查 API Key 是否正确
2. 确认已设置环境变量：`echo $OPENAI_API_KEY`
3. 重新导出：`export OPENAI_API_KEY='your-key'`

### 问题 2：模块未找到

```bash
❌ 错误: ModuleNotFoundError: No module named 'openai'
```

**解决方案**：
```bash
pip install openai --break-system-packages
# 或
pip3 install openai
```

### 问题 3：Token 超限

```bash
❌ 错误: Rate limit exceeded
```

**解决方案**：
1. 等待片刻后重试
2. 检查账户配额
3. 考虑升级到付费计划

### 问题 4：输出不符合预期

**解决方案**：
1. 调整 `temperature` 参数（0.5-0.9 之间）
2. 修改 System Prompt 更明确地指定要求
3. 在 User Prompt 中添加更多细节

---

## 🔄 集成到其他平台

### Cursor

将 Python 脚本集成到 Cursor：

1. 复制 `examples/python/write_article.py` 到项目
2. 在 Cursor 中创建 Task：
   ```python
   import subprocess
   result = subprocess.run(
       ['python', 'write_article.py', topic],
       capture_output=True,
       text=True
   )
   ```

### VS Code

创建 VS Code Task (`.vscode/tasks.json`):

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate Dan Koe Article",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}/examples/python/write_article.py",
        "${input:topic}",
        "${input:author}"
      ],
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "topic",
      "type": "promptString",
      "description": "文章话题"
    },
    {
      "id": "author",
      "type": "promptString",
      "description": "作者名字",
      "default": "changyou"
    }
  ]
}
```

### Web 应用

使用 Flask 创建简单 Web 界面：

```python
from flask import Flask, request, jsonify
from write_article import write_article

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    article = write_article(
        topic=data['topic'],
        author=data.get('author', 'changyou'),
        location=data.get('location', ''),
        timestamp=data.get('timestamp', '')
    )
    return jsonify({'article': article})

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 📚 更多资源

- **完整集成指南**: 查看 `multi-platform-guide.md`
- **GitHub Copilot 配置**: 查看 `.github/copilot-instructions.md`
- **Cursor 集成**: 参考 Cursor 集成包
- **Claude.ai 集成**: 使用 `dankoe-writing.skill` 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- 写作风格灵感来源于 Dan Koe
- 基于 OpenAI GPT-4 实现

---

## 📞 支持

如有问题，请：
1. 查看本 README 的故障排除部分
2. 查看 `multi-platform-guide.md` 获取更多信息
3. 在 GitHub 上提交 Issue

祝写作愉快！🎉
