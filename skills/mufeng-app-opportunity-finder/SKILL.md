---
name: mufeng-app-opportunity-finder
description: >-
  Mine App Store public data (category charts, app details, ratings, icons, screenshots,
  keyword search results and 1-2 star reviews) to find what users complain about in popular
  apps and which categories or keywords have weaker competition, then recommend app ideas
  with evidence. Triggers: 挖需求、找 App 方向、App Store 机会、哪个分类竞争小、竞品差评、
  用户吐槽什么、独立开发做什么、app idea research, app store opportunity, competitor reviews.
  Not for optimizing an existing app's own listing (use ASO skills) or for real download/revenue numbers.
metadata:
  version: "1.0.0"
compatibility: "Codex and Claude Code. Python 3.10+ (stdlib only) and network access to itunes.apple.com; image viewing is optional for icon/screenshot review."
---

# App Store 需求挖掘与机会评估

## 资源路径

运行命令前，把 shell 变量 `SKILL_DIR` 设为**当前加载的** `SKILL.md` 所在目录。所有脚本从这个目录定位，不使用工作目录或固定安装路径。

```bash
AOF="python3 $SKILL_DIR/scripts/asdata.py"
```

工作目录：在当前项目下创建 `app-opportunity/<YYYYMMDD>-<地区>-<主题>/`，所有中间数据放在这里。缓存在 `~/.cache/mufeng-app-opportunity-finder`（可用环境变量 `MUFENG_AOF_CACHE` 改），24 小时有效。

## 必须先说清的边界

开始前读 [references/method.md](references/method.md) 第 1 节。对用户的任何结论都必须遵守：

- 没有下载量和收入数据。评分数是用户规模的代理，畅销榜位置是收入的代理。说"约""代理"，不说"下载了 X 次""月收入 X"。
- 没有关键词搜索热度。需求度是"该词前 10 名中第 3 高的评分数"的代理。
- 机会分是启发式排序，只用来筛选候选方向，不是立项结论。
- 区分事实（接口原始数据）、推测（由代理指标推出）和判断（你的建议）。

## 工作流

### 0. 明确范围

从用户请求里确定：地区（默认 `us`；用户是中文市场时用 `cn`）、分类或关键词、目标（找方向 / 分析某个竞品 / 对比几个分类）。范围不清且会显著改变结果时再问；否则用默认值并在报告里写明。分类 ID 见 method.md 第 2 节。

用户没给分类时，默认扫独立开发者常见的分类：`6007,6013,6002,6012,6015,6017,6008,6027`。

### 1. 扫分类榜单

```bash
$AOF scan --country us --genres 6007,6013 --out "$WORK"
```

每个分类抓免费、付费、畅销三个榜单（各约 100 条），批量补全详情，写入 `$WORK/scan-<地区>-<分类>.json`。查看 stderr 的 WARNING，空榜单要在报告里说明。

### 2. 关键词验证（有候选方向后）

为每个候选方向列 3–8 个用户会搜的英文或中文关键词（按地区语言）：

```bash
$AOF keyword --country us --terms "habit tracker,water reminder,pomodoro" --out "$WORK"
```

### 3. 打分

```bash
python3 "$SKILL_DIR/scripts/score.py" "$WORK"
```

读终端摘要和 `$WORK/scores.json`。重点看 `flagged_apps` 里的 `weak_monetizer` 和 `small_monetizer`：前者说明用户愿意付钱但对现有产品不满，后者说明小体量也能赚钱。

### 4. 抓差评

从标记应用和关键词前 3 名中选 3–8 个目标应用，每个取两种排序：

```bash
$AOF reviews --country us --id <ID> --sort mostrecent  --max-stars 2 --out "$WORK/reviews/<ID>-recent.json"
$AOF reviews --country us --id <ID> --sort mosthelpful --max-stars 2 --out "$WORK/reviews/<ID>-helpful.json"
```

`summary.low_share` 是该样本中 1–2 星的比例。按 method.md 第 4 节聚类，写入 `$WORK/pains.json`。必须引用原文，不能编造或改写引用。

### 5. 看图标和截图（可选，宿主支持看图时）

```bash
$AOF assets --country us --ids <ID1>,<ID2> --out "$WORK/assets" --screens 3
```

查看下载的图片，评估：图标辨识度、截图是否讲清卖点、视觉是否过时。只写你实际看到的内容。

### 6. 生成报告

```bash
python3 "$SKILL_DIR/scripts/report_html.py" "$WORK"
```

生成 `$WORK/report.html`（分类表、评分散点图、关键词表、标记应用、诟病点）。再按 method.md 第 5 节模板写 markdown 结论报告：用户指定位置优先，未指定时保存到 `~/Desktop/app-opportunity-<地区>-<主题>-<YYYYMMDD>.md`。

### 7. 回复用户

终端里只给：推荐方向（1–3 个，带置信度和最大风险）、关键证据（数字 + 来源接口）、报告路径、HTML 打开方式（`open <path>`）、未能获取或未验证的数据。

## 判断原则

- 一个方向成立，至少要有两类证据：需求存在（大应用或畅销榜存在）+ 现有产品有可解决的缺陷（差评聚类）或竞争弱（低竞争度、小体量畅销、新进入者多）。
- 竞争度低但需求度也低，通常是"没人要"，不是机会。
- 差评集中在账号封禁、平台政策、内容版权等原厂专属问题时，不算新产品机会。
- 头部全是大公司（看 seller）的分类，即使机会分高也要降低置信度。
- 不确定时直接说不确定，并给出下一步验证动作（例如：做落地页测转化、用 Apple Search Ads 查热度）。

## 故障处理

- HTTP 403/429：脚本会自动退避重试；仍失败就降低并发、稍后再试，不要改代理或系统配置。
- 某个 ID lookup 不到：可能已下架或该地区不可用，记录在 `missing_lookup` 中，在报告里说明。
- 接口结构变化：用 `curl -v` 打一次原始请求，贴出响应，再改脚本。
