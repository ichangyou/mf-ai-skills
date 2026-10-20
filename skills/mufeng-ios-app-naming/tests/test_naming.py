import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "namecheck.py"
spec = importlib.util.spec_from_file_location("namecheck_test_module", SCRIPT)
nc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = nc
spec.loader.exec_module(nc)


def uspto_hit(wordmark, classes, alive=True, owner="Owner Inc.", goods=""):
    return {"source": {"wordmark": wordmark, "alive": alive, "internationalClass": classes, "ownerName": owner,
                       "statusDescription": "REGISTERED", "filedDate": "2025-04-15T00:00:00", "id": "1",
                       "goodsAndServices": goods}}


class MatchTests(unittest.TestCase):
    def test_match_kind(self):
        self.assertEqual(nc.match_kind("Kypra", "KYPRA"), "exact")
        self.assertEqual(nc.match_kind("Tacit", "TACIT KNOWLEDGE"), "word")
        self.assertEqual(nc.match_kind("Hexkey", "HEX-KEY"), "exact")
        self.assertEqual(nc.match_kind("Arcella", "MARCELLA"), "contains")
        self.assertIsNone(nc.match_kind("Kypra", "CYPRA"))
        self.assertIsNone(nc.match_kind("Kypra", None))

    def test_app_brand_kind(self):
        self.assertEqual(nc.app_brand_kind("Stillkey: Focus & App Blocker", "Stillkey"), "exact")
        self.assertEqual(nc.app_brand_kind("Alcove - Vault for Everything", "Alcove"), "exact")
        self.assertEqual(nc.app_brand_kind("Reserve ALCOVE", "Alcove"), "word")
        self.assertIsNone(nc.app_brand_kind("KeeperPass", "Keeper"))

    def test_parse_classes(self):
        self.assertEqual(nc.parse_classes("IC 009 IC 042"), [9, 42])
        self.assertEqual(nc.parse_classes(["IC 045", "IC 009"]), [9, 45])
        self.assertEqual(nc.parse_classes([42, 9, 9]), [9, 42])

    def test_auto_variants(self):
        variants = nc.auto_variants("Kypra")
        self.assertIn("Cypra", variants)
        self.assertIn("Kipra", variants)
        self.assertNotIn("Kypra", variants)
        self.assertIn("Arcela", nc.auto_variants("Arcella"))


class ParseTests(unittest.TestCase):
    def test_parse_appstore_flags_risky(self):
        results = [
            {"trackId": 1, "trackName": "Alcove - Vault for Everything", "primaryGenreName": "Utilities"},
            {"trackId": 2, "trackName": "Alcove: Tasks & Notes", "primaryGenreName": "Productivity"},
            {"trackId": 3, "trackName": "Something Else", "primaryGenreName": "Games"},
        ]
        hits = nc.parse_appstore(results, "Alcove")
        self.assertEqual(set(hits), {1, 2})
        self.assertTrue(hits[1]["risky"])
        self.assertFalse(hits[2]["risky"])

    def test_parse_uspto_filters_dead_and_unrelated(self):
        data = {"hits": {"hits": [
            uspto_hit("TACIT", "IC 009", goods="IC 009: Computer software for controlling and managing access server applications; Speech recognition software."),
            uspto_hit("TACIT", "IC 020", alive=False),
            uspto_hit("TACIT KNOWLEDGE", ["IC 042"]),
            uspto_hit("TACITURN WINES", "IC 033"),
            uspto_hit("MORIS", "IC 001"),
        ]}}
        marks = nc.parse_uspto(data, "Tacit")
        self.assertEqual([m["mark"] for m in marks], ["TACIT", "TACIT KNOWLEDGE", "TACITURN WINES"])
        self.assertEqual([m["software"] for m in marks], [True, True, False])
        self.assertEqual(marks[2]["kind"], "contains")

    def test_parse_tmview_skips_dead(self):
        data = {"tradeMarks": [
            {"tmName": "MICA", "tmOffice": "CN", "tradeMarkStatus": "Registered", "niceClass": [9], "applicantName": ["小米科技有限责任公司"]},
            {"tmName": "MICA", "tmOffice": "GB", "tradeMarkStatus": "Expired", "niceClass": [9]},
            {"tmName": "MICA BEAUTY", "tmOffice": "US", "tradeMarkStatus": "Registered", "niceClass": [3]},
        ]}
        marks = nc.parse_tmview(data, "Mica")
        self.assertEqual([(m["office"], m["software"]) for m in marks], [("CN", True), ("US", False)])

    def test_security_goods(self):
        goods = "IC 042: Computer programming; Identity validation (computer security); User authentication services using single sign-on technology; Web design"
        found = nc.security_goods(goods)
        self.assertEqual(len(found), 2)
        self.assertTrue(all("authent" in g.lower() or "security" in g.lower() for g in found))

    def test_rdap_status(self):
        self.assertEqual(nc.rdap_status(404, b"")["status"], "free")
        body = json.dumps({"events": [{"eventAction": "registration", "eventDate": "2026-07-03T10:00:00Z"}],
                           "entities": [{"roles": ["registrar"], "vcardArray": ["vcard", [["version", {}, "text", "4.0"], ["fn", {}, "text", "Namecheap Inc."]]]}]}).encode()
        info = nc.rdap_status(200, body)
        self.assertEqual(info, {"status": "taken", "registered": "2026-07-03", "registrar": "Namecheap Inc."})
        self.assertEqual(nc.rdap_status(0, b"")["status"], "unknown")

    def test_classify_site(self):
        self.assertEqual(nc.classify_site("Keyfold: your API keys and passwords, locked in one file"), "risky")
        self.assertEqual(nc.classify_site("porkbun.com | domain for sale"), "parked")
        self.assertEqual(nc.classify_site("Mica Apps"), "other")
        self.assertEqual(nc.classify_site(""), "empty")

    def test_domain_set(self):
        self.assertEqual(nc.domain_set("Kypra", ["app", "com"]),
                         ["kypra.app", "kypra.com", "getkypra.app", "usekypra.app", "kypraapp.com", "getkypra.com"])


class VerdictTests(unittest.TestCase):
    def base(self):
        return {"appstore": {"hits": []}, "marks": [], "domains": {"x.app": {"status": "free"}}, "errors": []}

    def test_clean_passes(self):
        self.assertEqual(nc.verdict(self.base())["status"], "PASS")

    def test_exact_software_mark_fails(self):
        r = self.base()
        r["marks"] = [{"office": "EM", "mark": "TACIT", "kind": "exact", "classes": [9, 42], "software": True, "owner": "Reflex"}]
        self.assertEqual(nc.verdict(r)["status"], "FAIL")

    def test_contains_mark_needs_review(self):
        r = self.base()
        r["marks"] = [{"office": "US", "mark": "MARCELLA", "kind": "contains", "classes": [9], "software": True, "owner": "Reef"}]
        self.assertEqual(nc.verdict(r)["status"], "REVIEW")

    def test_non_software_mark_ignored(self):
        r = self.base()
        r["marks"] = [{"office": "US", "mark": "MICA", "kind": "exact", "classes": [3], "software": False, "owner": "x"}]
        self.assertEqual(nc.verdict(r)["status"], "PASS")

    def test_risky_site_fails(self):
        r = self.base()
        r["domains"] = {"keyfold.app": {"status": "taken", "site_class": "risky", "site": "Keyfold: passwords"},
                        "getkeyfold.app": {"status": "free"}}
        self.assertEqual(nc.verdict(r)["status"], "FAIL")

    def test_same_brand_app(self):
        r = self.base()
        r["appstore"]["hits"] = [{"name": "Tacit - タシット", "genre": "Lifestyle", "kind": "exact", "risky": False}]
        self.assertEqual(nc.verdict(r)["status"], "REVIEW")
        r["appstore"]["hits"][0]["risky"] = True
        self.assertEqual(nc.verdict(r)["status"], "FAIL")

    def test_all_app_domains_taken_and_errors_review(self):
        r = self.base()
        r["domains"] = {"a.app": {"status": "taken"}, "geta.app": {"status": "taken"}, "a.com": {"status": "free"}}
        self.assertEqual(nc.verdict(r)["status"], "REVIEW")
        r = self.base()
        r["errors"] = ["TMview HTTP 0"]
        self.assertEqual(nc.verdict(r)["status"], "REVIEW")


class CliTests(unittest.TestCase):
    def test_screen_writes_json_offline(self):
        fake = {"name": "Kypra", "errors": [], "appstore": {"hits": []}, "marks": [], "domains": {}, "registry": {}}
        fake["verdict"] = nc.verdict(fake)
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(nc.Client, "rdap_selfcheck", return_value=True), \
                mock.patch.object(nc, "screen_one", return_value=fake), \
                mock.patch("sys.stdout"):
            nc.main(["screen", "--names", "Kypra", "--out", tmp])
            data = json.loads((Path(tmp) / "screen.json").read_text(encoding="utf-8"))
        self.assertEqual(data[0]["verdict"]["status"], "PASS")

    def test_rejects_unknown_store(self):
        with mock.patch("sys.stderr"), self.assertRaises(SystemExit):
            nc.main(["screen", "--names", "X", "--stores", "mars"])


if __name__ == "__main__":
    unittest.main()
