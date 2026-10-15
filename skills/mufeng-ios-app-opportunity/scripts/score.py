#!/usr/bin/env python3
"""Score genres, keywords and apps from asdata.py output.

Reads every scan-*.json and keywords-*.json in DIR, writes DIR/scores.json and prints
a compact summary. All scores are heuristics on public proxies (rating counts, ratings,
update dates, chart presence); they are not downloads or revenue. Weights are documented
in references/method.md.

Usage:
    score.py DIR
"""
import json
import math
from pathlib import Path
from statistics import median
import sys

SMALL_RATINGS = 5000      # "small" app: fewer ratings than this
WEAK_THRESHOLD = 0.35     # app weakness at or above this counts as a weak incumbent
FRESH_DAYS = 365          # released within this many days counts as a recent entrant


def clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def log_scale(value, lo_exp, hi_exp):
    """Map a count onto 0..1 between 10**lo_exp and 10**hi_exp on a log scale."""
    return clip((math.log10((value or 0) + 1) - lo_exp) / (hi_exp - lo_exp))


def app_weakness(app):
    """0..1: low rating (60%) plus stale updates (40%). Unknown values count as neutral 0."""
    rating = app.get("rating")
    rating_gap = clip((4.6 - rating) / 1.1) if rating is not None and app.get("ratings", 0) >= 20 else 0.0
    days = app.get("days_since_update")
    staleness = clip((days - 180) / 545) if days is not None else 0.0
    return round(0.6 * rating_gap + 0.4 * staleness, 3)


def app_flags(app):
    ranks = app.get("ranks", {})
    weakness = app_weakness(app)
    best = min(ranks.values()) if ranks else None
    flags = []
    if "grossing" in ranks and weakness >= WEAK_THRESHOLD:
        flags.append("weak_monetizer")
    if "grossing" in ranks and app.get("ratings", 0) < SMALL_RATINGS:
        flags.append("small_monetizer")
    if best is not None and best <= 25 and (app.get("days_since_update") or 0) > 365:
        flags.append("stale_leader")
    if best is not None and best <= 50 and (app.get("rating") or 5) < 4.0 and app.get("ratings", 0) >= 100:
        flags.append("low_rated_leader")
    return flags


def top(apps, feed, n):
    ranked = [a for a in apps if feed in a.get("ranks", {})]
    return sorted(ranked, key=lambda a: a["ranks"][feed])[:n]


def share(items, predicate):
    return round(sum(1 for i in items if predicate(i)) / len(items), 3) if items else 0.0


def score_genre(scan):
    apps = scan["apps"]
    free25, free50 = top(apps, "free", 25), top(apps, "free", 50)
    grossing = top(apps, "grossing", 100)
    # Grossing #1-50 is almost always big brands; small or weak apps that still earn show up in #51-100.
    tail = grossing[50:] if len(grossing) > 50 else grossing
    median_ratings = median([a.get("ratings", 0) for a in free25]) if free25 else 0
    competition = round(100 * log_scale(median_ratings, 2, 6))  # 100 ratings -> 0, 1M -> 100
    weak = share(tail, lambda a: app_weakness(a) >= WEAK_THRESHOLD)
    small = share(tail, lambda a: a.get("ratings", 0) < SMALL_RATINGS)
    fresh = share(free50, lambda a: (a.get("age_days") or 99999) <= FRESH_DAYS)
    opportunity = round(0.35 * (100 - competition) + 25 * weak + 25 * small + 15 * fresh)
    return {
        "country": scan["country"], "genre": scan["genre"], "genre_name": scan.get("genre_name"),
        "chart_sizes": scan.get("chart_sizes"),
        "competition": competition, "median_ratings_free_top25": median_ratings,
        "median_rating_free_top25": round(median([a["rating"] for a in free25 if a.get("rating")]), 2) if free25 else None,
        "grossing_tail_size": len(tail), "weak_share_grossing_tail": weak, "small_share_grossing_tail": small,
        "fresh_share_free_top50": fresh, "paid_apps_in_grossing": share(grossing, lambda a: (a.get("price") or 0) > 0),
        "opportunity": opportunity,
    }


def score_keyword(term, results):
    top10 = results[:10]
    counts = [a.get("ratings", 0) for a in top10]
    # Generalist giants rank for every term in a category; the 3rd-largest app shows whether
    # several apps are sustained by this term, and the 10M ceiling keeps big categories apart.
    demand_basis = sorted(counts, reverse=True)[min(2, len(counts) - 1)] if counts else 0
    demand = round(100 * log_scale(demand_basis, 2, 7))
    competition = round(100 * log_scale(median(counts) if counts else 0, 1, 5))
    weak = share(top10, lambda a: app_weakness(a) >= WEAK_THRESHOLD)
    fresh = share(top10, lambda a: (a.get("age_days") or 99999) <= FRESH_DAYS)
    return {
        "term": term, "results": len(results), "demand": demand, "competition": competition,
        "median_ratings_top10": median(counts) if counts else 0, "max_ratings_top10": max(counts, default=0),
        "demand_basis_ratings": demand_basis,
        "big_apps_top10": sum(1 for c in counts if c >= 10000),
        "weak_share_top10": weak, "fresh_share_top10": fresh,
        "opportunity": round(0.3 * demand + 0.3 * (100 - competition) + 25 * weak + 15 * fresh),
        "top3": [{"id": a["id"], "name": a["name"], "rating": a.get("rating"), "ratings": a.get("ratings")} for a in top10[:3]],
    }


def app_row(app, scan):
    return {
        "id": app["id"], "name": app["name"], "seller": app.get("seller"), "icon": app.get("icon"), "url": app.get("url"),
        "country": scan["country"], "genre": scan["genre"], "genre_name": scan.get("genre_name"),
        "price": app.get("price"), "rating": app.get("rating"), "ratings": app.get("ratings", 0),
        "days_since_update": app.get("days_since_update"), "age_days": app.get("age_days"),
        "ranks": app.get("ranks", {}), "weakness": app_weakness(app), "flags": app_flags(app),
    }


def build(directory):
    directory = Path(directory)
    scans = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("scan-*.json"))]
    keyword_files = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("keywords-*.json"))]
    genres = sorted((score_genre(s) for s in scans if s.get("apps")), key=lambda g: -g["opportunity"])
    apps = [app_row(a, s) for s in scans for a in s["apps"]]
    keywords = sorted((score_keyword(t, r) | {"country": k["country"]} for k in keyword_files for t, r in k["terms"].items()),
                      key=lambda k: -k["opportunity"])
    flagged = sorted((a for a in apps if a["flags"]), key=lambda a: (-len(a["flags"]), -a["weakness"]))
    return {"genres": genres, "keywords": keywords, "flagged_apps": flagged, "apps": apps}


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1 or not Path(argv[0]).is_dir():
        sys.exit(__doc__)
    result = build(argv[0])
    out = Path(argv[0]) / "scores.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for g in result["genres"]:
        print(f"[genre] {g['country']}/{g['genre_name'] or g['genre']}: opportunity={g['opportunity']} "
              f"competition={g['competition']} weak={g['weak_share_grossing_tail']} small={g['small_share_grossing_tail']} "
              f"fresh={g['fresh_share_free_top50']}")
    for k in result["keywords"]:
        print(f"[keyword] {k['country']}/{k['term']}: opportunity={k['opportunity']} demand={k['demand']} "
              f"competition={k['competition']} big_apps={k['big_apps_top10']}")
    for a in result["flagged_apps"][:15]:
        print(f"[app] {a['name']} ({a['genre_name']}) rating={a['rating']} ratings={a['ratings']} "
              f"updated={a['days_since_update']}d ranks={a['ranks']} flags={','.join(a['flags'])}")
    print(out)


if __name__ == "__main__":
    main()
