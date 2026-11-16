"""Deterministic synthetic prescription events for the scale benchmark.

The generator clones the family's curated events for their full schema,
then swaps in a weighted tail of other generic names and mutates the
rule-relevant fields so a planned fraction of events trips each rule.
Given the same seed it returns the same events every run.

    python3 scripts/generate_synthetic.py [count] [seed]
"""

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.constants.synthetic_roster import (
    INVALID_DEA_NUMBER,
    MED_EVENTS_PER_PATIENT,
    R1_DRUG,
    R1_VIOLATION_FRACTION,
    R2_DRUG,
    R2_VIOLATION_FRACTION,
    R3_DRUG,
    R3_VIOLATION_FRACTION,
    TAIL_DRUG_FRACTION,
    TAIL_DRUG_NAMES,
)
from src.ingestion import get_refill_events

VALID_DEA_NUMBER = "BJ8839207"
_ADULT_DOB = "1975-06-15"
_CHILD_DOB = "2016-05-01"


def _violation_plan(n: int) -> "list[str]":
    """Takes a count. Returns one rule label per event: R1, R2, R3, or clean."""
    r1 = round(n * R1_VIOLATION_FRACTION)
    r2 = round(n * R2_VIOLATION_FRACTION)
    r3 = round(n * R3_VIOLATION_FRACTION)
    clean = n - r1 - r2 - r3
    return ["R1"] * r1 + ["R2"] * r2 + ["R3"] * r3 + ["clean"] * clean


def _pick_drug(base: dict, rng: random.Random) -> dict:
    """Takes a template and returns it with a tail drug name sometimes swapped in."""
    if rng.random() < TAIL_DRUG_FRACTION:
        name = rng.choice(TAIL_DRUG_NAMES)
        base["medication"] = name
        base["brand"] = name
    return base


def _make_clean(event: dict, rng: random.Random) -> dict:
    """Takes an event and returns it shaped to trip no rule."""
    event = _pick_drug(event, rng)
    event["dob"] = _ADULT_DOB
    event["dea_schedule"] = "Non-controlled"
    event["dea"] = "None (Non-controlled)"
    event["refills"] = rng.randint(0, 5)
    event["quantity"] = rng.choice([30, 60, 90])
    return event


def _make_r1(event: dict) -> dict:
    """Takes an event and returns an R1 violation: a child on an adult drug."""
    event["medication"] = R1_DRUG
    event["brand"] = "Ambien"
    event["dob"] = _CHILD_DOB
    event["dea_schedule"] = "Schedule IV"
    event["dea"] = VALID_DEA_NUMBER
    event["refills"] = 2
    event["quantity"] = 30
    event["sig"] = "Take 1 tablet by mouth at bedtime."
    return event


def _make_r2(event: dict) -> dict:
    """Takes an event and returns an R2 violation: too many refills."""
    event["medication"] = R2_DRUG
    event["brand"] = "Restoril"
    event["dob"] = _ADULT_DOB
    event["dea_schedule"] = "Schedule IV"
    event["dea"] = VALID_DEA_NUMBER
    event["refills"] = 8
    event["quantity"] = 30
    event["sig"] = "Take 1 capsule by mouth at bedtime."
    return event


def _make_r3(event: dict) -> dict:
    """Takes an event and returns an R3 violation: a bad DEA registration."""
    event["medication"] = R3_DRUG
    event["brand"] = "Ultram"
    event["dob"] = _ADULT_DOB
    event["dea_schedule"] = "Schedule IV"
    event["dea"] = INVALID_DEA_NUMBER
    event["refills"] = 1
    event["quantity"] = 30
    event["sig"] = "Take 1 tablet by mouth every 6 hours as needed for pain."
    return event


def _shape_event(base: dict, kind: str, index: int, patient_count: int,
                 rng: random.Random) -> dict:
    """Takes a template, a rule label, a position, and the patient count.
    Returns one event assigned to a patient with a bounded regimen."""
    event = dict(base)
    event["event_id"] = f"SYN-{index:07d}"
    event["patient"] = f"Synthetic Patient {index % patient_count:06d}"
    if kind == "R1":
        return _make_r1(event)
    if kind == "R2":
        return _make_r2(event)
    if kind == "R3":
        return _make_r3(event)
    return _make_clean(event, rng)


def generate_events(n: int, seed: int) -> "list[dict]":
    """Takes a count and a seed. Returns n deterministic synthetic events
    matching the ingestion schema, drawn from the curated set plus a
    weighted tail, with a planned fraction tripping each rule."""
    rng = random.Random(seed)
    templates = get_refill_events()
    plan = _violation_plan(n)
    rng.shuffle(plan)
    patient_count = max(1, n // MED_EVENTS_PER_PATIENT)
    return [_shape_event(rng.choice(templates), kind, i, patient_count, rng)
            for i, kind in enumerate(plan)]


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    events = generate_events(count, seed)
    print(f"generated {len(events)} events with seed {seed}")
    print(f"first event id: {events[0]['event_id']}")
