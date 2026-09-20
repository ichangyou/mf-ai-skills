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
