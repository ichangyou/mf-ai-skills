---
name: mufeng-stock-research
description: "Educational stock research skill for market analysis and financial study. Works standalone via web search, or enhanced with Financial Datasets MCP for real-time structured data. Runs 8 analyses (fundamentals, risk, DCF, peer comparison, catalysts, technical, sentiment, research summary) and exports to PDF + HTML (default) or Word. Supports English (default) and Chinese."
when_to_use: "stock analysis, stock research, market research, 股票研究, 股票分析, 市场研究, fundamental analysis, DCF valuation, company research, analyze [company], research [company]"
metadata:
  version: "3.0.0"
---

> **Disclaimer:** This skill is for educational research and informational purposes only. It does not constitute professional financial advice. Users should consult a licensed financial advisor before making any financial decisions. All analytical conclusions include uncertainty caveats. This skill will not use language expressing certainty such as "guaranteed", "definitely", or "sure profit", and will not directly instruct users to buy or sell specific assets.

# Stock Research & Market Analysis

Fetch live data from Financial Datasets MCP (where available), supplement with web search, run 8 structured analyses, and compile a professional research report for educational purposes.

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
| 3 | **DCF Valuation** | cash flow statement (FCF), income statement (margins), balance sheet (shares, net cash) |
| 4 | **Peer Benchmarking** | financial metrics snapshot for company + each peer |
| 5 | **Catalysts** | earnings (surprise history + next date), news, insider trades |
| 6 | **Technical Analysis** | stock_prices (180-day daily OHLCV), stock_price (latest) |
| 7 | **News Sentiment** | news (last 30 days), insider trades direction |
| 8 | **Research Summary** | synthesize all above into educational thesis discussion |

### Step 4: Compile the Report

Assemble all 8 sections into a single markdown document:

```markdown
# [Company] ([TICKER]) Stock Research Report
**Date:** [date] | **Price:** $XX.XX | **Market Cap:** $XXB | **Language:** EN/ZH

> **Disclaimer:** This report is for educational and informational purposes only and does not constitute professional financial advice. Users should consult a licensed financial advisor before making any financial decisions. All conclusions are analytical estimates with inherent uncertainty — not guarantees of future performance.

---

## Executive Summary
[2-3 sentence overview of the company's key financial characteristics, notable strengths/risks, and research thesis — no buy/sell/hold call]

## 1. Fundamental Analysis
...

## 2. Downside Risk Assessment
...

## 3. DCF Valuation
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
**Bull Case:** [key upside factors, with uncertainty caveats]
**Bear Case:** [key downside factors, with uncertainty caveats]
**Key Uncertainties:** [variables that most affect the outcome]
**Summary:** [balanced synthesis of all 7 analyses — no buy/sell/hold rating, no price target]

---
*Data sourced from Financial Datasets MCP and public web sources as of [date]. This report is AI-generated for educational purposes only and does not constitute professional financial advice. Consult a licensed financial advisor before making any investment decisions.*
```

Save the compiled markdown to `~/Desktop/[Ticker]-research-report.md`.

### Step 5: Export the Report

Run `scripts/export.py` to generate the final files. **Default behavior exports both HTML and PDF** alongside the markdown.

```bash
# Default: HTML + PDF (always run this unless user asked for Word)
python3 ~/.claude/skills/mufeng-stock-research/scripts/export.py ~/Desktop/[Ticker]-research-report.md

# Word only (when user explicitly asked for Word/DOCX)
python3 ~/.claude/skills/mufeng-stock-research/scripts/export.py ~/Desktop/[Ticker]-research-report.md --format docx
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
- DCF model must explicitly state: FCF base (from MCP), revenue growth rate, operating margin, WACC, terminal growth rate, shares outstanding (from balance sheet).
- Technical analysis must name specific price levels derived from the fetched OHLCV data.
- Peer table must show real metric values fetched from MCP, not approximations.
- **Do not make Buy / Hold / Sell ratings, issue price targets, or provide direct investment instructions.** This skill is for educational research only.
- **Do not use language expressing certainty** such as "guaranteed", "definitely", or "sure profit." All analytical conclusions must include uncertainty caveats (e.g., "suggests", "indicates", "based on current data").
- The Research Summary must present a balanced bull/bear discussion — never a single definitive call.
