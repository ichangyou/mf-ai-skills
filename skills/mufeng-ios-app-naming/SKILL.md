---
name: mufeng-ios-app-naming
description: >-
  Generate and clear names for an iOS/macOS app: brainstorm candidates, then screen each through a
  five-step check (App Store name collisions, USPTO and TMview trademarks in classes 9/42/45, RDAP
  domain registration, what is actually live on registered domains, web search), review false
  positives, check sound-alike variants of finalists and recommend one name with a weighted score.
  Triggers: 给 App 起名、App 取名、英文名、产品名、品牌名、名字查重、商标查重、域名查重、
  这个名字能不能用、app naming, name my app, brand name check, trademark clearance, is this name taken.
  Not legal advice; does not register domains or file trademarks.
metadata:
  version: "1.0.0"
compatibility: "Codex and Claude Code. Python 3.9+ (stdlib only) with network access to itunes.apple.com, tmsearch.uspto.gov, www.tmdn.org and RDAP servers; web search tool for step 5. Japan (J-PlatPat) is manual."
---

# iOS App 起名与查重

## 资源路径

运行命令前，把 shell 变量 `SKILL_DIR` 设为**当前加载的** `SKILL.md` 所在目录。脚本从这个目录定位，不使用工作目录或固定安装路径。

```bash
NC="python3 $SKILL_DIR/scripts/namecheck.py"
```

工作目录：在当前项目下创建 `naming/<YYYYMMDD>-<主题>/`，记为 `$WORK`，所有 JSON 都存放在这里。

## 必须遵守的边界

开始前读 [references/method.md](references/method.md) 的第 1 节和第 7 节。

- 结论是筛查结果和经验判断，**不是法律意见**。最终回复里必须建议用户请商标代理人确认。
- 只能写「在某个数据源、某个范围内没有找到」，不能写「不存在」或「可以放心用」。
- 每条信息都标注来源类型：**实查**（脚本或检索的原始结果）、**知识**（凭知识判断，未核实）、**推测**。
- 不注册域名，不提交商标申请，不在 App Store Connect 占名。这些都列为用户的待办。

## 工作流

### 0. 明确输入

从对话或项目文档（PRD、竞品分析）里确定以下几项：
- 产品是什么、属于什么品类。
- 目标市场和语言：默认是全球市场，8 种语言（英、简中、繁中、日、韩、德、法、西）。
- 风格：例如更短、更有科技感，或者平静克制。
- 用户已经否决的名字。

只有当某项缺失、而且会显著改变结果时才问用户；否则使用默认值，并在报告里写明。

### 1. 生成候选名

按 method.md 第 2、3 节生成 20–40 个候选名，并按风格分组。生成时就先剔除常识范围内的知名品牌，以及和知名品牌只差一个字母的名字（标注为「知识」）。

### 2. 脚本筛查（五步中的前四步）

```bash
$NC screen --names "Kypra,Arcella,Tacere" --out "$WORK"
```

可选参数：
- `--stores us,jp,mac-us`：可以加 `cn`、`kr`、`de`。
- `--tlds app,com`：可以加 `dev`。
- `--classes 9,42,45`：冲突类别。
- `--tmview-pages 3`。

脚本会依次做四件事：
1. 查 App Store。
2. 查 USPTO 和 TMview 商标库。
3. 查域名注册状态（先用随机域名做 RDAP 自检）。
4. 抓取已注册域名上网站的标题和描述。

每个名字输出 `PASS`、`REVIEW` 或 `FAIL`，以及原因，完整结果写入 `$WORK/screen.json`。30 个名字大约需要 10–15 分钟，可以放到后台运行。

### 3. 人工复核

按 method.md 第 5 节，逐条复核 `REVIEW` 和 `FAIL` 的原因：
- 「仅包含」匹配（例如 MARCELLA 之于 Arcella）属于误杀，改判通过，但要列出来。
- 对有疑问的商标，运行下面的命令查看对方的商品描述。出现 authentication、identity、security、password 等字样即为直接冲突。

```bash
$NC marks --name Tacit --out "$WORK"
```

`marks` 只能显示**美国商标**的商品描述，因为 TMview 的结果里不包含这部分内容。其他地区的商标只会列出编号，需要到对应商标局的官网按编号查看，例如澳大利亚用 `https://search.ipaustralia.gov.au/trademarks/search/view/<编号>`（编号取 ST13 末尾的数字）。宿主有网页抓取或浏览器工具时，直接打开查看；没有的话，列为用户待办。

### 4. 网页检索（第五步）

对通过的名字，用宿主自带的网页检索工具，各搜两次：「"名字" app OR software OR company」，以及「"名字" password OR security」。如果找到同名的安全类产品，排除该名字。宿主没有检索工具时，在报告里写明这一步没有完成。

### 5. 终选近似检查

挑出 2–3 个终选名，逐个运行：

```bash
$NC variants --name Kypra --out "$WORK"
```

默认自动生成 c/k、y/i、双写或单写辅音等变体，也可以用 `--variants "Cypra,Kipra"` 手动补充读音近似的变体。如果宿主有浏览器工具，就用 J-PlatPat 查日本；没有的话，把它列为用户待办。

### 6. 加权评估

按 method.md 第 6 节的五个维度打分，算出加权得分，给出唯一推荐和一个备选。每项分数都要写明依据。主域名能否注册、近似商标、读音风险，都要引用实查结果。

### 7. 报告

按 method.md 第 8 节的模板写 markdown 报告：用户指定了位置就用用户的；没有指定时，项目里已有命名文档就追加进去，否则保存为 `~/Desktop/naming-<主题>-<YYYYMMDD>.md`。

### 8. 回复用户

终端里只给这几项：
- 推荐的名字和备选，加上加权得分。
- 决定性证据，附数据源。
- 主要风险和应对办法。
- 用户待办：注册域名、在 App Store Connect 试占名称、用 J-PlatPat 查日本、请商标代理人出具意见。
- 报告路径，以及没有完成的检查。

## 故障处理

- 出现 `HTTP 0` 或 SSL EOF：脚本会自动重试；仍然失败的，记入 `errors`，名字判为 REVIEW，不要当作通过。
- RDAP 自检失败：域名结果不可信，脚本会跳过域名检查。不要改用 whois。
- 接口结构变了，导致解析为空：用 `curl -v` 打一次原始请求，贴出响应，再修改脚本里的 `parse_*` 函数，并补上测试。
- 不要为了绕过限流去修改代理或系统配置。
