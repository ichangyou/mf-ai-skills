# 数据源、评分规则与报告模板

## 1. 数据源与已验证限制

以下结论在 2026-10-15 实测得到。苹果可能随时调整接口，脚本出错时先用 `curl -v` 复查。

| 数据 | 接口 | 限制 |
|---|---|---|
| 分类榜单 | `itunes.apple.com/{cc}/rss/{topfreeapplications\|toppaidapplications\|topgrossingapplications}/limit=N/genre=G/json` | 每个榜单最多约 100 条；`limit=200` 也只返回 100 |
| 应用详情 | `itunes.apple.com/lookup?id=a,b,c&country=cc` | 支持逗号分隔批量查询；字段含评分、评分数、价格、更新时间、图标、截图、描述 |
| 关键词搜索 | `itunes.apple.com/search?term=..&entity=software&country=cc` | 返回顺序近似商店搜索排序，但不保证一致；没有搜索热度 |
| 评论 | `itunes.apple.com/{cc}/rss/customerreviews/page=P/id=X/sortby={mostrecent\|mosthelpful}/json` | 每页 50 条，最多 10 页（第 11 页返回 400），所以每个排序最多 500 条 |

拿不到的数据：
- 下载量、收入：苹果不公开。只能用评分数和畅销榜位置作代理。
- 关键词搜索热度：只在 Apple Search Ads 后台可见。
- 竞品的 App Store Connect 数据：ASC API 只能查自己的应用。
- 新版 RSS（`rss.marketingtools.apple.com`）不支持按分类筛选，脚本不使用它。

## 2. 分类 ID（iOS，已逐个实测）

| ID | 分类 | ID | 分类 | ID | 分类 |
|---|---|---|---|---|---|
| 6000 | Business 商务 | 6009 | News 新闻 | 6017 | Education 教育 |
| 6001 | Weather 天气 | 6010 | Navigation 导航 | 6018 | Books 图书 |
| 6002 | Utilities 工具 | 6011 | Music 音乐 | 6020 | Medical 医疗 |
| 6003 | Travel 旅游 | 6012 | Lifestyle 生活 | 6023 | Food & Drink 美食佳饮 |
| 6004 | Sports 体育 | 6013 | Health & Fitness 健康健美 | 6024 | Shopping 购物 |
| 6005 | Social Networking 社交 | 6014 | Games 游戏 | 6026 | Developer Tools 开发者工具 |
| 6006 | Reference 参考 | 6015 | Finance 财务 | 6027 | Graphics & Design 图形和设计 |
| 6007 | Productivity 效率 | 6016 | Entertainment 娱乐 | | |
| 6008 | Photo & Video 摄影与录像 | | | | |

不可用：6021（返回混杂分类）、6022 与 6025（空榜单）。

常用地区代码：`us` 美国、`cn` 中国、`jp` 日本、`gb` 英国、`de` 德国、`kr` 韩国、`tw` 台湾、`hk` 香港。

## 3. 评分规则（启发式，不是统计模型）

### 应用弱势度 weakness（0–1）

```
rating_gap = clip((4.6 − rating) / 1.1)        # 评分 3.5 及以下记满分；评分数 < 20 时记 0
staleness  = clip((days_since_update − 180) / 545)   # 半年内更新记 0，两年未更新记满分
weakness   = 0.6 × rating_gap + 0.4 × staleness
```

weakness ≥ 0.35 视为"弱势在位者"。

### 应用标记

| 标记 | 条件 | 含义 |
|---|---|---|
| weak_monetizer 弱势但赚钱 | 在畅销榜，且 weakness ≥ 0.35 | 用户愿意付钱但产品不好，最值得研究 |
| small_monetizer 小体量但赚钱 | 在畅销榜，且评分数 < 5000 | 小团队也能进畅销榜的信号 |
| stale_leader 头部久未更新 | 任一榜单前 25，且超过 365 天未更新 | 头部松动 |
| low_rated_leader 头部低评分 | 任一榜单前 50，评分 < 4.0，评分数 ≥ 100 | 用户被迫使用、普遍不满 |

### 分类机会分（0–100）

```
competition = 100 × clip((log10(免费榜前25评分数中位数) − 2) / 4)   # 100 → 0，100 万 → 100
opportunity = 0.35 × (100 − competition)
            + 25 × 畅销榜第51–100名中弱势应用占比
            + 25 × 畅销榜第51–100名中小体量应用占比
            + 15 × 免费榜前50中上架不满一年的应用占比
```

为什么只统计畅销榜尾部：2026-10-15 美区实测，效率类和健康类畅销榜前 50 名的评分数中位数为 7 万–49 万，评分数 < 5000 的应用仅 0–1 个；第 51–100 名中有 7–15 个。用前 50 名统计时，两个分类的弱势占比和小体量占比都接近 0，指标失去区分度。畅销榜不足 51 条时退回全榜统计。

### 关键词机会分（0–100）

```
demand      = 100 × clip((log10(前10中第3高的评分数) − 2) / 5)   # 100 → 0，1000 万 → 100；不足 3 个结果时取最小值
competition = 100 × clip((log10(前10评分数中位数) − 1) / 4)
opportunity = 0.3 × demand + 0.3 × (100 − competition) + 25 × 前10弱势占比 + 15 × 前10新进入者占比
```

为什么用第 3 高而不是最大值：2026-10-15 美区天气类实测，The Weather Channel（约 608 万评分）出现在 weather radar、hurricane tracker、lightning tracker 三个词的前 10 名中，用最大值时三个词的需求度都是 100。第 3 高值反映"有几个应用靠这个词活着"。原上限 100 万也会让大分类饱和，所以提高到 1000 万。

### 已知偏差

- 评分数受"应用年龄"和"评分弹窗策略"影响很大，不等于下载量。
- 畅销榜包含订阅和内购，被大公司应用占满时，小应用的占比会被低估。
- 最近评论偏向新版本问题；用 `--sort mosthelpful` 补充长期痛点。
- 机会分只用于排序和筛选候选方向，不能直接作为立项结论。

## 4. 差评聚类规则

1. 每个目标应用至少取 `mostrecent` 与 `mosthelpful` 两种排序的 1–2 星评论。
   `reviews` 输出字段：顶层 `id`、`name`、`rating`（应用店面均分）、`ratings`（评分数）、`sort`、`summary`、`reviews`；
   每条评论为 `stars`（1–5 星，注意不是 `rating`）、`title`、`content`、`version`、`date`、`votes`。
   `summary` 含 `total`、`distribution`、`low_share`（1–2 星占比）和 `date_range`（样本最早与最晚日期）。
   `mosthelpful` 会带回多年前的评论：先看 `date_range`，报告中区分近期问题与历史问题。
2. 按"用户想做什么但做不到"归类，不按情绪归类。例如"同步丢数据"是一类，"太贵"是一类，"广告多"是一类。
3. 每类写：主题、条数、2–3 条原文引用（保留原语言）。
4. 只出现 1 次的问题不单独成类，放进"其他"。
5. 区分"可被新产品解决的需求"和"只有原厂能解决的问题"（例如账号封禁、平台政策）。后者不算机会。

写入 `pains.json`：

```json
[{"app_id": "123", "app_name": "Foo", "themes": [{"theme": "iCloud 同步丢数据", "count": 14, "quotes": ["..."]}]}]
```

## 5. 报告模板（markdown）

```markdown
# App 机会分析：{地区} / {分类或关键词}（{日期}）

## 结论
- 推荐方向 1–3 个，每个一句话：做什么 + 为谁 + 为什么现在能进。
- 每个方向标注置信度（高/中/低）与最大风险。

## 数据范围
地区、分类、关键词、抓取时间、样本量、无法获取的数据。

## 分类 / 关键词对比
表格：机会分、竞争度、需求度、弱势占比、小体量占比。

## 值得研究的在位者
表格：应用、评分、评分数、更新时间、榜单位置、标记。

## 用户诟病点
按应用列出主题、条数、原文引用，并标注"新产品可解决 / 不可解决"。

## 推荐方向的详细论证
每个方向：目标用户、核心功能（只针对诟病点）、差异化、变现方式（参考畅销榜同类定价）、
获取曝光的关键词、主要风险、下一步验证动作。

## 限制
列出代理指标的偏差与未验证项。
```
