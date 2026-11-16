import unittest
from collections import Counter

from scripts.generate_synthetic import generate_events
from src.constants.synthetic_roster import (
    R1_VIOLATION_FRACTION,
    R2_VIOLATION_FRACTION,
    R3_VIOLATION_FRACTION,
)
from src.ingestion import get_refill_events
from src.rules import run_rules

SEED = 42
TOLERANCE = 0.01


def _rule_fractions(events):
    """Takes events. Returns the fraction tripping each rule id."""
    counts = Counter()
    for event in events:
        for rule_id in {f["rule_id"] for f in run_rules(event)}:
            counts[rule_id] += 1
    return {rule: counts[rule] / len(events) for rule in ("R1", "R2", "R3")}


class TestDeterminism(unittest.TestCase):

    def test_same_seed_gives_identical_events(self):
        self.assertEqual(generate_events(2000, SEED),
                         generate_events(2000, SEED))

    def test_different_seed_gives_different_events(self):
        self.assertNotEqual(generate_events(2000, SEED),
                            generate_events(2000, SEED + 1))


class TestSchema(unittest.TestCase):

    def test_matches_the_ingestion_schema(self):
        reference = set(get_refill_events()[0].keys())
        for event in generate_events(1000, SEED):
            self.assertEqual(set(event.keys()), reference)

    def test_event_ids_are_unique(self):
        events = generate_events(5000, SEED)
        self.assertEqual(len({e["event_id"] for e in events}), len(events))


class TestViolationFractions(unittest.TestCase):

    def test_each_rule_fires_at_its_planned_fraction(self):
        fractions = _rule_fractions(generate_events(10000, SEED))
        self.assertAlmostEqual(fractions["R1"], R1_VIOLATION_FRACTION,
                               delta=TOLERANCE)
        self.assertAlmostEqual(fractions["R2"], R2_VIOLATION_FRACTION,
                               delta=TOLERANCE)
        self.assertAlmostEqual(fractions["R3"], R3_VIOLATION_FRACTION,
                               delta=TOLERANCE)

    def test_the_bulk_of_events_clear_every_rule(self):
        events = generate_events(2000, SEED)
        clean = sum(1 for e in events if not run_rules(e))
        self.assertGreater(clean / len(events), 0.80)


if __name__ == "__main__":
    unittest.main()
