#!/usr/bin/env python3
"""Render DIR/scores.json (+ optional DIR/pains.json) into a self-contained interactive HTML report.

pains.json (written by the agent after clustering reviews) is optional:
    [{"app_id": "123", "app_name": "Foo", "themes": [{"theme": "...", "count": 12, "quotes": ["..."]}]}]

Usage:
    report_html.py DIR [--out DIR/report.html]
"""
import argparse
import json
from pathlib import Path

TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>App 机会矩阵</title>
<style>
:root { --bg:#fbfaf7; --panel:#ffffff; --text:#1d1d1b; --muted:#6b6a66; --line:#e4e1da;
  --accent:#c2410c; --base:#3b6ea5; --flag:#b42318; --good:#1f7a4d; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#141413; --panel:#1d1d1b; --text:#ecebe6;
  --muted:#a3a19a; --line:#34332f; --accent:#f08a4b; --base:#7fa8d6; --flag:#f2766b; --good:#5cc08c; } }
:root[data-theme="dark"] { --bg:#141413; --panel:#1d1d1b; --text:#ecebe6; --muted:#a3a19a; --line:#34332f;
  --accent:#f08a4b; --base:#7fa8d6; --flag:#f2766b; --good:#5cc08c; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:15px/1.55 -apple-system,"PingFang SC","Helvetica Neue",sans-serif; }
main { max-width:1100px; margin:0 auto; padding:24px 16px 64px; }
h1 { font-size:24px; margin:0 0 4px; } h2 { font-size:18px; margin:36px 0 10px; }
.note { color:var(--muted); font-size:13px; }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; overflow-x:auto; }
table { border-collapse:collapse; width:100%; font-size:13px; font-variant-numeric:tabular-nums; }
th,td { text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); white-space:nowrap; }
th { color:var(--muted); font-weight:600; cursor:pointer; user-select:none; }
td.num, th.num { text-align:right; }
.bar { display:inline-block; height:8px; border-radius:4px; background:var(--accent); vertical-align:middle; margin-right:6px; }
.controls { display:flex; gap:12px; flex-wrap:wrap; align-items:center; margin-bottom:8px; font-size:13px; }
select { font:inherit; padding:4px 6px; background:var(--panel); color:var(--text); border:1px solid var(--line); border-radius:6px; }
svg text { fill:var(--muted); font-size:11px; }
.legend span { display:inline-flex; align-items:center; gap:4px; margin-right:12px; }
.dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
.cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:10px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:10px; display:flex; gap:10px; }
.card img { width:48px; height:48px; border-radius:11px; flex:none; }
.card b { display:block; font-size:14px; } .tag { display:inline-block; font-size:11px; padding:1px 6px; margin:2px 4px 0 0;
  border-radius:4px; border:1px solid var(--flag); color:var(--flag); }
.theme { margin:6px 0 12px; } .theme q { display:block; color:var(--muted); font-size:13px; margin:2px 0 2px 12px; }
#tip { position:fixed; pointer-events:none; background:var(--panel); border:1px solid var(--line); border-radius:6px;
  padding:6px 8px; font-size:12px; display:none; max-width:260px; }
</style>
</head>
<body>
<main>
<h1>App 机会矩阵</h1>
<p class="note">数据来自 App Store 公开榜单、lookup、search 与评论 RSS。评分数只是用户规模的代理，不是下载量；畅销榜只是收入的代理，不是收入数字。机会分是启发式加权，权重见 references/method.md。</p>

<h2>分类对比</h2>
<div class="panel"><table id="genres"></table></div>
<p class="note">机会分 = 0.35×(100−竞争度) + 25×畅销榜51–100名弱势占比 + 25×畅销榜51–100名小体量占比 + 15×免费榜前50新进入者占比。畅销榜前50几乎全是大应用，所以只统计尾部。</p>

<h2>应用分布：评分数 × 评分</h2>
<div class="panel">
<div class="controls"><label>分类 <select id="genreSel"></select></label>
<label><input type="checkbox" id="onlyGross"> 只看畅销榜</label>
<span class="legend"><span><i class="dot" style="background:var(--accent)"></i>在畅销榜</span>
<span><i class="dot" style="background:var(--base)"></i>不在畅销榜</span>
<span><i class="dot" style="border:2px solid var(--flag)"></i>被标记</span></span></div>
<svg id="scatter" viewBox="0 0 760 380" width="100%" role="img" aria-label="评分数与评分散点图"></svg>
<p class="note">左上 = 体量小但口碑好（可能是细分标杆）；右下 = 体量大但口碑差（用户不满，可切入）；靠左且在畅销榜 = 小应用也能赚钱。</p>
</div>

<h2>关键词</h2>
<div class="panel"><table id="keywords"></table></div>
<p class="note">需求度 = 前 10 名中第 3 高的评分数（对数，1000 万封顶），避开跨词通吃的综合大应用；竞争度 = 前 10 名评分数中位数（对数）。苹果不公开搜索热度，需求度只是代理。</p>

<h2>被标记的应用</h2>
<div class="cards" id="flagged"></div>

<h2>用户诟病点</h2>
<div id="pains"></div>
</main>
<div id="tip"></div>
<script>
const DATA = __DATA__;
const PAINS = __PAINS__;
const FLAG_ZH = {weak_monetizer:"弱势但赚钱", small_monetizer:"小体量但赚钱", stale_leader:"头部久未更新", low_rated_leader:"头部低评分"};
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fmt = n => n == null ? "—" : n >= 1e6 ? (n/1e6).toFixed(1)+"M" : n >= 1e3 ? (n/1e3).toFixed(1)+"k" : String(n);
const pct = x => x == null ? "—" : Math.round(x*100)+"%";

function table(el, cols, rows) {
  let sortKey = null, dir = -1;
  const render = () => {
    const data = sortKey ? [...rows].sort((a,b) => ((a[sortKey] > b[sortKey]) - (a[sortKey] < b[sortKey])) * dir) : rows;
    el.innerHTML = "<tr>" + cols.map(c => `<th class="${c.num?"num":""}" data-k="${c.k}">${c.t}</th>`).join("") + "</tr>" +
      data.map(r => "<tr>" + cols.map(c => `<td class="${c.num?"num":""}">${c.f ? c.f(r[c.k], r) : esc(r[c.k])}</td>`).join("") + "</tr>").join("");
    el.querySelectorAll("th").forEach(th => th.onclick = () => { dir = sortKey === th.dataset.k ? -dir : -1; sortKey = th.dataset.k; render(); });
  };
  render();
}
const bar = v => `<span class="bar" style="width:${Math.max(2, v*0.6)}px"></span>${v}`;

table(document.getElementById("genres"), [
  {k:"country", t:"地区"}, {k:"genre_name", t:"分类", f:(v,r)=>esc(v||r.genre)},
  {k:"opportunity", t:"机会分", num:1, f:bar}, {k:"competition", t:"竞争度", num:1},
  {k:"median_ratings_free_top25", t:"免费榜前25评分数中位", num:1, f:fmt},
  {k:"weak_share_grossing_tail", t:"畅销51–100弱势占比", num:1, f:pct},
  {k:"small_share_grossing_tail", t:"畅销51–100小体量占比", num:1, f:pct},
  {k:"fresh_share_free_top50", t:"新进入者占比", num:1, f:pct},
  {k:"paid_apps_in_grossing", t:"畅销榜付费下载占比", num:1, f:pct}], DATA.genres);

table(document.getElementById("keywords"), [
  {k:"country", t:"地区"}, {k:"term", t:"关键词"}, {k:"opportunity", t:"机会分", num:1, f:bar},
  {k:"demand", t:"需求度", num:1}, {k:"competition", t:"竞争度", num:1},
  {k:"median_ratings_top10", t:"前10评分数中位", num:1, f:fmt}, {k:"big_apps_top10", t:"≥1万评分的应用数", num:1},
  {k:"weak_share_top10", t:"弱势占比", num:1, f:pct}, {k:"fresh_share_top10", t:"新进入者占比", num:1, f:pct},
  {k:"top3", t:"前三名", f:v => (v||[]).map(a => esc(a.name)).join(" / ")}], DATA.keywords);

const sel = document.getElementById("genreSel"), only = document.getElementById("onlyGross"), svg = document.getElementById("scatter"), tip = document.getElementById("tip");
const groups = [...new Set(DATA.apps.map(a => a.country + "|" + a.genre))];
sel.innerHTML = groups.map(g => { const a = DATA.apps.find(x => x.country + "|" + x.genre === g); return `<option value="${g}">${esc(a.country)} / ${esc(a.genre_name || a.genre)}</option>`; }).join("");
function scatter() {
  const W=760, H=380, L=48, R=36, T=12, B=36;
  const apps = DATA.apps.filter(a => a.country + "|" + a.genre === sel.value && a.rating != null && (!only.checked || a.ranks.grossing));
  const x = n => L + Math.min(Math.log10(n + 1), 8) / 8 * (W - L - R);
  const y = r => T + (5 - Math.max(r, 1)) / 4 * (H - T - B);
  let s = "";
  for (let e = 0; e <= 8; e++) s += `<line x1="${x(10**e-1)}" x2="${x(10**e-1)}" y1="${T}" y2="${H-B}" stroke="var(--line)"/><text x="${x(10**e-1)}" y="${H-B+16}" text-anchor="middle">${fmt(10**e)}</text>`;
  for (let r = 1; r <= 5; r++) s += `<line x1="${L}" x2="${W-R}" y1="${y(r)}" y2="${y(r)}" stroke="var(--line)"/><text x="${L-8}" y="${y(r)+4}" text-anchor="end">${r}★</text>`;
  s += `<text x="${(L+W-R)/2}" y="${H-2}" text-anchor="middle">评分数（对数）</text>`;
  apps.forEach((a, i) => {
    const c = a.ranks.grossing ? "var(--accent)" : "var(--base)";
    s += `<circle data-i="${i}" cx="${x(a.ratings)}" cy="${y(a.rating)}" r="5" fill="${c}" fill-opacity=".75" stroke="${a.flags.length ? "var(--flag)" : "none"}" stroke-width="2"/>`;
  });
  svg.innerHTML = s;
  svg.querySelectorAll("circle").forEach(el => {
    const a = apps[+el.dataset.i];
    el.onmousemove = ev => { tip.style.display = "block"; tip.style.left = ev.clientX + 12 + "px"; tip.style.top = ev.clientY + 12 + "px";
      tip.innerHTML = `<b>${esc(a.name)}</b><br>${a.rating}★ · ${fmt(a.ratings)} 评分 · ${a.days_since_update ?? "?"} 天前更新<br>` +
        Object.entries(a.ranks).map(([k,v]) => ({free:"免费",paid:"付费",grossing:"畅销"}[k]) + " #" + v).join(" · ") +
        (a.flags.length ? "<br>" + a.flags.map(f => FLAG_ZH[f]).join("、") : ""); };
    el.onmouseleave = () => tip.style.display = "none";
  });
}
sel.onchange = only.onchange = scatter; if (groups.length) scatter();

document.getElementById("flagged").innerHTML = DATA.flagged_apps.slice(0, 40).map(a => `<div class="card">
  ${a.icon ? `<img src="${esc(a.icon)}" alt="" loading="lazy">` : ""}<div><b><a href="${esc(a.url)}" target="_blank" rel="noopener">${esc(a.name)}</a></b>
  <span class="note">${esc(a.genre_name)} · ${a.rating ?? "—"}★ · ${fmt(a.ratings)} 评分 · ${a.days_since_update ?? "?"} 天前更新</span><br>
  ${a.flags.map(f => `<span class="tag">${FLAG_ZH[f]}</span>`).join("")}</div></div>`).join("") || '<p class="note">没有被标记的应用。</p>';

document.getElementById("pains").innerHTML = PAINS.length ? PAINS.map(p => `<div class="panel" style="margin-bottom:10px"><b>${esc(p.app_name)}</b>` +
  (p.themes||[]).map(t => `<div class="theme">${esc(t.theme)} <span class="note">（${t.count ?? "?"} 条）</span>${(t.quotes||[]).map(q => `<q>${esc(q)}</q>`).join("")}</div>`).join("") + "</div>").join("")
  : '<p class="note">尚未生成 pains.json（差评聚类由 agent 完成后写入）。</p>';
</script>
</body>
</html>
"""


def embed(data):
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def render(directory):
    directory = Path(directory)
    scores = json.loads((directory / "scores.json").read_text(encoding="utf-8"))
    pains_path = directory / "pains.json"
    pains = json.loads(pains_path.read_text(encoding="utf-8")) if pains_path.is_file() else []
    return TEMPLATE.replace("__DATA__", embed(scores)).replace("__PAINS__", embed(pains))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dir")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    out = Path(args.out or Path(args.dir) / "report.html")
    out.write_text(render(args.dir), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
