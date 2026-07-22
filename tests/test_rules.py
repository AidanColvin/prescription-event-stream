import unittest
from datetime import date

from src.ingestion import get_refill_events
from src.rules import evaluate_event, run_rules, summarize_queue
from src.rules.clinical_math import (
    age_in_years,
    days_supply,
    doses_per_day_from_sig,
    total_days_authorized,
)
from src.rules.r1_pediatric import check_pediatric_contraindication
from src.rules.r2_refill_limit import check_schedule_refill_limit
from src.rules.r3_dea_validity import check_dea_validity, is_valid_dea_number
from src.constants.controlled_schedules import normalize_schedule
from src.transform import process_events

AS_OF = date(2026, 7, 21)
VALID_DEA = "BJ8839207"


def zolpidem_event(**overrides):
    """Returns a Schedule IV zolpidem event with fields overridable by test."""
    event = {
        "event_id": "EVT-TEST",
        "patient": "Test Patient",
        "dob": "1980-01-01",
        "medication": "Zolpidem Tartrate",
        "brand": "Ambien",
        "sig": "Take 1 tablet by mouth at bedtime.",
        "quantity": 30,
        "refills": 2,
        "dea_schedule": "Schedule IV",
        "prescriber": "Dr. Sarah Jenkins, MD",
        "dea": VALID_DEA,
    }
    event.update(overrides)
    return event


class TestR1Pediatric(unittest.TestCase):

    def test_catches_an_eleven_year_old_on_zolpidem(self):
        finding = check_pediatric_contraindication(
            zolpidem_event(patient="James Smith", dob="2015-02-14"), AS_OF)
        self.assertEqual(finding["rule_id"], "R1")
        self.assertEqual(finding["severity"], "blocked")
        self.assertEqual(finding["evidence"]["patient_age_years"], 11)

    def test_names_the_patient_from_the_event(self):
        finding = check_pediatric_contraindication(
            zolpidem_event(patient="Rosa Ibarra", dob="2016-03-01"), AS_OF)
        self.assertIn("Rosa Ibarra", finding["headline"])
        self.assertNotIn("James Smith", finding["headline"])

    def test_passes_an_adult_on_the_same_drug(self):
        self.assertIsNone(
            check_pediatric_contraindication(zolpidem_event(), AS_OF))

    def test_ignores_a_drug_with_no_age_floor(self):
        event = zolpidem_event(medication="Amoxicillin", dob="2015-02-14")
        self.assertIsNone(check_pediatric_contraindication(event, AS_OF))

    def test_counts_a_birthday_that_has_not_arrived_yet(self):
        self.assertEqual(age_in_years("2015-08-01", AS_OF), 10)
        self.assertEqual(age_in_years("2015-07-21", AS_OF), 11)


class TestR2RefillLimit(unittest.TestCase):

    def test_catches_the_four_hundred_fifty_day_supply(self):
        finding = check_schedule_refill_limit(
            zolpidem_event(quantity=90, refills=4))
        self.assertEqual(finding["evidence"]["total_days_authorized"], 450)
        self.assertEqual(finding["evidence"]["days_allowed"], 180)

    def test_divides_by_doses_per_day(self):
        finding = check_schedule_refill_limit(zolpidem_event(
            quantity=90, refills=4, sig="Take 1 tablet by mouth twice daily."))
        self.assertEqual(finding["evidence"]["total_days_authorized"], 225)

    def test_catches_a_refill_count_over_five(self):
        finding = check_schedule_refill_limit(zolpidem_event(refills=7))
        self.assertEqual(finding["evidence"]["refills_authorized"], 7)

    def test_catches_any_refill_on_schedule_two(self):
        finding = check_schedule_refill_limit(
            zolpidem_event(dea_schedule="Schedule II", refills=1))
        self.assertEqual(finding["evidence"]["refills_allowed"], 0)

    def test_passes_a_compliant_schedule_four_prescription(self):
        self.assertIsNone(check_schedule_refill_limit(zolpidem_event()))

    def test_ignores_an_uncontrolled_drug(self):
        event = zolpidem_event(dea_schedule="Non-controlled", refills=11)
        self.assertIsNone(check_schedule_refill_limit(event))

    def test_normalizes_schedule_text(self):
        self.assertEqual(normalize_schedule("Schedule IV"), "CIV")
        self.assertIsNone(normalize_schedule("Non-controlled"))


class TestR3DeaValidity(unittest.TestCase):

    def test_catches_a_missing_registration(self):
        event = zolpidem_event(prescriber="Dr. Robert Chen, DO",
                               dea="None (Non-controlled)")
        self.assertEqual(check_dea_validity(event)["rule_id"], "R3")

    def test_catches_a_failed_check_digit(self):
        finding = check_dea_validity(zolpidem_event(dea="MH5502841"))
        self.assertIn("does not validate", finding["headline"])

    def test_passes_a_valid_registration(self):
        self.assertIsNone(check_dea_validity(zolpidem_event()))

    def test_ignores_an_uncontrolled_drug(self):
        event = zolpidem_event(dea_schedule="Non-controlled", dea="")
        self.assertIsNone(check_dea_validity(event))

    def test_checks_format_prefix_and_check_digit(self):
        self.assertTrue(is_valid_dea_number("BJ8839207"))
        self.assertFalse(is_valid_dea_number("BJ8839201"))
        self.assertFalse(is_valid_dea_number("BJ883920"))
        self.assertFalse(is_valid_dea_number("ZZ8839207"))
        self.assertFalse(is_valid_dea_number(None))


class TestClinicalMath(unittest.TestCase):

    def test_reads_frequency_from_a_sig(self):
        self.assertEqual(doses_per_day_from_sig("Take 1 tablet at bedtime."), 1)
        self.assertEqual(doses_per_day_from_sig("Take 1 tablet twice daily."), 2)
        self.assertEqual(doses_per_day_from_sig("Take 1 tablet three times a day."), 3)

    def test_accounts_for_units_per_dose(self):
        self.assertEqual(days_supply(60, "Take 2 tablets once daily."), 30)

    def test_counts_the_first_fill_plus_refills(self):
        self.assertEqual(
            total_days_authorized(90, "Take 1 tablet at bedtime.", 4), 450)


class TestQueue(unittest.TestCase):

    def test_the_demo_queue_stops_exactly_three(self):
        evaluated = [evaluate_event(e) for e in get_refill_events()]
        summary = summarize_queue(evaluated)
        self.assertEqual(summary["stopped"], 3)
        self.assertEqual(summary["cleared"], summary["read"] - summary["stopped"])

        stopped = {e["patient"]: sorted(f["rule_id"] for f in e["findings"])
                   for e in evaluated if e["severity"] != "clear"}
        self.assertEqual(stopped["James Smith"], ["R1", "R2"])

    def test_the_payload_carries_a_computed_summary(self):
        payload = process_events(get_refill_events())
        self.assertEqual(payload["summary"]["read"], len(payload["events"]))
        self.assertIn("dea_status", payload["events"][0])

    def test_rule_ids_are_unique_per_event(self):
        for event in get_refill_events():
            ids = [f["rule_id"] for f in run_rules(event)]
            self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
