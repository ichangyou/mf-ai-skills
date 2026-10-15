#!/usr/bin/env python3
"""Fetch public App Store data for opportunity research (stdlib only).

Sources (no account or key needed):
  - Category charts:  itunes.apple.com/{cc}/rss/{feed}/limit=N/genre=G/json  (max ~100 entries)
  - App details:      itunes.apple.com/lookup?id=a,b,c&country=cc
  - Keyword search:   itunes.apple.com/search?term=..&entity=software&country=cc
  - Reviews:          itunes.apple.com/{cc}/rss/customerreviews/page=P/id=X/sortby=S/json  (pages 1-10, 50 each)

Responses are cached for 24h under $MUFENG_IAO_CACHE (default ~/.cache/mufeng-ios-app-opportunity).

Usage:
    asdata.py scan     --country us --genres 6007,6013 --out DIR
    asdata.py keyword  --country us --terms "habit tracker,water reminder" --out DIR
    asdata.py reviews  --country us --id 389801252 [--pages 10] [--sort mosthelpful] [--max-stars 2] [--out FILE]
    asdata.py assets   --country us --ids 389801252,284882215 --out DIR [--screens 3]
    asdata.py lookup   --country us --ids 389801252
    asdata.py charts   --country us --genre 6007
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

FEEDS = {"free": "topfreeapplications", "paid": "toppaidapplications", "grossing": "topgrossingapplications"}
REVIEW_SORTS = ("mostrecent", "mosthelpful")
CACHE_TTL = 24 * 3600
USER_AGENT = "Mozilla/5.0 (Macintosh) mufeng-ios-app-opportunity/1.0"
_last_request = 0.0


def cache_dir():
    return Path(os.environ.get("MUFENG_IAO_CACHE") or Path.home() / ".cache" / "mufeng-ios-app-opportunity")


def fetch(url, use_cache=True, raw=False):
    """GET a URL with a polite delay, retries and a 24h on-disk cache."""
    global _last_request
    path = cache_dir() / (hashlib.sha256(url.encode()).hexdigest() + (".bin" if raw else ".json"))
    if use_cache and path.is_file() and time.time() - path.stat().st_mtime < CACHE_TTL:
        data = path.read_bytes()
        return data if raw else json.loads(data)
    for attempt in range(4):
        wait = 0.6 - (time.time() - _last_request)
        if wait > 0:
            time.sleep(wait)
        _last_request = time.time()
        try:
            with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=30) as response:
                data = response.read()
            break
        except HTTPError as error:
            # 400 = past the last review page; 404 = unknown feed. Neither improves on retry.
            if error.code in (400, 404):
                return None
            if attempt == 3:
                raise
            time.sleep(2 ** attempt * 3)
        except URLError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt * 3)
    parsed = data if raw else json.loads(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return parsed


def label(node, key, default=None):
    value = node.get(key)
    return value.get("label", default) if isinstance(value, dict) else default


def days_since(iso, now=None):
    if not iso:
        return None
    now = now or datetime.now(timezone.utc)
    return max(0, (now - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days)


def parse_chart(feed_json):
    """Return [{id, name, rank}] from a legacy RSS chart response."""
    entries = (feed_json or {}).get("feed", {}).get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]
    return [
        {"id": e["id"]["attributes"]["im:id"], "name": label(e, "im:name"), "rank": i + 1}
        for i, e in enumerate(entries)
    ]


def chart(country, genre, feed, limit=100, use_cache=True):
    url = f"https://itunes.apple.com/{country}/rss/{FEEDS[feed]}/limit={limit}/genre={genre}/json"
    return parse_chart(fetch(url, use_cache))


def normalize_app(r, now=None):
    return {
        "id": str(r["trackId"]),
        "name": r.get("trackName"),
        "seller": r.get("sellerName") or r.get("artistName"),
        "genre": r.get("primaryGenreName"),
        "price": r.get("price"),
        "formatted_price": r.get("formattedPrice"),
        "rating": round(r["averageUserRating"], 2) if r.get("averageUserRating") is not None else None,
        "ratings": r.get("userRatingCount", 0),
        "rating_current_version": r.get("averageUserRatingForCurrentVersion"),
        "ratings_current_version": r.get("userRatingCountForCurrentVersion"),
        "version": r.get("version"),
        "released": r.get("releaseDate"),
        "updated": r.get("currentVersionReleaseDate"),
        "age_days": days_since(r.get("releaseDate"), now),
        "days_since_update": days_since(r.get("currentVersionReleaseDate"), now),
        "icon": r.get("artworkUrl512") or r.get("artworkUrl100"),
        "screenshots": r.get("screenshotUrls", []),
        "url": r.get("trackViewUrl"),
        "description": (r.get("description") or "")[:400],
    }


def lookup(country, ids, use_cache=True):
    apps = {}
    ids = [str(i) for i in ids]
    for start in range(0, len(ids), 100):
        chunk = ",".join(ids[start:start + 100])
        data = fetch(f"https://itunes.apple.com/lookup?{urlencode({'id': chunk, 'country': country})}", use_cache) or {}
        for r in data.get("results", []):
            if r.get("wrapperType") == "software" or "trackId" in r:
                app = normalize_app(r)
                apps[app["id"]] = app
    return apps


def search(country, term, limit=25, use_cache=True):
    query = urlencode({"term": term, "entity": "software", "country": country, "limit": limit})
    data = fetch(f"https://itunes.apple.com/search?{query}", use_cache) or {}
    return [normalize_app(r) | {"search_rank": i + 1} for i, r in enumerate(data.get("results", []))]


def parse_reviews(feed_json):
    entries = (feed_json or {}).get("feed", {}).get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]
    reviews = []
    for e in entries:
        if "im:rating" not in e:  # the first entry of some legacy feeds is the app itself
            continue
        reviews.append({
            "stars": int(label(e, "im:rating", 0)),
            "title": label(e, "title", ""),
            "content": label(e, "content", ""),
            "version": label(e, "im:version"),
            "date": label(e, "updated"),
            "votes": int(label(e, "im:voteCount", 0) or 0),
        })
    return reviews


def reviews(country, app_id, pages=10, sort="mostrecent", use_cache=True):
    collected = []
    for page in range(1, min(pages, 10) + 1):
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby={sort}/json"
        batch = parse_reviews(fetch(url, use_cache))
        if not batch:
            break
        collected.extend(batch)
    return collected


def review_summary(items):
    dist = {str(s): 0 for s in range(1, 6)}
    for r in items:
        dist[str(r["stars"])] = dist.get(str(r["stars"]), 0) + 1
    total = len(items)
    dates = sorted(r["date"][:10] for r in items if r.get("date"))
    return {"total": total, "distribution": dist,
            "low_share": round((dist["1"] + dist["2"]) / total, 3) if total else None,
            "date_range": {"earliest": dates[0], "latest": dates[-1]} if dates else None}


def scan(country, genre, use_cache=True):
    ranks = {}
    for feed in FEEDS:
        for row in chart(country, genre, feed, use_cache=use_cache):
            ranks.setdefault(row["id"], {})[feed] = row["rank"]
    apps = lookup(country, list(ranks), use_cache)
    rows = [apps[i] | {"ranks": ranks[i]} for i in ranks if i in apps]
    return {
        "kind": "scan", "country": country, "genre": str(genre),
        "genre_name": next((a["genre"] for a in rows if a.get("ranks", {}).get("free")), None),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "chart_sizes": {f: sum(1 for r in ranks.values() if f in r) for f in FEEDS},
        "missing_lookup": sorted(set(ranks) - set(apps)),
        "apps": rows,
    }


def download_assets(country, ids, out, screens=3, use_cache=True):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    saved = []
    for app in lookup(country, ids, use_cache).values():
        urls = [("icon", app["icon"])] + [(f"shot{i + 1}", u) for i, u in enumerate(app["screenshots"][:screens])]
        for kind, url in urls:
            if not url:
                continue
            data = fetch(url, use_cache, raw=True)
            if data:
                path = out / f"{app['id']}-{kind}{Path(url.split('?')[0]).suffix or '.jpg'}"
                path.write_bytes(data)
                saved.append(str(path))
    return saved


def emit(data, out=None):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text, encoding="utf-8")
        print(out)
    else:
        print(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-cache", action="store_true", help="Ignore cached responses")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("charts"); p.add_argument("--country", default="us"); p.add_argument("--genre", required=True)
    p.add_argument("--feed", choices=FEEDS, default="free"); p.add_argument("--out")
    p = sub.add_parser("lookup"); p.add_argument("--country", default="us"); p.add_argument("--ids", required=True); p.add_argument("--out")
    p = sub.add_parser("search"); p.add_argument("--country", default="us"); p.add_argument("--term", required=True)
    p.add_argument("--limit", type=int, default=25); p.add_argument("--out")
    p = sub.add_parser("reviews"); p.add_argument("--country", default="us"); p.add_argument("--id", required=True)
    p.add_argument("--pages", type=int, default=10); p.add_argument("--sort", choices=REVIEW_SORTS, default="mostrecent")
    p.add_argument("--max-stars", type=int, default=5, help="Keep reviews with stars <= N"); p.add_argument("--out")
    p = sub.add_parser("assets"); p.add_argument("--country", default="us"); p.add_argument("--ids", required=True)
    p.add_argument("--out", required=True); p.add_argument("--screens", type=int, default=3)
    p = sub.add_parser("scan"); p.add_argument("--country", default="us"); p.add_argument("--genres", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("keyword"); p.add_argument("--country", default="us"); p.add_argument("--terms", required=True)
    p.add_argument("--limit", type=int, default=25); p.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    cache = not args.no_cache
    country = args.country.lower()

    if args.cmd == "charts":
        emit(chart(country, args.genre, args.feed, use_cache=cache), args.out)
    elif args.cmd == "lookup":
        emit(list(lookup(country, args.ids.split(","), cache).values()), args.out)
    elif args.cmd == "search":
        emit(search(country, args.term, args.limit, cache), args.out)
    elif args.cmd == "reviews":
        items = reviews(country, args.id, args.pages, args.sort, cache)
        meta = lookup(country, [args.id], cache).get(str(args.id), {})
        emit({"kind": "reviews", "country": country, "id": str(args.id), "name": meta.get("name"),
              "rating": meta.get("rating"), "ratings": meta.get("ratings"), "sort": args.sort,
              "summary": review_summary(items),
              "reviews": [r for r in items if r["stars"] <= args.max_stars]}, args.out)
    elif args.cmd == "assets":
        for path in download_assets(country, args.ids.split(","), args.out, args.screens, cache):
            print(path)
    elif args.cmd == "scan":
        for genre in [g.strip() for g in args.genres.split(",") if g.strip()]:
            data = scan(country, genre, cache)
            emit(data, Path(args.out) / f"scan-{country}-{genre}.json")
            if not data["apps"]:
                print(f"WARNING: genre {genre} returned no apps in {country}", file=sys.stderr)
    elif args.cmd == "keyword":
        terms = [t.strip() for t in args.terms.split(",") if t.strip()]
        emit({"kind": "keywords", "country": country,
              "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "terms": {t: search(country, t, args.limit, cache) for t in terms}},
             Path(args.out) / f"keywords-{country}-{hashlib.sha1(quote(','.join(terms)).encode()).hexdigest()[:8]}.json")


if __name__ == "__main__":
    main()
