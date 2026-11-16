import json
import unittest
from pathlib import Path

from src.faers import (
    FaersCounts,
    build_contingency_tables,
    compute_chi_square,
    compute_prr,
    compute_ror,
    is_signal,
    lookup_signals,
    rank_signals,
    shape_signal,
    shape_signal_payload,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _counts(name):
    """Takes a fixture stem. Returns its reaction counts keyed by term."""
    payload = json.loads((FIXTURES / f"{name}.json").read_text())
    return {r["term"]: r["count"] for r in payload["results"]}


DRUG_COUNTS = _counts("faers_drug_counts")
BACKGROUND_COUNTS = _counts("faers_background_counts")

# HEADACHE cell layout: a=50 with the drug and event, b=50 drug without the
# event, c=150 event without the drug, d=1550 neither.
HEADACHE = FaersCounts("HEADACHE", 50, 50, 150, 1550)


class TestContingencyTables(unittest.TestCase):

    def test_builds_a_2x2_table_per_shared_event(self):
        tables = build_contingency_tables(DRUG_COUNTS, BACKGROUND_COUNTS)
        by_event = {t.event: t for t in tables}
        self.assertEqual(set(by_event), {"HEADACHE", "NAUSEA", "DIZZINESS"})
        self.assertEqual(by_event["HEADACHE"], HEADACHE)

    def test_cells_sum_to_the_background_total(self):
        table = build_contingency_tables(DRUG_COUNTS, BACKGROUND_COUNTS)[0]
        total = (table.drug_event + table.drug_no_event
                 + table.event_no_drug + table.no_drug_no_event)
        self.assertEqual(total, sum(BACKGROUND_COUNTS.values()))

    def test_skips_events_absent_from_the_background(self):
        drug = {"HEADACHE": 5, "UNSEEN": 3}
        background = {"HEADACHE": 40, "RASH": 200}
        tables = build_contingency_tables(drug, background)
        self.assertEqual([t.event for t in tables], ["HEADACHE"])


class TestPrr(unittest.TestCase):

    def test_matches_the_hand_computed_ratio(self):
        # (50/100) / (150/1700) = 0.5 / 0.0882353 = 5.6667.
        stat = compute_prr(HEADACHE)
        self.assertAlmostEqual(stat.value, 5.6667, places=3)
        self.assertEqual(stat.case_count, 50)

    def test_matches_the_hand_computed_interval(self):
        stat = compute_prr(HEADACHE)
        self.assertAlmostEqual(stat.ci_low, 4.4197, places=3)
        self.assertAlmostEqual(stat.ci_high, 7.2655, places=3)


class TestRor(unittest.TestCase):

    def test_matches_the_hand_computed_ratio(self):
        # (50 * 1550) / (50 * 150) = 77500 / 7500 = 10.3333.
        stat = compute_ror(HEADACHE)
        self.assertAlmostEqual(stat.value, 10.3333, places=3)

    def test_matches_the_hand_computed_interval(self):
        stat = compute_ror(HEADACHE)
        self.assertAlmostEqual(stat.ci_low, 6.7467, places=3)
        self.assertAlmostEqual(stat.ci_high, 15.8267, places=3)


class TestChiSquare(unittest.TestCase):

    def test_matches_the_hand_computed_value(self):
        self.assertAlmostEqual(compute_chi_square(HEADACHE), 157.99, places=1)


class TestSignalFlagging(unittest.TestCase):

    def test_flags_when_all_three_criteria_are_met(self):
        self.assertTrue(is_signal(2.0, 4.0, 3))

    def test_prr_just_below_the_cutoff_does_not_flag(self):
        self.assertFalse(is_signal(1.99, 400.0, 300))

    def test_chi_square_just_below_the_cutoff_does_not_flag(self):
        self.assertFalse(is_signal(9.0, 3.99, 300))

    def test_case_count_just_below_the_cutoff_does_not_flag(self):
        self.assertFalse(is_signal(9.0, 400.0, 2))

    def test_the_headache_signal_is_flagged(self):
        self.assertTrue(shape_signal(HEADACHE)["flagged"])


class TestRankingAndPayload(unittest.TestCase):

    def test_ranks_by_prr_and_drops_thin_case_counts(self):
        thin = FaersCounts("SNEEZE", 2, 98, 4, 1600)
        tables = build_contingency_tables(DRUG_COUNTS, BACKGROUND_COUNTS)
        ranked = rank_signals(tables + [thin])
        events = [s["event"] for s in ranked]
        self.assertNotIn("Sneeze", events)
        prrs = [s["prr"] for s in ranked]
        self.assertEqual(prrs, sorted(prrs, reverse=True))

    def test_payload_shape_carries_signals_and_disclaimer(self):
        tables = build_contingency_tables(DRUG_COUNTS, BACKGROUND_COUNTS)
        payload = shape_signal_payload("headache-drug", rank_signals(tables))
        self.assertTrue(payload["found"])
        self.assertEqual(payload["drug"], "Headache-Drug")
        self.assertIn("disclaimer", payload)
        self.assertIn("FAERS", payload["source"])
        first = payload["signals"][0]
        for key in ("event", "prr", "prr_ci_low", "prr_ci_high", "ror",
                    "ror_ci_low", "ror_ci_high", "case_count", "flagged"):
            self.assertIn(key, first)

    def test_invalid_term_returns_not_found_without_network(self):
        payload = lookup_signals("<script>")
        self.assertFalse(payload["found"])
        self.assertEqual(payload["signals"], [])


class _FakeWFile:
    """Collects bytes a handler writes so a test can read the response body."""

    def __init__(self):
        self.chunks = []

    def write(self, data):
        self.chunks.append(data)

    def body(self):
        return b"".join(self.chunks)


class TestSignalEndpoint(unittest.TestCase):

    def _run(self, path):
        """Takes a request path. Returns the endpoint's headers and body
        without a network call, using a canned signal lookup."""
        import importlib

        api_signal = importlib.import_module("api.signal")
        tables = build_contingency_tables(DRUG_COUNTS, BACKGROUND_COUNTS)
        canned = shape_signal_payload("headache-drug", rank_signals(tables))
        original = api_signal.lookup_signals
        api_signal.lookup_signals = lambda term: canned
        try:
            worker = api_signal.handler.__new__(api_signal.handler)
            worker.path = path
            worker.wfile = _FakeWFile()
            worker.headers = {}
            worker.send_response = lambda code: worker.headers.setdefault(
                "status", code)
            worker.send_header = lambda key, value: worker.headers.__setitem__(
                key, value)
            worker.end_headers = lambda: None
            worker.do_GET()
            return worker.headers, json.loads(worker.wfile.body())
        finally:
            api_signal.lookup_signals = original

    def test_returns_json_with_the_documented_shape(self):
        headers, payload = self._run("/api/signal?name=headache-drug")
        self.assertEqual(headers["status"], 200)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertTrue(payload["found"])
        self.assertTrue(payload["signals"])
        first = payload["signals"][0]
        for key in ("event", "prr", "ror", "prr_ci_low", "prr_ci_high",
                    "case_count", "flagged"):
            self.assertIn(key, first)

    def test_caches_at_the_edge_for_a_day(self):
        headers, _ = self._run("/api/signal?name=headache-drug")
        self.assertIn("s-maxage=86400", headers["Cache-Control"])


class TestCardRendering(unittest.TestCase):

    def _app_js(self):
        """Returns the shared frontend script source."""
        root = Path(__file__).resolve().parents[1]
        return (root / "assets" / "app.js").read_text()

    def test_card_renders_the_signal_disclaimer_line(self):
        source = self._app_js()
        self.assertIn("signal-disclaimer", source)
        self.assertIn("info.disclaimer", source)

    def test_card_lists_prr_and_case_count(self):
        source = self._app_js()
        self.assertIn("Reported adverse event signals", source)
        self.assertIn("s.prr", source)
        self.assertIn("s.case_count", source)


if __name__ == "__main__":
    unittest.main()
