import importlib.util
from datetime import datetime, timezone
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(f"aof_{name}_test_module", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


asdata, score, report = load("asdata"), load("score"), load("report_html")
NOW = datetime(2026, 10, 15, tzinfo=timezone.utc)


def app(i, rating=4.7, ratings=1000, updated="2026-09-01T00:00:00Z", released="2020-01-01T00:00:00Z", ranks=None, price=0.0):
    raw = {"trackId": i, "trackName": f"App {i}", "sellerName": "Dev", "primaryGenreName": "Productivity",
           "price": price, "averageUserRating": rating, "userRatingCount": ratings,
           "currentVersionReleaseDate": updated, "releaseDate": released, "artworkUrl512": "https://x/icon.jpg",
           "screenshotUrls": ["https://x/1.png"], "trackViewUrl": "https://apps.apple.com/x"}
    return asdata.normalize_app(raw, NOW) | {"ranks": ranks or {}}


class ParseTests(unittest.TestCase):
    def test_parse_chart_ranks_in_order(self):
        feed = {"feed": {"entry": [{"id": {"attributes": {"im:id": "11"}}, "im:name": {"label": "A"}},
                                   {"id": {"attributes": {"im:id": "22"}}, "im:name": {"label": "B"}}]}}
        self.assertEqual(asdata.parse_chart(feed), [{"id": "11", "name": "A", "rank": 1}, {"id": "22", "name": "B", "rank": 2}])

    def test_parse_chart_single_entry_dict_and_empty(self):
        single = {"feed": {"entry": {"id": {"attributes": {"im:id": "1"}}, "im:name": {"label": "A"}}}}
        self.assertEqual(len(asdata.parse_chart(single)), 1)
        self.assertEqual(asdata.parse_chart({"feed": {}}), [])
        self.assertEqual(asdata.parse_chart(None), [])

    def test_parse_reviews_skips_app_entry(self):
        feed = {"feed": {"entry": [
            {"im:name": {"label": "The app itself"}},
            {"im:rating": {"label": "1"}, "title": {"label": "Bad"}, "content": {"label": "Sync lost data"},
             "im:version": {"label": "2.0"}, "updated": {"label": "2026-10-01"}, "im:voteCount": {"label": "3"}}]}}
        parsed = asdata.parse_reviews(feed)
        self.assertEqual(parsed, [{"stars": 1, "title": "Bad", "content": "Sync lost data", "version": "2.0",
                                   "date": "2026-10-01", "votes": 3}])

    def test_review_summary(self):
        summary = asdata.review_summary([{"stars": 1}, {"stars": 2}, {"stars": 5}, {"stars": 5}])
        self.assertEqual(summary["distribution"], {"1": 1, "2": 1, "3": 0, "4": 0, "5": 2})
        self.assertEqual(summary["low_share"], 0.5)
        self.assertIsNone(asdata.review_summary([])["low_share"])
        self.assertIsNone(summary["date_range"])
        dated = asdata.review_summary([{"stars": 1, "date": "2026-10-13T17:02:02-07:00"}, {"stars": 2, "date": "2021-03-01T00:00:00-07:00"}])
        self.assertEqual(dated["date_range"], {"earliest": "2021-03-01", "latest": "2026-10-13"})

    def test_normalize_app_days(self):
        a = app(1, updated="2026-10-05T00:00:00Z", released="2025-10-15T00:00:00Z")
        self.assertEqual((a["id"], a["days_since_update"], a["age_days"]), ("1", 10, 365))


class ScoreTests(unittest.TestCase):
    def test_weakness_bounds(self):
        self.assertEqual(score.app_weakness(app(1, rating=4.8, updated="2026-10-01T00:00:00Z")), 0.0)
        self.assertEqual(score.app_weakness(app(2, rating=3.0, updated="2023-01-01T00:00:00Z")), 1.0)
        # Too few ratings: rating gap ignored, only staleness counts.
        self.assertEqual(score.app_weakness(app(3, rating=1.0, ratings=5, updated="2026-10-01T00:00:00Z")), 0.0)

    def test_flags(self):
        a = app(1, rating=3.5, ratings=800, updated="2024-01-01T00:00:00Z", ranks={"grossing": 3, "free": 10})
        self.assertEqual(set(score.app_flags(a)), {"weak_monetizer", "small_monetizer", "stale_leader", "low_rated_leader"})
        self.assertEqual(score.app_flags(app(2, ratings=10**6, ranks={"free": 1})), [])

    def test_genre_opportunity_orders_weak_market_higher(self):
        crowded = {"country": "us", "genre": "1", "apps": [
            app(i, ratings=10**6, ranks={"free": i, "grossing": i}) for i in range(1, 51)]}
        open_market = {"country": "us", "genre": "2", "apps": [
            app(i, rating=3.6, ratings=300, released="2026-06-01T00:00:00Z", updated="2024-06-01T00:00:00Z",
                ranks={"free": i, "grossing": i}) for i in range(1, 51)]}
        c, o = score.score_genre(crowded), score.score_genre(open_market)
        self.assertEqual(c["competition"], 100)
        self.assertEqual(c["opportunity"], 0)
        self.assertGreater(o["opportunity"], 80)

    def test_genre_tail_uses_grossing_51_to_100(self):
        # Big apps at #1-50, small apps at #51-100: only the tail drives the small share.
        apps = [app(i, ratings=10**6, ranks={"grossing": i}) for i in range(1, 51)]
        apps += [app(i, ratings=500, ranks={"grossing": i}) for i in range(51, 101)]
        g = score.score_genre({"country": "us", "genre": "1", "apps": apps})
        self.assertEqual((g["grossing_tail_size"], g["small_share_grossing_tail"]), (50, 1.0))
        short = score.score_genre({"country": "us", "genre": "2", "apps": apps[:10]})
        self.assertEqual((short["grossing_tail_size"], short["small_share_grossing_tail"]), (10, 0.0))

    def test_keyword_score(self):
        results = [app(i, ratings=r) for i, r in enumerate([200000, 50, 40, 30, 20, 10, 10, 10, 5, 5, 5], 1)]
        k = score.score_keyword("habit", results)
        self.assertEqual((k["big_apps_top10"], k["max_ratings_top10"], len(k["top3"])), (1, 200000, 3))
        self.assertEqual(k["demand_basis_ratings"], 40)  # 3rd largest, not the lone giant

    def test_keyword_demand_ignores_single_generalist_giant(self):
        giant = app(99, ratings=6_000_000)
        niche = score.score_keyword("niche", [giant] + [app(i, ratings=300) for i in range(1, 10)])
        broad = score.score_keyword("broad", [giant] + [app(i, ratings=1_000_000) for i in range(1, 10)])
        self.assertLess(niche["demand"], 30)
        self.assertGreater(broad["demand"], niche["demand"])
        self.assertEqual(score.score_keyword("one", [giant])["demand_basis_ratings"], 6_000_000)
        self.assertEqual(score.score_keyword("none", [])["demand"], 0)

    def test_build_and_report_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            scan = {"kind": "scan", "country": "us", "genre": "6007", "genre_name": "Productivity",
                    "apps": [app(1, rating=3.2, ratings=900, ranks={"grossing": 1, "free": 2}), app(2, ranks={"free": 1})]}
            (d / "scan-us-6007.json").write_text(json.dumps(scan), encoding="utf-8")
            (d / "keywords-us-x.json").write_text(json.dumps({"country": "us", "terms": {"todo": [app(3)]}}), encoding="utf-8")
            (d / "pains.json").write_text(json.dumps([{"app_id": "1", "app_name": "App 1",
                                                       "themes": [{"theme": "</script>同步", "count": 2, "quotes": ["lost"]}]}]), encoding="utf-8")
            result = score.build(d)
            self.assertEqual([a["id"] for a in result["flagged_apps"]], ["1"])
            self.assertEqual(result["keywords"][0]["term"], "todo")
            (d / "scores.json").write_text(json.dumps(result), encoding="utf-8")
            page = report.render(d)
            self.assertNotIn("__DATA__", page)
            self.assertEqual(page.count("</script>"), 1)  # embedded data cannot close the script tag


if __name__ == "__main__":
    unittest.main()
