#!/usr/bin/env python3
"""Screen app-name candidates: App Store, USPTO, TMview, RDAP domains and live websites.

Standard library only. Subcommands:
  screen    run the five-step screen on candidate names
  variants  check spelling/sound-alike variants of finalists in trademark registries
  marks     list live trademarks for one name, with security-related goods highlighted
"""

import argparse
import json
import random
import re
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
USPTO_URL = "https://tmsearch.uspto.gov/prod-stage-v1-0-0/tmsearch"
TMVIEW_URL = "https://www.tmdn.org/tmview/api/search/results?translate=true"
RDAP = {"com": "https://rdap.verisign.com/com/v1/domain/", "app": "https://pubapi.registry.google/rdap/domain/",
        "dev": "https://pubapi.registry.google/rdap/domain/"}
STORES = {"us": ("software", "us"), "jp": ("software", "jp"), "cn": ("software", "cn"),
          "kr": ("software", "kr"), "de": ("software", "de"), "mac-us": ("macSoftware", "us")}
DEFAULT_CLASSES = {9, 42, 45}
DEAD = {"Expired", "Ended", "Withdrawn", "Refused", "Cancelled", "Surrendered", "Abandoned", "Invalidated", "Rejected"}
RISKY_APP = re.compile(r"password|passkey|vault|2fa|authenticat|otp|secur|privacy|private|lock|secret|encrypt|crypto|wallet", re.I)
RISKY_GENRES = {"Utilities", "Finance"}
RISKY_TEXT = re.compile(r"password|passkey|vault|2fa|authenticat|secur|encrypt|secret|credential|identity|login", re.I)
PARKED = re.compile(r"for sale|parked|buy this domain|domain name|is available|godaddy|sedo|afternic|porkbun|dan\.com", re.I)
BRAND_SEP = re.compile(r"\s*[:\-–—|(]")


def norm(text):
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def as_text(value):
    return " ".join(map(str, value)) if isinstance(value, list) else str(value or "")


def match_kind(name, text):
    """exact: the whole mark is the name; word: the name is a separate word; contains: substring only."""
    if not text:
        return None
    key = norm(name)
    if norm(text) == key:
        return "exact"
    if key in [norm(t) for t in re.split(r"[\s\-_.,/&+]+", text)]:
        return "word"
    if key in norm(text):
        return "contains"
    return None


def app_brand_kind(track_name, name):
    """exact: the part before ':' / '-' / '|' is the name; word: the name appears as a word elsewhere."""
    brand = BRAND_SEP.split(track_name or "", maxsplit=1)[0]
    if norm(brand) == norm(name):
        return "exact"
    if re.search(r"\b" + re.escape(name) + r"\b", track_name or "", re.I):
        return "word"
    return None


def parse_classes(value):
    if isinstance(value, list) and all(isinstance(v, int) for v in value):
        return sorted(set(value))
    return sorted({int(x) for x in re.findall(r"\d{1,3}", as_text(value))})


def risky_app(track_name, genre):
    return bool(RISKY_APP.search(track_name or "")) or genre in RISKY_GENRES


def parse_appstore(results, name):
    hits = {}
    for app in results:
        kind = app_brand_kind(app.get("trackName", ""), name)
        if kind:
            hits[app["trackId"]] = {"name": app.get("trackName"), "genre": app.get("primaryGenreName", ""),
                                    "seller": app.get("sellerName", ""), "kind": kind,
                                    "updated": (app.get("currentVersionReleaseDate") or "")[:10],
                                    "risky": risky_app(app.get("trackName"), app.get("primaryGenreName", ""))}
    return hits


def parse_uspto(data, name, classes=DEFAULT_CLASSES):
    marks = []
    for hit in data.get("hits", {}).get("hits", []):
        s = hit.get("source", {})
        if not s.get("alive"):
            continue
        kind = match_kind(name, s.get("wordmark"))
        if not kind:
            continue
        cls = parse_classes(s.get("internationalClass"))
        marks.append({"office": "US", "mark": s.get("wordmark"), "kind": kind, "classes": cls,
                      "software": bool(set(cls) & classes), "owner": as_text(s.get("ownerName"))[:80],
                      "status": s.get("statusDescription"), "filed": as_text(s.get("filedDate"))[:10],
                      "id": s.get("id"), "goods": as_text(s.get("goodsAndServices"))})
    return marks


def parse_tmview(data, name, classes=DEFAULT_CLASSES):
    marks = []
    for m in data.get("tradeMarks", []):
        if m.get("tradeMarkStatus") in DEAD:
            continue
        kind = match_kind(name, m.get("tmName"))
        if not kind:
            continue
        cls = parse_classes(m.get("niceClass"))
        marks.append({"office": m.get("tmOffice"), "mark": m.get("tmName"), "kind": kind, "classes": cls,
                      "software": bool(set(cls) & classes), "owner": as_text(m.get("applicantName"))[:80],
                      "status": m.get("tradeMarkStatus"), "filed": as_text(m.get("applicationDate"))[:10],
                      "id": m.get("ST13")})
    return marks


def security_goods(goods):
    items = [x.strip() for x in re.split(r";|\bIC \d{3}:", goods or "") if x.strip()]
    return [x for x in items if RISKY_TEXT.search(x)]


def rdap_status(code, body):
    if code == 404:
        return {"status": "free"}
    if code == 200:
        data = json.loads(body or b"{}")
        events = {e.get("eventAction"): (e.get("eventDate") or "")[:10] for e in data.get("events", [])}
        registrar = ""
        for entity in data.get("entities", []):
            if "registrar" in entity.get("roles", []):
                for item in (entity.get("vcardArray") or [None, []])[1]:
                    if item and item[0] == "fn":
                        registrar = item[3]
        return {"status": "taken", "registered": events.get("registration", ""), "registrar": registrar}
    return {"status": "unknown", "http": code}


def classify_site(title_desc):
    if not title_desc:
        return "empty"
    if RISKY_TEXT.search(title_desc):
        return "risky"
    if PARKED.search(title_desc):
        return "parked"
    return "other"


def auto_variants(name, limit=8):
    n = name.lower()
    out = []
    swaps = [("k", "c"), ("c", "k"), ("y", "i"), ("i", "y"), ("ph", "f"), ("f", "ph"), ("x", "ks"), ("qu", "kw")]
    for a, b in swaps:
        if a in n:
            out.append(n.replace(a, b, 1))
    doubled = re.sub(r"([bcdfglmnprst])\1", r"\1", n)
    if doubled != n:
        out.append(doubled)
    else:
        m = re.search(r"([aeiouy])([lnrst])([aeiouy])", n)
        if m:
            out.append(n[:m.start(2)] + m.group(2) * 2 + n[m.end(2):])
    if n.endswith("e"):
        out.append(n[:-1])
    elif n[-1] in "aeiouy":
        out.append(n[:-1] + "e")
    seen, result = {n}, []
    for v in out:
        if v not in seen:
            seen.add(v)
            result.append(v.capitalize())
    return result[:limit]


def verdict(result):
    fail, review = [], []
    for app in result.get("appstore", {}).get("hits", []):
        if app["kind"] == "exact":
            (fail if app["risky"] else review).append(f"App Store 同名品牌: {app['name']} ({app['genre']})")
    word_apps = [a for a in result.get("appstore", {}).get("hits", []) if a["kind"] == "word"]
    if len(word_apps) >= 3:
        review.append(f"App Store 有 {len(word_apps)} 个名称含该词的 App，品牌拥挤")
    for m in result.get("marks", []):
        if not m["software"]:
            continue
        line = f"{m['office']} {m['mark']} {m['classes']} {m['owner'][:40]}"
        if m["kind"] in ("exact", "word"):
            fail.append("同名商标: " + line)
        else:
            review.append("仅包含匹配，需人工复核: " + line)
    for domain, info in result.get("domains", {}).items():
        if info.get("site_class") == "risky":
            fail.append(f"{domain} 上有安全相关业务: {info.get('site', '')[:80]}")
    domains = result.get("domains", {})
    app_keys = [k for k in domains if k.endswith(".app")]
    if app_keys and all(domains[k].get("status") == "taken" for k in app_keys):
        review.append("所有 .app 组合均已注册")
    for err in result.get("errors", []):
        review.append("未完成: " + err)
    status = "FAIL" if fail else ("REVIEW" if review else "PASS")
    return {"status": status, "fail": fail, "review": review}


class Client:
    def __init__(self, delay=3.2, verbose=True):
        self.delay = delay
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(msg, file=sys.stderr)

    def fetch(self, url, data=None, headers=None, timeout=60, tries=3):
        h = {"User-Agent": UA}
        h.update(headers or {})
        for attempt in range(tries):
            try:
                req = urllib.request.Request(url, data=data, headers=h, method="POST" if data else "GET")
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return r.status, r.read()
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503) and attempt < tries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                return e.code, b""
            except Exception as e:
                self.log(f"  retry {attempt + 1} {url[:60]}: {e}")
                time.sleep(4 * (attempt + 1))
        return 0, b""

    def appstore(self, name, stores):
        hits, errors = {}, []
        for store in stores:
            entity, country = STORES[store]
            q = urllib.parse.urlencode({"term": name, "entity": entity, "country": country, "limit": 200})
            code, body = self.fetch("https://itunes.apple.com/search?" + q)
            if code != 200:
                errors.append(f"App Store {store} HTTP {code}")
            else:
                hits.update(parse_appstore(json.loads(body).get("results", []), name))
            time.sleep(self.delay)
        return list(hits.values()), errors

    def uspto(self, name, classes, max_records=1000):
        marks, start, total = [], 0, None
        while True:
            body = {"query": {"bool": {"must": [{"match": {"WM": {"query": name}}}]}}, "size": 200, "from": start}
            code, raw = self.fetch(USPTO_URL, json.dumps(body).encode(),
                                   {"Content-Type": "application/json", "Origin": "https://tmsearch.uspto.gov",
                                    "Referer": "https://tmsearch.uspto.gov/search/search-results"})
            if code != 200:
                return marks, {"total": total, "error": f"USPTO HTTP {code}"}
            data = json.loads(raw)
            total = data.get("hits", {}).get("totalValue", 0)
            marks += parse_uspto(data, name, classes)
            start += 200
            if start >= min(total, max_records):
                break
        return marks, {"total": total, "fetched": min(total, max_records), "truncated": total > max_records}

    def tmview(self, name, classes, pages):
        marks, total, fetched = [], None, 0
        for page in range(1, pages + 1):
            body = {"page": str(page), "pageSize": "100", "criteria": "C", "basicSearch": name}
            code, raw = self.fetch(TMVIEW_URL, json.dumps(body).encode(),
                                   {"Content-Type": "application/json", "Accept": "application/json",
                                    "Origin": "https://www.tmdn.org", "Referer": "https://www.tmdn.org/tmview/"},
                                   timeout=120, tries=4)
            if code != 200:
                return marks, {"total": total, "fetched": fetched, "error": f"TMview HTTP {code}"}
            data = json.loads(raw)
            batch = data.get("tradeMarks", [])
            total = data.get("totalResults") or data.get("totalTrademarks") or total
            fetched += len(batch)
            marks += parse_tmview(data, name, classes)
            if len(batch) < 100:
                break
            time.sleep(1.5)
        return marks, {"total": total, "fetched": fetched, "truncated": bool(total and fetched < total)}

    def rdap(self, domain):
        tld = domain.rsplit(".", 1)[-1]
        if tld not in RDAP:
            return {"status": "unsupported"}
        code, body = self.fetch(RDAP[tld] + domain, timeout=20)
        return rdap_status(code, body)

    def rdap_selfcheck(self):
        probe = "".join(random.choice(string.ascii_lowercase) for _ in range(14))
        return all(self.rdap(f"{probe}.{tld}")["status"] == "free" for tld in ("com", "app"))

    def site(self, domain):
        code, body = self.fetch("https://" + domain, timeout=12, tries=1)
        html = body.decode("utf-8", "ignore")
        title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        desc = re.search(r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"']([^\"']*)", html, re.I)
        text = " | ".join(x for x in [(title.group(1).strip() if title else ""), (desc.group(1).strip() if desc else "")] if x)
        return text[:200], code


def domain_set(name, tlds):
    n = norm(name)
    out = [f"{n}.{t}" for t in tlds]
    if "app" in tlds:
        out += [f"get{n}.app", f"use{n}.app"]
    if "com" in tlds:
        out += [f"{n}app.com", f"get{n}.com"]
    return out


def screen_one(client, name, args, rdap_ok):
    result = {"name": name, "errors": []}
    hits, errs = client.appstore(name, args.stores)
    result["appstore"] = {"hits": hits}
    result["errors"] += errs
    us, us_meta = client.uspto(name, args.classes)
    tm, tm_meta = client.tmview(name, args.classes, args.tmview_pages)
    for meta in (us_meta, tm_meta):
        if meta.get("error"):
            result["errors"].append(meta["error"])
    if tm_meta.get("truncated"):
        result["errors"].append(f"TMview 只取回 {tm_meta['fetched']}/{tm_meta['total']} 条")
    for m in us:
        m.pop("goods", None)
    result["marks"] = us + tm
    result["registry"] = {"uspto": us_meta, "tmview": tm_meta}
    domains = {}
    if rdap_ok:
        for d in domain_set(name, args.tlds):
            info = client.rdap(d)
            if info["status"] == "taken":
                text, code = client.site(d)
                info.update({"site": text, "site_http": code, "site_class": classify_site(text)})
            domains[d] = info
    else:
        result["errors"].append("RDAP 自检失败，域名结果不可信，已跳过")
    result["domains"] = domains
    result["verdict"] = verdict(result)
    return result


def print_summary(r):
    v = r["verdict"]
    apps = r["appstore"]["hits"]
    soft = [m for m in r["marks"] if m["software"]]
    doms = " ".join(f"{d}:{'free' if i['status'] == 'free' else i.get('registered') or i['status']}" for d, i in r["domains"].items())
    print(f"{v['status']:6} | {r['name']} | apps={len(apps)} marks(9/42/45)={len(soft)} | {doms}")
    for line in v["fail"][:5]:
        print("        ✗ " + line)
    for line in v["review"][:5]:
        print("        ? " + line)
    for d, i in r["domains"].items():
        if i.get("status") == "taken" and i.get("site"):
            print(f"        site {d} [{i.get('site_class')}]: {i['site'][:110]}")
    sys.stdout.flush()


def cmd_screen(args):
    names = [n.strip() for n in args.names.split(",") if n.strip()]
    client = Client(delay=args.delay)
    rdap_ok = client.rdap_selfcheck()
    if not rdap_ok:
        print("WARNING: RDAP 自检失败（随机域名没有返回 404），跳过域名检查", file=sys.stderr)
    results = []
    for name in names:
        r = screen_one(client, name, args, rdap_ok)
        results.append(r)
        print_summary(r)
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        path = out / "screen.json"
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        keep = [x for x in old if x["name"] not in {r["name"] for r in results}]
        path.write_text(json.dumps(keep + results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nwritten: {path}", file=sys.stderr)


def cmd_variants(args):
    client = Client(delay=args.delay)
    variants = [v.strip() for v in args.variants.split(",")] if args.variants else auto_variants(args.name)
    print(f"variants of {args.name}: {', '.join(variants)}")
    report = []
    for v in variants:
        us, _ = client.uspto(v, args.classes, max_records=400)
        tm, meta = client.tmview(v, args.classes, 1)
        soft = [m for m in us + tm if m["software"]]
        strong = [m for m in soft if m["kind"] in ("exact", "word")]
        print(f"  {v:12} software marks={len(soft)} exact/word={len(strong)}")
        for m in strong[:6]:
            print(f"      ✗ {m['office']} {m['mark']} {m['classes']} {m['owner'][:40]}")
        for m in [m for m in soft if m["kind"] == "contains"][:3]:
            print(f"      ? {m['office']} {m['mark']} {m['classes']} (仅包含)")
        for m in us:
            m.pop("goods", None)
        report.append({"variant": v, "marks": soft})
    if args.out:
        Path(args.out).mkdir(parents=True, exist_ok=True)
        (Path(args.out) / f"variants-{norm(args.name)}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_marks(args):
    client = Client(delay=args.delay)
    us, us_meta = client.uspto(args.name, args.classes)
    tm, tm_meta = client.tmview(args.name, args.classes, args.tmview_pages)
    print(f"USPTO total={us_meta.get('total')} | TMview fetched={tm_meta.get('fetched')}/{tm_meta.get('total')}")
    for m in [m for m in us if m["software"] and m["kind"] != "contains"]:
        print(f"  US {m['mark']} {m['classes']} {m['owner'][:45]} | {m['status']} | filed {m['filed']} | serial {m['id']}")
        for g in security_goods(m.get("goods"))[:6]:
            print(f"      ! {g[:200]}")
    others = [m for m in tm if m["software"] and m["kind"] != "contains" and m["office"] != "US"]
    for m in others:
        print(f"  {m['office']} {m['mark']} {m['classes']} {m['owner'][:45]} | {m['status']} | filed {m['filed']} | {m['id']}")
    if others:
        print("  note: TMview 结果不含商品描述；非美国商标的商品与服务需到该局官网按编号查看")
    if args.out:
        Path(args.out).mkdir(parents=True, exist_ok=True)
        (Path(args.out) / f"marks-{norm(args.name)}.json").write_text(
            json.dumps({"uspto": us, "tmview": tm, "meta": {"uspto": us_meta, "tmview": tm_meta}}, ensure_ascii=False, indent=2),
            encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("--classes", default="9,42,45", help="Nice classes treated as conflicts (default 9,42,45)")
        p.add_argument("--delay", type=float, default=3.2, help="Seconds between App Store requests")
        p.add_argument("--out", help="Directory for JSON output")

    s = sub.add_parser("screen", help="Five-step screen for candidate names")
    s.add_argument("--names", required=True, help="Comma-separated candidates")
    s.add_argument("--stores", default="us,jp,mac-us", help=f"App Store fronts: {','.join(STORES)}")
    s.add_argument("--tlds", default="app,com", help="Domain TLDs to check (app,com,dev)")
    s.add_argument("--tmview-pages", type=int, default=3)
    common(s)
    v = sub.add_parser("variants", help="Trademark check for spelling/sound-alike variants")
    v.add_argument("--name", required=True)
    v.add_argument("--variants", help="Comma-separated variants; default generates c/k, y/i, double-letter swaps")
    common(v)
    m = sub.add_parser("marks", help="Live marks for one name with security-related goods")
    m.add_argument("--name", required=True)
    m.add_argument("--tmview-pages", type=int, default=3)
    common(m)
    args = parser.parse_args(argv)
    args.classes = {int(c) for c in args.classes.split(",") if c.strip()}
    if getattr(args, "stores", None):
        args.stores = [x.strip() for x in args.stores.split(",") if x.strip()]
        unknown = set(args.stores) - set(STORES)
        if unknown:
            parser.error("unknown stores: " + ", ".join(sorted(unknown)))
    if getattr(args, "tlds", None):
        args.tlds = [x.strip().lstrip(".") for x in args.tlds.split(",") if x.strip()]
    {"screen": cmd_screen, "variants": cmd_variants, "marks": cmd_marks}[args.cmd](args)


if __name__ == "__main__":
    main()
