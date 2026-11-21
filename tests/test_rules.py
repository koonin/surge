import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rules(filename):
    for line in (ROOT / filename).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith(("#", ";", "//")):
            yield [field.strip() for field in line.split(",")]


def matches_domain(rule, hostname):
    kind, value = rule[:2]
    if kind == "DOMAIN":
        return hostname == value
    if kind == "DOMAIN-SUFFIX":
        return hostname == value or hostname.endswith("." + value)
    if kind == "DOMAIN-KEYWORD":
        return value in hostname
    return False


class RulesTest(unittest.TestCase):
    def test_safe_browsing_is_absent_from_privacy_domain_rules(self):
        privacy = list(rules("Privacy.list"))
        for host in ("safebrowsing.googleapis.com", "safebrowsing.urlsec.qq.com"):
            with self.subTest(host=host):
                self.assertFalse(any(matches_domain(rule, host) for rule in privacy))

    def test_netflix_domain_coverage(self):
        netflix = list(rules("netflix.list"))
        for rule in netflix:
            self.assertEqual(len(rule), 2, rule)
            self.assertIn(rule[0], {"DOMAIN", "DOMAIN-SUFFIX"}, rule)
        cases = {
            "www.netflix.com": True,
            "assets.nflxext.com": True,
            "cdn.nflxvideo.net": True,
            "fast.com": True,
            "api.fast.com": True,
            "www.youtube.com": False,
            "example.cloudfront.net": False,
            "notnetflix.com": False,
            "netflix.com.example.org": False,
        }
        for host, expected in cases.items():
            with self.subTest(host=host):
                self.assertEqual(any(matches_domain(rule, host) for rule in netflix), expected)
