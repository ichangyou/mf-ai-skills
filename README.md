# mf-ai-skills

沐风（Joey）的开源 AI skill 集合，共 16 个，支持 **Codex 和 Claude Code**。
覆盖写作与发布、阅读与复盘、思考与决策、iOS 工程和研究分析。两端共用 `skills/` 中的同一份内容。
生图、账号数据和发布需要额外配置工具与凭据。

## 快速安装

需要 Git 和 Python 3.10+。默认同时安装到两端的用户目录，不覆盖已有同名 skill：

```bash
git clone https://github.com/ichangyou/mf-ai-skills.git
cd mf-ai-skills
python3 scripts/install.py --platform both --scope user
```

默认使用软链接，保留仓库即可通过 `git pull` 更新。Windows 或不支持软链接时加 `--mode copy`。
只安装一个 skill：

```bash
python3 scripts/install.py --platform both --skill mufeng-book-notes
```

项目级安装、冲突处理、更新与卸载见 [安装文档](docs/installation.md)。当前采用直接安装方式，没有 Claude Code marketplace。

## 怎么调用

| Codex | Claude Code |
|---|---|
| `$mufeng-book-notes 根据这份摘录生成读书笔记` | `/mufeng-book-notes 根据这份摘录生成读书笔记` |

也可用自然语言明确要求使用 skill。安装后未出现时，重新加载 skills 或重启客户端。

## 有哪些 skill，需要什么依赖

下表列的是执行条件，不表示外部服务已经完成端到端验证。详细示例见各 skill 的使用说明。

| 场景 | Skill / 使用说明 | 用途 | 额外依赖 |
|---|---|---|---|
| 写作 | [mufeng-blog-writing](skills/mufeng-blog-writing/README.md) | 技术博客、教程和排错文章 | 素材；核实事实时需网络检索 |
| 写作 | [mufeng-dankoe-writing](skills/mufeng-dankoe-writing/README.md) | Dan Koe 风格长篇写作 | 无专用工具 |
| 发布 | [mufeng-wechat-publish-full](skills/mufeng-wechat-publish-full/README.md) | 完成文章的配图、上传和公众号发布 | 生图工具、gh、Bun、发布工具与凭据 |
| 发布 | [mufeng-materials-to-wechat-publish](skills/mufeng-materials-to-wechat-publish/README.md) | 目录素材转公众号文章 | 博客 skill、网络检索；生图和发布依赖同上 |
| 绘本 | [mufeng-bilingual-storybook](skills/mufeng-bilingual-storybook/README.md) | 中英文插画绘本与 PDF | Python、Pillow、pypdfium2、生图/视觉工具；默认 PDF 字体需 macOS |
| 阅读 | [mufeng-book-notes](skills/mufeng-book-notes/README.md) | 可落地的读书笔记 | 真实摘录或读书材料 |
| 阅读 | [mufeng-weread-x-writing](skills/mufeng-weread-x-writing/README.md) | 阅读记录提炼原创 X 推文 | Python；微信读书工具或真实导出材料 |
| 复盘 | [mufeng-weekly-report](skills/mufeng-weekly-report/README.md) | 周报与行动建议 | 当前对话或用户提供的周记录 |
| 复盘 | [mufeng-monthly-report](skills/mufeng-monthly-report/README.md) | 月度趋势与行动计划 | 当前对话或用户提供的月记录 |
| 思考 | [mufeng-brainstorm](skills/mufeng-brainstorm/README.md) | 发散、筛选和反驳 | 子代理可选；缺少时注明顺序检查 |
| 思考 | [mufeng-virtual-team](skills/mufeng-virtual-team/README.md) | CTO / 产品 / 用户多视角评审 | 功能描述与项目背景 |
| 设计 | [mufeng-uxreview](skills/mufeng-uxreview/README.md) | UI/UX 评审 | 页面代码，必要时提供截图 |
| iOS | [mufeng-ios-release-audit](skills/mufeng-ios-release-audit/README.md) | 上线审计与上线文案 | iOS 项目；编译需 macOS + Xcode |
| iOS | [mufeng-ios-visual-regression](skills/mufeng-ios-visual-regression/README.md) | 多语言与明暗截图对比 | macOS + Xcode + Simulator、Python、Pillow、应用 harness |
| 调试 | [mufeng-parallel-root-cause](skills/mufeng-parallel-root-cause/README.md) | 证伪式根因调查 | 日志和实验工具；并行需子代理 |
| 研究 | [mufeng-stock-research](skills/mufeng-stock-research/README.md) | 股票研究与报告导出 | 网络检索；MCP 可选；导出需 Pandoc，PDF 需 Chrome/Chromium |

生图、发布、阅读数据和历史会话的配置与限制，见 [兼容性文档](docs/compatibility.md)。

## 目录与维护

```text
skills/<name>/             # 唯一内容来源
  SKILL.md                 # AI 执行说明与元数据
  README.md                # 用户使用说明
  references/              # 详细规则（可选）
  scripts/                 # 辅助脚本（可选）
  assets/                  # 图片、模板（可选）
  agents/openai.yaml       # Codex UI 元数据（可选）
.agents/skills/<name>      # Codex 项目入口 → skills/<name>
.claude/skills/<name>      # Claude Code 项目入口 → skills/<name>
docs/                     # 安装和兼容性说明
scripts/                  # 安装、校验和打包工具
examples/                 # 可选 API 示例和历史格式
tests/                    # 安装与兼容性回归测试
```

开发检查：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m unittest discover -s skills/mufeng-bilingual-storybook/tests -v
```

Windows 使用 `.venv\Scripts\python.exe`。绘本 PDF 测试使用 macOS 默认字体。
校验覆盖元数据、两端入口、目录索引和本地链接；业务效果与外部服务需要真实环境验证。
贡献约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT © Chang You，见 [LICENSE](LICENSE)。
