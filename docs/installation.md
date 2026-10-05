# 安装、更新与卸载

需要 Git、Python 3.10+ 和要使用的 Codex / Claude Code 客户端。安装脚本仅使用 Python 标准库，不需要 API Key，不修改客户端配置，也不安装外部工具。

## 用户级安装

在仓库根目录执行：

```bash
python3 scripts/install.py --platform both --scope user
```

| 平台 | 安装位置 | 作用范围 |
|---|---|---|
| Codex | `~/.agents/skills/<name>/` | 本机各项目 |
| Claude Code | `~/.claude/skills/<name>/` | 本机各项目 |

只安装某个平台或若干 skill：

```bash
python3 scripts/install.py --platform codex --skill mufeng-book-notes
python3 scripts/install.py --platform claude --skill mufeng-blog-writing --skill mufeng-materials-to-wechat-publish
```

素材发布还需 `mufeng-blog-writing`；安装器不隐式安装其他依赖。

## 项目级安装

```bash
python3 scripts/install.py --platform both --scope project --project /path/to/your-project
```

目标项目必须已经存在。省略 `--project` 时使用当前目录。入口分别位于目标项目的 `.agents/skills/` 和 `.claude/skills/`。
本仓库已提交指向 `skills/` 的相对链接，克隆后即可在本仓库发现 skills；不会自动让其他项目拥有这些 skills。

## 软链接、复制与冲突

默认 `--mode link`：仓库保持一份源码，安装目录引用它。保留仓库位置；移动后重新建立安装链接。
Windows 或无法创建目录软链接时使用 `--mode copy`：

```bash
python3 scripts/install.py --platform both --mode copy
python3 scripts/install.py --platform both --dry-run
```

第二条仅预览默认链接安装。复制模式不依赖原仓库位置，但更新需重新复制。
同名目录或指向其他位置的链接会在写入前报错，不覆盖、合并或删除已有 skill。同一源码的已有链接会被跳过，重复链接安装是幂等的。

## 验证

在 Codex 中通过 `/skills` 或 `$mufeng-book-notes` 选择，在 Claude Code 中通过 `/mufeng-book-notes` 调用。
未刷新时重新加载 skills 或重启。用真实摘录验证读书笔记等不依赖账号的工作流。
能发现 skill 不代表生图、微信读书或发布已配置；见 [兼容性说明](compatibility.md)。
仓库的 `python3 scripts/validate.py` 只做静态校验，需要先安装 `requirements-dev.txt`。

## 更新

链接模式：在源码仓库执行 `git pull`，再运行原安装命令补齐新增 skill。已删除 skill 的旧链接需核对后单独移除。
复制模式：先 `git pull`，将已安装的本仓库 skill 目录移到备份位置，再使用 `--mode copy` 安装。
存在本地修改时先比较差异，安装器不会覆盖它们。

## 卸载与旧入口迁移

只移除安装目录下确认属于本仓库的 `<name>` 条目。链接模式删除链接即可，不删除 `skills/` 源码。
先检查 `ls -ld ~/.agents/skills/mufeng-book-notes` 确认目标，再执行：

```bash
unlink ~/.agents/skills/mufeng-book-notes
```

Claude Code 使用 `~/.claude/skills/<name>`。复制模式先备份并确认内容，再自行删除该 skill 目录。
历史仓库级 `.codex/skills/` 已迁移为 `.agents/skills/`。个人旧安装请按本文重新安装，确认新入口可调用后再清理旧入口，避免重复。

## Marketplace 与官方依据

当前没有 marketplace 清单，不要将本仓库配置进 `extraKnownMarketplaces`。未来提供市场发布时会补齐清单与命名空间说明。

- [Codex 加载位置与调用](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Claude Code marketplace 清单要求](https://code.claude.com/docs/en/plugin-marketplaces)
