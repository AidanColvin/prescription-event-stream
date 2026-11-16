import json
import unittest
from pathlib import Path

from src.constants.pubmed_evidence import PUBMED_SELECTION_NOTE
from src.pubmed import (
    PubmedRef,
    attach_references,
    parse_esearch_ids,
    parse_esummary_refs,
    refs_to_json,
    shape_reference,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(name):
    """Takes a fixture stem. Returns its parsed JSON payload."""
    return json.loads((FIXTURES / f"{name}.json").read_text())


ESEARCH = _fixture("pubmed_esearch")
ESUMMARY = _fixture("pubmed_esummary")


class TestEsearchParsing(unittest.TestCase):

    def test_pulls_the_id_list_in_order(self):
        ids = parse_esearch_ids(ESEARCH)
        self.assertEqual(ids[0], "37000001")
        self.assertEqual(len(ids), 5)

    def test_returns_empty_when_no_results(self):
        self.assertEqual(parse_esearch_ids({"esearchresult": {}}), [])
        self.assertEqual(parse_esearch_ids({}), [])


class TestReferenceShaping(unittest.TestCase):

    def test_shapes_title_journal_year_and_url(self):
        entry = ESUMMARY["result"]["37000001"]
        ref = shape_reference("37000001", entry)
        self.assertEqual(ref.title,
                         "Sertraline for major depressive disorder: "
                         "a systematic review")
        self.assertEqual(ref.journal, "The Lancet Psychiatry")
        self.assertEqual(ref.year, "2023")
        self.assertEqual(ref.url, "https://pubmed.ncbi.nlm.nih.gov/37000001/")

    def test_falls_back_to_source_when_no_full_journal(self):
        ref = shape_reference("35900003", ESUMMARY["result"]["35900003"])
        self.assertEqual(ref.journal, "Am J Psychiatry")
        self.assertEqual(ref.year, "2022")

    def test_returns_none_for_a_titleless_entry(self):
        self.assertIsNone(
            shape_reference("35100004", ESUMMARY["result"]["35100004"]))


class TestSummaryParsing(unittest.TestCase):

    def test_keeps_order_and_drops_titleless_entries(self):
        ids = parse_esearch_ids(ESEARCH)
        refs = parse_esummary_refs(ESUMMARY, ids)
        self.assertEqual([r.pmid for r in refs],
                         ["37000001", "36500002", "35900003", "34700005"])
        self.assertTrue(all(isinstance(r, PubmedRef) for r in refs))

    def test_json_shape_carries_the_link_fields(self):
        refs = parse_esummary_refs(ESUMMARY, parse_esearch_ids(ESEARCH))
        payload = refs_to_json(refs)
        first = payload[0]
        for key in ("pmid", "title", "journal", "year", "url"):
            self.assertIn(key, first)
        self.assertTrue(first["url"].endswith("/37000001/"))


class TestAttachReferences(unittest.TestCase):

    def test_leaves_a_not_found_result_untouched(self):
        result = {"found": False}
        self.assertEqual(attach_references(result), {"found": False})

    def test_attaches_references_and_note(self):
        refs = refs_to_json(
            parse_esummary_refs(ESUMMARY, parse_esearch_ids(ESEARCH)))

        import src.pubmed as pubmed

        original = pubmed.fetch_references
        pubmed.fetch_references = lambda drug: refs
        try:
            result = pubmed.attach_references(
                {"found": True, "generic_name": "Sertraline"})
        finally:
            pubmed.fetch_references = original
        self.assertEqual(result["references"], refs)
        self.assertEqual(result["references_note"], PUBMED_SELECTION_NOTE)


class TestCardRendering(unittest.TestCase):

    def _app_js(self):
        root = Path(__file__).resolve().parents[1]
        return (root / "assets" / "app.js").read_text()

    def test_card_renders_the_evidence_list_and_note(self):
        source = self._app_js()
        self.assertIn("Peer-reviewed evidence", source)
        self.assertIn("references_note", source)

    def test_pubmed_article_url_is_defined(self):
        root = Path(__file__).resolve().parents[1]
        constants = (root / "src" / "constants" / "pubmed_evidence.py").read_text()
        self.assertIn("pubmed.ncbi.nlm.nih.gov", constants)

    def test_row_detail_includes_the_reference_section(self):
        root = Path(__file__).resolve().parents[1]
        index = (root / "index.html").read_text()
        self.assertIn("referenceSection(ev.medication, render)", index)


if __name__ == "__main__":
    unittest.main()
