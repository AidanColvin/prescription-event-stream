import unittest

from src.drug_lookup import is_valid_term, shape_drug_info, trim_label_text

# A trimmed-down real openFDA label result, canned so no test needs a network.
ALPRAZOLAM_LABEL = {
    "indications_and_usage": [
        "1 INDICATIONS AND USAGE Alprazolam tablets are indicated for the "
        "acute treatment of generalized anxiety disorder and the treatment "
        "of panic disorder, with or without agoraphobia, in adults."
    ],
    "contraindications": [
        "4 CONTRAINDICATIONS Known hypersensitivity to alprazolam or other "
        "benzodiazepines. Concomitant use with strong CYP3A inhibitors."
    ],
    "drug_interactions": [
        "7 DRUG INTERACTIONS Opioids: profound sedation, respiratory "
        "depression, coma, and death may result."
    ],
    "pediatric_use": [
        "8.4 Pediatric Use The safety and effectiveness of alprazolam have "
        "not been established in pediatric patients."
    ],
    "mechanism_of_action": [
        "12.1 Mechanism of Action Alprazolam binds to the gamma-aminobutyric "
        "acid (GABA-A) receptor and enhances GABA-mediated inhibition."
    ],
    "openfda": {
        "generic_name": ["ALPRAZOLAM"],
        "brand_name": ["XANAX"],
        "pharm_class_epc": ["Benzodiazepine [EPC]"],
        "pharm_class_moa": ["Benzodiazepine Receptor Agonists [MoA]"],
    },
}


class TestTermValidation(unittest.TestCase):

    def test_accepts_ordinary_drug_names(self):
        for term in ["xanax", "metoprolol succinate", "st. john's wort", "co-trimoxazole"]:
            self.assertTrue(is_valid_term(term))

    def test_rejects_junk(self):
        for term in [None, "", "x", "a" * 80, "<script>", "name=1&x=2"]:
            self.assertFalse(is_valid_term(term))


class TestLabelTrimming(unittest.TestCase):

    def test_strips_numbered_section_headings(self):
        text = "1 INDICATIONS AND USAGE This drug treats hypertension."
        self.assertEqual(trim_label_text(text), "This drug treats hypertension.")

    def test_strips_title_case_headings_too(self):
        text = "12.1 Mechanism of Action Alprazolam binds to the GABA-A receptor."
        self.assertEqual(trim_label_text(text),
                         "Alprazolam binds to the GABA-A receptor.")
        text = "8.4 Pediatric Use Safety has not been established."
        self.assertEqual(trim_label_text(text),
                         "Safety has not been established.")

    def test_cuts_long_text_at_a_sentence_boundary(self):
        text = ("First sentence about the drug goes here and continues for a "
                "while to build length. Second sentence adds detail. " * 8)
        trimmed = trim_label_text(text, limit=200)
        self.assertLessEqual(len(trimmed), 201)
        self.assertTrue(trimmed.endswith("."))

    def test_returns_none_for_empty(self):
        self.assertIsNone(trim_label_text(None))
        self.assertIsNone(trim_label_text(""))


class TestShaping(unittest.TestCase):

    def test_shapes_a_real_label(self):
        info = shape_drug_info(ALPRAZOLAM_LABEL)
        self.assertTrue(info["found"])
        self.assertEqual(info["generic_name"], "Alprazolam")
        self.assertEqual(info["brand_name"], "Xanax")
        self.assertEqual(info["drug_class"], "Benzodiazepine")
        self.assertIn("GABA", info["mechanism"])
        self.assertIn("panic disorder", info["approved_uses"])
        self.assertNotIn("[EPC]", info["drug_class"])
        self.assertNotIn("4 CONTRAINDICATIONS", info["contraindications"])
        self.assertIn("dailymed.nlm.nih.gov", info["dailymed_url"])

    def test_falls_back_to_moa_class_when_no_mechanism_text(self):
        label = dict(ALPRAZOLAM_LABEL)
        label.pop("mechanism_of_action")
        info = shape_drug_info(label)
        self.assertIn("Benzodiazepine Receptor Agonists", info["mechanism"])

    def test_returns_none_without_any_name(self):
        self.assertIsNone(shape_drug_info({"openfda": {}}))


if __name__ == "__main__":
    unittest.main()
