---
name: mufeng-ios-release-audit
description: iOS App Store 上线前完整发布审计。逐项核验权限文案、托管 EULA/条款 URL 及违禁内容条款、硬编码价格、.lproj 本地化完整性、App 图标、版本号与 build 号、数据层强制解包、零编译警告、多语言商店元数据，并产出微信/X/Reddit 上线文案。触发词：iOS 要上线了、上线前检查、提交 App Store、会不会被拒、审核会过吗、iOS release 检查、发版前审查、iOS 发布审计、iOS release audit、生成上线文案。仅限 iOS/App Store 项目。
---

# iOS App Store 完整发布审计

对着代码库逐项核验，输出 pass/fail 表格。**全程只读，不改代码**——发现问题先报告根因和修复方案，等用户批准再动手。

## 来源

清单的每一项都来自真实事故或真实审查，不是通用最佳实践的罗列：

| 会话 | 项目 | 产出的教训 |
|---|---|---|
| 2026-07-09 | SpeechNote | **Guideline 3.1.2 反复拒审**：Terms 只是 App 内本地文本页，没有网址，导致商店页描述里没有可点 EULA 链接 |
| 2026-07-12 上午 | ShotZen | 上线前审查：版本号 1.1.1 与素材 1.2.0 不符；CoreData `fatalError` 启动崩溃隐患 |
| 2026-07-12 晚 | ShotZen | 商店文案四语；简中名称必须锁定备案名 |
| 2026-07-12 深夜 | ShotZen | 定价：`.lproj` 里 3 条硬编码旧价死字符串；静态截图印死价格风险 |
| — | Creem | 支付通道审核拒因：Terms 必须明确禁止 NSFW 内容——URL 可达不等于内容达标 |

## 前置

确认在 iOS repo 根目录（有 `*.xcodeproj`）。所有文件枚举**一律用 `git ls-files`**——`find` 会命中 `build/`、`.build/DerivedData/` 里的构建产物副本，导致同一语言重复统计、结果失真（已踩过）。

---

## 1. 权限说明文案

两种存放位置，**都要查**，查空了不等于 FAIL：

```bash
# (a) GENERATE_INFOPLIST_FILE = YES 的项目，文案在 pbxproj 里（ShotZen 是这种）
grep -oE "INFOPLIST_KEY_NS[A-Za-z]*UsageDescription = [^;]*;" *.xcodeproj/project.pbxproj | sort -u

# (b) 有独立 Info.plist 的项目（SpeechNote 是这种，(a) 会返回空）
grep -A1 "UsageDescription" $(git ls-files "*Info.plist" | head -1)
```

(a) 返回空只说明项目用的是 (b)，别误判成"没有权限文案"。

**判定**：代码里实际请求的每种权限都要有对应文案；文案说清**为什么要**和**数据去哪**，不能只写 "需要相册权限"。
参考达标写法（ShotZen）："ShotZen reads your screenshots to organize them with on-device AI. Photos never leave your device."

顺带查出口合规声明，缺了每次提交都要手填加密问卷：

```bash
grep -o "ITSAppUsesNonExemptEncryption[^;]*;" *.xcodeproj/project.pbxproj | sort -u
```

## 2. 托管的条款/EULA URL

**这是唯一一次真实 App Store 拒审的位置，优先级最高。**

3.1.2 要求：有自动续订/内购的 App，**商店页描述（Description）字段**里必须有可点击的 Terms of Use (EULA) 链接。注意三点，全是 SpeechNote 那次踩过的：

- 「元数据」指**商店页描述字段**，不是推广文本，不是审核备注，不是 App 内
- App 内购买页有「服务条款」按钮**不算数**——SpeechNote 内购页有按钮，照样被拒
- 必须是完整 `https://` 网址才会被 App Store 渲染成可点链接；写「服务条款」四个字或相对路径无效

先看代码里的法务 URL 到底存不存在：

```bash
grep -rhoE 'https://[A-Za-z0-9./_-]*(privacy|terms|eula|legal)[A-Za-z0-9./_-]*' --include="*.swift" . | sort -u
```

**关键判定**：Terms/EULA 是否只是个本地文本常量（如 `presentLegalPage(termsContent)`）而**根本没有网址**。这正是 SpeechNote 反复被拒的根因——不是"URL 填错了"，是"URL 压根不存在"。若 grep 只出隐私政策、没出 terms，直接判 FAIL。

再验证每个 URL 真能访问（reviewer 会点）：

```bash
for u in <上一步的 URL>; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 15 "$u")  $u"
done
```

非 200 判 FAIL。

**若确实缺 EULA 网址**，两个选择：
- 省事：用 Apple 标准 EULA `https://www.apple.com/legal/internet-services/itunes/dev/stdeula/`
- 一致（推荐）：与隐私政策同域自托管一份 terms 页，同时把 App 内按钮也改成开这个网址

⚠️ 若 App 内用的是自定义条款文本、元数据却填 Apple 标准 EULA，二者内容不一致是隐患。

## 3. 条款内容覆盖违禁内容

**教训来源**：Creem 审核拒因——支付通道要求 Terms 明确禁止 NSFW 内容。第 2 项的 200 只证明页面存在，不证明内容达标。

对第 2 项拿到的 Terms/EULA URL 拉正文检查：

```bash
curl -sL --max-time 20 "$TERMS_URL" | sed 's/<[^>]*>//g' | \
  grep -inE 'prohibit|forbidden|not permitted|nsfw|adult content|porn|sexual|illegal|unlawful|禁止|不得|违法'
```

**判定**：
- 命中明确的禁止性条款（违禁内容 / 违法用途 / 年龄门槛，至少其一）→ `✅ PASS`，引用命中行作证据
- URL 可达但无命中 → `⚠️ 需人工确认`，并在报告里给出建议补写的条款要点：禁止色情/NSFW 内容、禁止违法用途、平台对违规内容的处置权、使用年龄门槛
- 页面 JS 渲染导致 curl 拿不到正文 → `⚠️ 需人工确认`，注明原因，让用户人工打开核对
- 若用 Apple 标准 EULA，本项自动 PASS（Apple 条款已覆盖），但要提醒：App 内自定义条款与之不一致仍是隐患（见第 2 项）

## 4. 付费墙无硬编码价格

**先摆正认知**：在用的 Paywall 代码通常本来就没问题——ShotZen 的价格、月均价、省钱角标全是运行时从 StoreKit `displayPrice` 取或实时算的。真正的坑在另外三处。

**(a) `.lproj` 里的死字符串**（ShotZen 实际中招，3 条硬编码 `$9.99`/`$14.99`）：

```bash
grep -rnE '[¥$€£][0-9]+([.,][0-9]{2})?|[0-9]+\.99' $(git ls-files "*.lproj/Localizable.strings")
```

命中后**不要直接判 FAIL**——先 grep 该 key 是否还被 `L()` 引用。ShotZen 那 3 条无人引用、不显示，但属于地雷（有人接回去就显示错价），结论是删掉。

**(b) Swift 源码里的价格字面量**：

```bash
grep -rnE '"\s*[¥$€£][0-9]+' --include="*.swift" .
```

**(c) 静态营销截图印死价格 —— 风险最大的一项**
商店截图是静态图，不会跟着动态价格变。改价后截图里的价格必然对不上，既影响转化，reviewer 也可能挑。**这项无法自动检测**，必须让用户人工确认：截图里的 Paywall 画面有没有印具体价格。在表格里标为「需人工确认」。

**(d) 项目 CLAUDE.md 里关于价格的描述可能过时**
ShotZen 的 CLAUDE.md 曾写着「Save 69% chip 硬编码、调价要同步改文案」，核实下来角标是实时算的，这条已过时。**以代码为准，不要信文档**。

## 5. `.lproj` 本地化完整性

**语言集合从 repo 推导，不要预设**。各 App 语言数不同——ShotZen 是 en/zh-Hans/zh-Hant/ja 四语，SpeechNote 只有 en/zh-Hans 两语。写死"三语"必然误报。

```bash
git ls-files "*.lproj/Localizable.strings"
```

key 数量：

```bash
for f in $(git ls-files "*.lproj/Localizable.strings"); do
  echo "$(basename $(dirname $f)): $(grep -cE '^\s*\"' "$f")"
done
```

key 名一致性（以第一个语言为基准，逐一 diff）：

```bash
base=$(git ls-files "*.lproj/Localizable.strings" | head -1)
for f in $(git ls-files "*.lproj/Localizable.strings"); do
  echo "--- $f"
  diff <(grep -oE '^\s*"[^"]+"' "$base" | tr -d ' "' | sort) \
       <(grep -oE '^\s*"[^"]+"' "$f" | tr -d ' "' | sort) && echo "一致"
done
```

**判定**：各语言 key 数相同、key 名完全一致、无空值。缺 key 会在界面上显示原始 key 名，reviewer 会记 bug。

⚠️ **有 diff 不要直接判 FAIL，先看 key 长什么样**。有的项目用自然语言当 key（SpeechNote 的 `en.lproj` 里就有 `累计3次`、`语音转写` 这种中文 key）——这类 key 在 zh-Hans 里缺失时，回退显示的就是 key 本身，恰好是中文，界面上看不出问题。这种情况标「⚠️ 需人工确认」并列出差异 key，让用户判断，不要自作主张判 FAIL 或去补齐。

## 6. App 图标

```bash
icon=$(git ls-files "*AppIcon.appiconset/*1024*" | head -1)
sips -g pixelWidth -g pixelHeight -g hasAlpha -g space "$icon"
```

**判定**：1024×1024、`hasAlpha: no`、`space: RGB`。**有 alpha 通道会被拒**。

## 7. 版本号与 build 号递增

```bash
grep -oE "(MARKETING_VERSION|CURRENT_PROJECT_VERSION) = [^;]*;" *.xcodeproj/project.pbxproj | sort -u
git tag | sort -V | tail -5
```

pbxproj 里会有多个 target 的值（App 主 target 之外还有 widget/test target），**认准 App 主 target 的那个**，Release 和 Debug 两处都要改。

**判定三条**：
1. `MARKETING_VERSION` 与本次商店素材/宣发标注的版本一致——ShotZen 那次代码停在 1.1.1、素材全是 1.2.0，就是忘了 bump
2. **已发布过的版本号不可复用**——git tag 有 `v1.1.1` 说明大概率已上架，ASC 会拒绝同号新构建
3. `CURRENT_PROJECT_VERSION` 相对上次提交递增（ShotZen 用日期时间戳如 `202607122208`，天然递增）

版本号改哪个是**发布决策，必须让用户拍板**，不要自作主张。

## 8. 更新说明与商店元数据（按 repo 实际语言）

语言集合同第 5 项，从 `.lproj` 推导。

先搞清这一版到底改了什么，**不要猜**：

```bash
git log --oneline <上个版本 tag>..HEAD
```

若没打 tag，找 `MARKETING_VERSION` 上次变更的 commit 定位区间。

**App Store Connect 字符上限**（都踩过）：

| 字段 | 上限 | 备注 |
|---|---|---|
| 推广文本 Promotional Text | 170 | 不用重新提审就能随时改，适合放时效性卖点 |
| 更新说明 What's New | 4000 | |
| 描述 Description | 4000 | 3.1.2 的 EULA 链接放这里 |
| 关键词 Keywords | 100 | 逗号分隔、**逗号后不留空格**（空格占字符） |
| 副标题 Subtitle | 30 | 不受备案约束，ASO 主发力点 |
| 审核备注 Review Notes | — | **单一字段、不本地化**，填英文即可 |

**注意**：用户全局 CLAUDE.md 里「description ≤55 chars」指的是别处的短描述场景，不是 App Store 主描述（4000）。别搞混。

写文案的三条纪律：
- 只写这一版**真实实现**的功能。描述里提了未开放的功能 = 功能与描述不符，会被拒
- 名称/副标题/关键词三个字段**内部去重**，同一个词出现两次是浪费额度
- 更新说明里的 bug 修复细节，先问用户要不要对外暴露

## 9. 简中名称锁定备案名

中国大陆区强制 ICP/工信部 App 备案，ASC 里的名称需与**备案名称一致**。

**规则：简体中文名称 = 备案名，一个字不动，不加任何描述后缀。** 业界确实有"品牌名+描述"而备案只是品牌名照样过审的案例，但也有被判名称不一致卡审核的——名称对不上的代价是整个版本被拦，远大于塞几个关键词的 ASO 收益。不值得赌。

ASO 火力全部转移到**不受备案约束**的副标题（30 字符）和关键词字段（100 字符）。

繁/英/日名称**不受**此约束，可以用"品牌名 + 描述词"结构。

已知：ShotZen 简中备案名 =「截净」。

## 10. 启动崩溃隐患

```bash
grep -rn "fatalError\|try!" --include="*.swift" . | grep -v "init(coder:"
```

**必须过滤掉 `init(coder:)` 那一类**——那是 UIKit 样板，无害，不过滤会淹没真问题。

重点看**持久化/启动路径**：CoreData `loadPersistentStores` 失败直接 `fatalError` 会导致 store 损坏时**崩溃循环且无法自恢复**，Apple 明确拒审启动即崩的 App。

ShotZen 的处理方式可参考：该库只存可重建的缓存，改成加载失败时删掉 store 文件（含 `-wal`/`-shm` 连字符后缀，不是扩展名）重建一次，再失败才崩。

## 11. 数据层强制解包

补第 10 项的缺口——`fatalError|try!` 查不到强制解包。范围限定在持久化/数据层文件，全仓查会淹没在 UI 样板里：

```bash
git ls-files "*.swift" | grep -iE 'store|persist|coredata|database|repository|cache|migration' | \
  xargs grep -nE '(as! |try! |[[:alnum:]_)\]]![^=])' 2>/dev/null | \
  grep -v 'IBOutlet\|init(coder\|Test\|Preview'
```

正则说明：`![^=]` 排除 `!=` 比较符；过滤测试与 Preview 代码。

**判定看可达性，不看数量**：命中后逐条确认是否在**启动即执行**的路径上（CoreData container 初始化、启动时读磁盘/UserDefaults 强转）。启动路径上的强制解包 → `❌ FAIL`（store 损坏或数据缺失时启动即崩）；非启动路径 → `⚠️ 需人工确认`，列出清单。修法参考第 10 项 ShotZen 方案（`guard let` / 可失败初始化 / 删 store 重建），只报告不动代码。

## 12. Release 编译零警告

耗时长，**在审查开始时就后台起**，最后收结果。判定标准不止 build 成功，还要 0 warning：

```bash
LOG=$(mktemp)
xcodebuild -scheme <Scheme> -configuration Release -sdk iphoneos build CODE_SIGNING_ALLOWED=NO 2>&1 | tee "$LOG" | tail -5
grep -E 'warning:' "$LOG" | sort -u
```

**判定**：build 成功且 0 条 warning → `✅ PASS`；build 失败 → `❌ FAIL`；有 warning → `❌ FAIL`，逐条列 file:line + 警告类型，按「机械可修（未使用变量、废弃 API 有直替）」和「需决策（并发警告、行为可能变化）」分组，只列修复方案等批准。贴真实输出，不要只说"通过"。

## 13. 上线文案（微信公众号 / X / Reddit）

前提：第 8 项已用 `git log` 确定这一版的**真实改动**。文案纪律同第 8 项：只写真实实现的功能，不编造，bug 修复细节是否对外先问用户。

| 平台 | 形态 | 约束 |
|---|---|---|
| 微信公众号 | 短图文导语（2~3 段）| 中文，面向已有订阅者，讲「为什么做这个功能」而不是罗列 changelog；结尾给下载引导。需成文发布时另走 mufeng-wechat-publish-full |
| X | 1~3 条线程 | 英文为主；每条 ≤280 字符（链接按 23 字符计）；首条是钩子（问题场景），中间功能点，末条链接 |
| Reddit | 标题 + 正文 | 选 1~2 个相关 subreddit 并注明选择理由；正文以开发者身份透明自述（self-promo 需坦白）、讲解决什么问题、以征求反馈收尾；禁营销腔和 emoji 堆砌 |

三平台**不互相复制**，按各自语境重写。发布动作由用户执行，本 skill 只交付文案。

---

## 输出格式

审查完输出这张表，然后**按严重度排序**列出需处理项，每项给根因 + 证据（file:line）：

```markdown
## 发布审计结果 —— <App> v<版本>

| # | 检查项 | 结果 | 说明 |
|---|---|---|---|
| 1 | 权限说明文案 | ✅ PASS | 2 项权限均有文案，说明清晰 |
| 2 | 托管 EULA/条款 URL | ✅ PASS | 2 个 URL 均返回 200 |
| 3 | 条款覆盖违禁内容 | ⚠️ 需人工确认 | URL 可达但未见禁止性条款 |
| 4 | 付费墙无硬编码价格 | ⚠️ 需人工确认 | 代码动态渲染；静态截图待确认 |
| 5 | .lproj 本地化完整性 | ✅ PASS | en/zh-Hans/zh-Hant/ja 各 210 key，key 名一致 |
| 6 | App 图标 | ✅ PASS | 1024×1024, RGB, 无 alpha |
| 7 | 版本号与 build 号 | ❌ FAIL | MARKETING_VERSION=1.1.1，素材为 1.2.0 |
| 8 | 更新说明与元数据 | — | 已按 4 语言产出 |
| 9 | 简中名称锁定备案名 | ✅ PASS | =「截净」，未加后缀 |
| 10 | 启动崩溃隐患 | ❌ FAIL | CoreDataStack.swift:17 fatalError |
| 11 | 数据层强制解包 | ✅ PASS | 数据层无强制解包 |
| 12 | Release 编译零警告 | ❌ FAIL | build 成功，3 条 warning |
| 13 | 上线文案 | — | 已按 3 平台产出 |
```

三档判定：`✅ PASS` / `❌ FAIL` / `⚠️ 需人工确认`（无法自动检测的，如截图价格）。

表格之后依次给出：
1. 按严重度排序的需处理项（根因 + file:line 证据 + 修复方案）
2. 四语言商店元数据（第 8、9 项产出）
3. 三平台上线文案（第 13 项产出）
4. **需用户决策清单**：版本号 bump、EULA 选型、条款补写内容、警告修复批准、下方 ASC 端人工项

## 代码外的 ASC 端人工项

代码审查覆盖不到，每次都要提醒用户：

- IAP 商品要随本次构建**一起提交**（首次上架的订阅/内购必须挂到版本页才可售）
- 隐私「营养标签」如实声明（相册/麦克风等）
- App 信息 → **License Agreement 字段**：用 Apple 标准 EULA 或上传自定义（与描述里的链接**两个都做**最稳）
- 支持 URL / 联系邮箱可达（注意支持邮箱域名可能与 app 域名不同）
- 审核备注：写清是否需登录、权限用途、IAP 档位、**可复现的测试步骤**；把 EULA/隐私链接也贴一份并注明"描述里和 App 内都有"，帮 reviewer 快速核实

## 纪律

- **只读核查**。发现问题先给根因和证据，等用户批准再改代码（用户 CLAUDE.md：动手前先过审）
- **不自动 commit**
- 版本号改哪个、终身价定多少这类**发布决策交给用户**
- 贴命令**真实输出**，不要总结
- 别信项目 CLAUDE.md 里的陈述（已发现过时条目），**以代码为准**
