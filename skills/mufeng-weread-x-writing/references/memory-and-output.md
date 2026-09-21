# 历史记忆与输出格式

## 历史记录格式

`history.jsonl` 每行一个 JSON 对象，UTF-8 编码。建议字段：

```json
{
  "id": "20260919T103000-01",
  "created_at": "2026-09-19T10:30:00+08:00",
  "status": "generated",
  "text": "推文正文",
  "insight": "观点指纹：一句最短的核心结论",
  "topics": ["注意力", "学习"],
  "source_books": ["专注的真相"],
  "source_materials": ["个人评论：对素材的短摘要"],
  "structure": "微型思考",
  "keywords": ["时间", "注意力", "复利"]
}
```

约束：

- `status` 可为 `generated`、`saved` 或 `published`；新候选默认为 `generated`。
- `created_at` 必须带时区。
- `insight` 写核心结论，不复制正文。
- `source_materials` 只存足以识别素材的摘要，不保存大段书籍原文。
- 未知字段用空数组或省略，不编造。
- 对正文完全相同的记录，脚本会拒绝重复追加。

写入一条记录：

```bash
python3 /Users/changyou/.agents/skills/mufeng-weread-x-writing/scripts/history.py add --json '{"text":"...","insight":"...","topics":["学习"]}'
```

也可以从标准输入传入单个对象或对象数组：

```bash
python3 /Users/changyou/.agents/skills/mufeng-weread-x-writing/scripts/history.py add < records.json
```

## 语义去重对象

比较历史时依次看：

1. `insight`：思想是否相同。
2. `source_materials`：是否复用了同一划线、评论或案例。
3. `topics`：最近是否主题过密。
4. `structure`：表达骨架是否重复。
5. `text`：是否只是调序、缩写或同义替换。

不要把关键词重合直接判为思想重复；也不要因为文字不同就忽略观点重复。

## 最终展示格式

每条之间留空行：

```text
1

推文正文

来源：书名 / 我的笔记 / 我的评论
核心主题：注意力 / 学习 / 人生 / 商业 / 哲思等
新鲜度：高 / 中
与最近 30 天历史内容：无明显重复 / 有轻微关联

2

……

今日最值得发布的 2 条

- 第 X 条：主题。简短说明质量最高的原因。
- 第 Y 条：主题。简短说明质量最高的原因。
```

规则：

- 正文可以直接复制发布，来源等元信息不得写进正文。
- “新鲜度”综合考虑主题频率、观点新颖性和素材新近程度。
- “有轻微关联”只用于 30–50% 的可接受关联，并说明新增角度；更高相似度不应出现在结果中。
- 少于两条合格内容时，只指出实际值得发布的数量。

## Markdown 文件输出

每轮结果除了在终端展示，还要另存一份 Markdown 文件。落盘一律走 `scripts/save_output.py`：

```bash
python3 /Users/changyou/.agents/skills/mufeng-weread-x-writing/scripts/save_output.py --count 6 < body.md
```

标准输入接收正文区（编号推文 + 来源元信息 + 今日最值得发布的 2 条），脚本补文件头、选目录、防覆盖，回包 JSON 里的 `path` 就是终端要报的绝对路径。下面几节是脚本已实现的规则，供理解与核对，不需要手工复刻。

### 存放位置

取当前工作目录 `cwd`：

| 情况 | 落盘目录 |
|---|---|
| `cwd` 等于 `/` 或等于 `$HOME` | `~/Downloads/` |
| 其余任何目录 | `cwd` 本身 |

判定只看 `cwd` 本身，不要求目录里存在 `.git`、`package.json`、`pyproject.toml` 之类的项目标志。用户本轮明确指定了路径时，以用户指定的为准。

### 文件名

`weread-x-YYYY-MM-DD.md`，日期取本地当天。目标文件已存在时依次尝试 `weread-x-YYYY-MM-DD-2.md`、`-3.md`，直到找到未占用的名字。任何情况下都不覆盖已有文件。

### 文件骨架

正文区与上面「最终展示格式」完全一致，只在顶部多一个文件头：

```markdown
# 微信读书推文候选 YYYY-MM-DD

生成时间：YYYY-MM-DD HH:MM（+08:00）
本轮候选：N 条 · 状态：generated（未发布）

---

1

推文正文

来源：书名 / 我的笔记 / 我的评论
核心主题：注意力 / 学习 / 人生 / 商业 / 哲思等
新鲜度：高 / 中
与最近 30 天历史内容：无明显重复 / 有轻微关联

2

……

---

## 今日最值得发布的 2 条

- 第 X 条：主题。简短说明质量最高的原因。
- 第 Y 条：主题。简短说明质量最高的原因。
```

### 与终端输出的关系

- 终端仍打印全部正文，不因为已落盘而改成摘要。
- 终端末尾补一行「已保存到 `<绝对路径>`」，给绝对路径而不是相对路径。
- 写盘失败时照常输出全文，并说明未保存及原因。
- 这份 Markdown 不替代 `history.jsonl`；历史仍按本文件开头的规则单独写入，路径不随 `cwd` 变化。
