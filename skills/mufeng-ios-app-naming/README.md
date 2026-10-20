# 沐风 · iOS 起名与查重（mufeng-ios-app-naming）

支持 Codex 和 Claude Code。安装与更新见 [项目安装文档](https://github.com/ichangyou/mf-ai-skills/blob/main/docs/installation.md)。

给 iOS/macOS App 起英文名，并对每个候选名做五步查重：

1. App Store 有没有同名 App。
2. 美国 USPTO 和多国 TMview 的商标库里，9、42、45 类有没有同名商标。
3. 域名有没有被注册。
4. 已注册的域名上实际跑着什么业务。
5. 网页检索。

最后对终选名做读音和字形的近似检查，按加权评分推荐一个名字。

## 调用

Codex：

```text
$mufeng-ios-app-naming 给我的密码管理器起个英文名，全球市场，要短、平静克制
```

Claude Code：

```text
/mufeng-ios-app-naming 给我的密码管理器起个英文名，全球市场，要短、平静克制
```

也可以只查一个已有的名字：`/mufeng-ios-app-naming 帮我查 Kypra 这个名字能不能用`。

## 依赖与执行范围

- Python 3.9+，只用标准库，不需要安装依赖。
- 能访问 `itunes.apple.com`、`tmsearch.uspto.gov`、`www.tmdn.org`，以及 RDAP 服务（Verisign、Google Registry）。不需要账号或 API Key。
- 第五步的网页检索需要宿主提供网页检索工具；没有的话，报告里会写明这一步没有完成。

“支持”表示提供两端入口和执行说明；外部服务需要网络可达。实际执行规则见 [SKILL.md](SKILL.md)。

## 能查 / 查不了

| 能查 | 查不了 |
|---|---|
| App Store 美区、日区 iPhone，美区 Mac（可加中、韩、德） | 已下架、或者所选地区以外的 App |
| 美国商标，按名字取全部记录，包括商品描述 | 日本商标（需要在 J-PlatPat 手动查）；非美国商标的商品描述（需要到对应商标局官网查） |
| TMview 汇总的欧盟、英国、中国、韩国、澳大利亚等地商标 | TMview 中匹配上万条的常见词（只取前几页，报告会标明截断） |
| `.com`、`.app`、`.dev` 的注册状态和注册日期 | 域名能不能买到、要多少钱 |
| 已注册域名上网站的标题和描述 | 需要登录或 JS 渲染的网站内容 |

结果只是筛查结论，**不构成法律意见**。正式定名前请商标代理人确认。

## 输出

- `naming/<日期>-<主题>/screen.json`：每个候选名的 App Store 命中、商标、域名、网站内容和判定结果（PASS / REVIEW / FAIL）。
- `marks-<名字>.json`、`variants-<名字>.json`：单个名字的商标详情，以及近似变体的检查结果。
- markdown 报告：包括通过名单、排除原因、终选的加权评分，以及用户待办。默认保存到 `~/Desktop`，项目里已有命名文档时会追加进去。

## 单独使用脚本

```bash
python3 scripts/namecheck.py screen --names "Kypra,Arcella" --out work
python3 scripts/namecheck.py marks --name Tacit --out work
python3 scripts/namecheck.py variants --name Kypra --out work
```

## 测试

```bash
python3 -m unittest discover -s skills/mufeng-ios-app-naming/tests -v
```

测试使用离线样例数据，不访问网络。
