# 沐风 · iOS 需求挖掘（mufeng-ios-app-opportunity）

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

用 App Store 公开数据挖需求：找出热门应用被用户诟病的地方，比较不同分类和关键词的竞争强度，给出更容易获得曝光和收入的开发方向，并附上证据。

## 调用

Codex：

```text
$mufeng-ios-app-opportunity 帮我看美区效率类和健康类有什么机会
```

Claude Code：

```text
/mufeng-ios-app-opportunity 帮我看美区效率类和健康类有什么机会
```

也可以直接分析竞品：`/mufeng-ios-app-opportunity 分析习惯追踪类应用的差评，中国区`。

## 依赖与执行范围

- Python 3.10+，只用标准库，不需要安装依赖。
- 能访问 `itunes.apple.com`。不需要苹果账号或 API Key。
- 看图标和截图需要宿主支持读取图片；不支持时跳过这一步。

“支持”表示提供两端入口和执行说明；外部服务、账号认证及工具能力需单独配置。实际执行规则见 [SKILL.md](SKILL.md)。

## 能拿到 / 拿不到的数据

| 能拿到 | 拿不到 |
|---|---|
| 分类免费榜、付费榜、畅销榜（各约 100 条） | 下载量、收入（苹果不公开） |
| 评分、评分数、价格、更新时间、图标、截图 | 关键词搜索热度（仅 Apple Search Ads 后台） |
| 关键词搜索结果 | 竞品的 App Store Connect 数据 |
| 每个应用最近或最有用的评论，各最多 500 条 | 超过 500 条的历史评论 |

所以评分数和畅销榜位置只是代理指标。评分规则和偏差见 [references/method.md](references/method.md)。

## 输出

- 工作目录 `app-opportunity/<日期>-<地区>-<主题>/`：原始 JSON、`scores.json`、`pains.json`、图标截图、`report.html`。
- `report.html`：分类对比表、评分数 × 评分散点图（可切换分类、只看畅销榜）、关键词表、被标记应用、用户诟病点。
- markdown 结论报告：默认保存到 `~/Desktop`。

## 单独使用脚本

```bash
python3 scripts/asdata.py scan --country us --genres 6007 --out work
python3 scripts/asdata.py keyword --country us --terms "habit tracker" --out work
python3 scripts/score.py work
python3 scripts/report_html.py work
open work/report.html
```

## 测试

```bash
python3 -m unittest discover -s skills/mufeng-ios-app-opportunity/tests -v
```

测试使用离线样例数据，不访问网络。
