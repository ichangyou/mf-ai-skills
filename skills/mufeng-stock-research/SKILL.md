---
name: mufeng-stock-research
description: "Educational stock research skill for market analysis and financial study. Works standalone via web search, or enhanced with Financial Datasets MCP for real-time structured data. Runs 8 analyses (fundamentals, risk, DCF, peer comparison, catalysts, technical, sentiment, research summary) and exports to PDF + HTML (default) or Word. Supports English (default) and Chinese."
when_to_use: "stock analysis, stock research, market research, 股票研究, 股票分析, 市场研究, fundamental analysis, DCF valuation, company research, analyze [company], research [company]"
metadata:
  version: "1.0.0"
---

> **Disclaimer:** This skill is for educational research and informational purposes only. It does not constitute professional financial advice. Users should consult a licensed financial advisor before making any financial decisions. All analytical conclusions include uncertainty caveats. This skill will not use language expressing certainty such as "guaranteed", "definitely", or "sure profit", and will not provide investment-action judgments for specific assets.

# Stock Research & Market Analysis

Fetch live data from Financial Datasets MCP (where available), supplement with web search, run 8 structured analyses, and compile a professional research report for educational purposes.

## Safety Boundary: Educational Research Only

This skill may analyze facts, assumptions, valuation scenarios, risks, catalysts, technical levels, and sentiment for a publicly traded company. It must not answer whether the user should take an investment action in a specific stock.

### Direct Action Questions

If the user asks any direct action question about a specific asset, first state the boundary, then redirect to educational research. This includes questions such as:

- "Should I buy/sell/hold [stock]?"
- "Is [stock] a buy?"
- "Would you buy [stock] now?"
- "Should I wait, avoid, enter, add, reduce, or take profits?"
- "Is [stock] investable?"

Use this response pattern before continuing:

```text
I can't tell you whether to buy, sell, hold, wait on, avoid, enter, or treat [Company] ([Ticker]) as investable. I can provide educational research on its fundamentals, valuation scenarios, risks, catalysts, technical levels, and sentiment so you can discuss the decision with a licensed financial advisor.
```

### Prohibited Output

Never write an action verdict for a specific stock, even with disclaimers or investor-type qualifiers. Prohibited examples include:

- "Clear answer: yes/no."
- "I would buy / would not buy [stock] now."
- "For a new position: wait."
- "Existing holders should hold/sell/add/reduce."
- "Avoid this stock."
- "This is investable / not investable."
- "Enter below $X" or "take profits above $X."

Do not replace Buy/Hold/Sell with synonymous action labels such as accumulate, trim, wait, avoid, enter, exit, add, reduce, take profits, or investable. Do not convert valuation gaps, technical levels, or sentiment into instructions about what the user should do.

## Financial Datasets MCP — Optional Enhancement

This skill works in two modes. **Web search alone produces a complete, high-quality report.** MCP adds real-time structured data when available.

### MCP Availability Detection

Before calling any MCP endpoint, probe availability with `get_company_facts(ticker)`:

| Probe result | Mode | Action |
|---|---|---|
| Returns data | **MCP Mode** | Use MCP endpoints + web search to supplement |
| "tool not found" / tool call fails at invocation | **Web-Only Mode** | Skip all MCP calls, use web search for everything |
| "balance is $0.00" on paid endpoints | **Partial MCP Mode** | `get_company_facts` only; web search for all paid data |
| Auth/session error (no "balance" mention) | Re-authenticate | Call `authenticate` → user opens URL → `complete_authentication` → retry |

### MCP Endpoint Tiers

| Endpoint | Tier |
|---|---|
| `get_company_facts` | ✅ Free |
| All others (price, financials, metrics, news, earnings, insider trades) | 💳 Requires paid credits |

## Workflow

Before Step 1, check whether the user's request contains a direct action question. If it does, apply the safety boundary above and then continue only with educational research content.

### Step 1: Parse Input

Extract from the user's request:
- **Company name** (required) — e.g. "Tesla", "拼多多", "Apple"
- **Ticker symbol** — derive if not provided (Apple → AAPL, 拼多多 → PDD, Tesla → TSLA). For A-share companies not on US exchanges, note the limitation.
- **Language** — English (default) or Chinese (用中文 / 中文输出 / zh)
- **Export format** — PDF (default) or Word/DOCX (word / docx / .docx)

### Step 2: Collect Data

Run the probe first, then collect all data in parallel using the appropriate mode.

#### Data collection map (MCP → Web fallback)

| Data needed | MCP call (if available) | Web search fallback (always works) |
|---|---|---|
| Company overview | `get_company_facts(ticker)` | "[company] sector industry exchange" |
| Latest stock price | `get_stock_price(ticker)` | "[ticker] stock price today" |
| Valuation metrics | `get_financial_metrics_snapshot(ticker)` | "[ticker] PE ratio EV/EBITDA market cap" |
| Income statement (4yr) | `get_income_statement(ticker, period="annual", limit=4)` | "[company] annual revenue net income 2022 2023 2024 2025" |
| Cash flow statement | `get_cash_flow_statement(ticker, period="annual", limit=4)` | "[company] free cash flow operating cash flow" |
| Balance sheet | `get_balance_sheet(ticker, period="annual", limit=2)` | "[company] total debt cash balance sheet" |
| Historical metrics | `get_financial_metrics(ticker, period="ttm", limit=4)` | "[company] gross margin operating margin ROE history" |
| Earnings history | `get_earnings(ticker)` | "[company] latest earnings EPS beat miss surprise" |
| Price history (6mo) | `get_stock_prices(ticker, start_date="[180d ago]", end_date="[today]", interval="day")` | "[ticker] stock chart 52 week high low support resistance" |
| Recent news (30d) | `get_news(ticker, start_date="[30d ago]", end_date="[today]", limit=10)` | "[company] news last 30 days" |
| Insider trades | `get_insider_trades(ticker)` *(load schema via ToolSearch first)* | "[company] insider trading SEC Form 4 recent" |
| Peer benchmarking | `get_financial_metrics_snapshot(peer_ticker)` for each peer | "[peer1] [peer2] PE ratio EV/EBITDA comparison" |

Tag every number in the report with its source: `[MCP]` or `[Web]`.

In Web-Only Mode, run all web searches in parallel — this is fast and produces complete results, as demonstrated in production use.

### Step 3: Run the 8 Analyses

Load `references/prompts.md` for the full bilingual prompt set. Write each section grounded in the MCP data fetched above — never use vague estimates when real numbers are available.

| # | Topic | Primary MCP data sources |
|---|-------|--------------------------|
| 1 | **Fundamentals** | income statement (4yr trend), company facts, financial metrics snapshot |
| 2 | **Downside Risk** | balance sheet (debt/cash), financial metrics (leverage), news (regulatory) |
| 3 | **DCF Scenario Analysis** | cash flow statement (FCF), income statement (margins), balance sheet (shares, net cash) |
| 4 | **Peer Benchmarking** | financial metrics snapshot for company + each peer |
| 5 | **Catalysts** | earnings (surprise history + next date), news, insider trades |
| 6 | **Technical Analysis** | stock_prices (180-day daily OHLCV), stock_price (latest) |
| 7 | **News Sentiment** | news (last 30 days), insider trades direction |
| 8 | **Research Summary** | synthesize all above into educational research discussion |

### Step 4: Compile the Report

Assemble all 8 sections into a single markdown document:

```markdown
# [Company] ([TICKER]) Stock Research Report
**Date:** [date] | **Price:** $XX.XX | **Market Cap:** $XXB | **Language:** EN/ZH

> **Disclaimer:** This report is for educational and informational purposes only and does not constitute professional financial advice. Users should consult a licensed financial advisor before making any financial decisions. All conclusions are analytical estimates with inherent uncertainty — not guarantees of future performance.

---

## Executive Summary
[2-3 sentence overview of the company's key financial characteristics, notable strengths/risks, and research observations — no investment-action verdict]

## 1. Fundamental Analysis
...

## 2. Downside Risk Assessment
...

## 3. DCF Scenario Analysis
...

## 4. Peer Benchmarking
...

## 5. Upcoming Catalysts
...

## 6. Technical Analysis
...

## 7. News Sentiment
...

## 8. Research Summary
**Supportive Factors:** [key factors that could support stronger outcomes, with uncertainty caveats]
**Risk Factors:** [key downside risks and headwinds]
**Key Uncertainties:** [variables that most affect the outcome]
**Summary:** [balanced synthesis of all 7 analyses — no investment-action verdict, no price target]

---
*Data sourced from Financial Datasets MCP and public web sources as of [date]. This report is AI-generated for educational purposes only and does not constitute professional financial advice. Consult a licensed financial advisor before making any investment decisions.*
```

Save the compiled markdown to the user's Desktop as `[Ticker]-research-report.md`. Resolve the Desktop path at runtime based on the operating system (macOS/Linux: the standard user Desktop folder; Windows: the equivalent Desktop path).

### Step 5: Export the Report

Run `scripts/export.py` to generate the final files. **Default behavior exports both HTML and PDF** alongside the markdown. Resolve the skill script path at runtime from the skill's own directory.

```bash
# Default: HTML + PDF (always run this unless user asked for Word)
python3 [skill-dir]/scripts/export.py [Desktop]/[Ticker]-research-report.md

# Word only (when user explicitly asked for Word/DOCX)
python3 [skill-dir]/scripts/export.py [Desktop]/[Ticker]-research-report.md --format docx
```

Expected output files (default):
- `[Ticker]-research-report.md` — source markdown
- `[Ticker]-research-report.html` — readable in any browser, Chinese fonts supported
- `[Ticker]-research-report.pdf` — print-ready PDF via Chrome headless or pandoc

If PDF generation fails (no Chrome or PDF engine), the script prints a warning and still delivers the HTML. Tell the user which files were created and their paths.

## Language Rules

- **English (default)**: All prose in English. Financial terms stay in English (P/E, DCF, EBITDA).
- **Chinese mode**: All prose in Simplified Chinese. Use standard Chinese financial terms (市盈率, 现金流折现, 每股收益, etc.).

## Quality Standards

- Every number in the report must come from MCP data or a cited web source — no fabricated figures.
- DCF scenario analysis must explicitly state: FCF base (from MCP), revenue growth rate, operating margin, WACC, terminal growth rate, shares outstanding (from balance sheet), and that outputs are illustrative scenarios rather than price targets.
- Technical analysis must name specific price levels derived from the fetched OHLCV data.
- Peer table must show real metric values fetched from MCP, not approximations.
- **Do not make Buy / Hold / Sell ratings, issue price targets, or provide direct investment instructions.** This also forbids equivalent action judgments such as wait, avoid, enter, exit, add, reduce, take profits, accumulate, trim, or investable. This skill is for educational research only.
- **Do not use language expressing certainty** such as "guaranteed", "definitely", or "sure profit." All analytical conclusions must include uncertainty caveats (e.g., "suggests", "indicates", "based on current data").
- The Research Summary must present balanced supportive factors, risk factors, and key uncertainties — never a single definitive call or action verdict.

## Final Compliance Check

Before sending the final answer or generated report, verify:

- It does not answer a direct action question with yes/no.
- Outside the boundary sentence that declines to provide action guidance, it does not contain "I would buy", "I would not buy", "for a new position", "wait", "avoid", "enter", "add", "reduce", "take profits", "investable", or equivalent action language for the specific stock.
- Any DCF output is labeled as an illustrative valuation scenario, not a target price.
- Technical levels are labeled as market observations, not entry, exit, stop-loss, or take-profit instructions.
