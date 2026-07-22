"""Drug-drug interaction screen.

Screens each patient's actual regimen — not the whole queue — for known
interacting pairs. An interaction is a property of two prescriptions in
one person, so the screen runs per patient and returns one finding per
pair, phrased for every audience.
"""

from itertools import combinations

from src.constants.drug_interactions import INTERACTION_SOURCE, interactions_for_pair

SEVERITY_ORDER = {"major": 0, "moderate": 1}


def screen_interactions(events):
    """Takes the event queue and returns interaction findings, worst first.

    Each finding names the patient, both prescriptions, the severity, the
    clinical and plain-language effect, and the suggested action.
    """
    by_patient = {}
    for event in events:
        by_patient.setdefault(event.get("patient", ""), []).append(event)

    findings = []
    for patient, meds in by_patient.items():
        for a, b in combinations(meds, 2):
            entry = interactions_for_pair(
                a.get("medication", ""), b.get("medication", ""))
            if entry is None:
                continue
            findings.append({
                "patient": patient,
                "severity": entry["severity"],
                "drug_a": a.get("medication"), "brand_a": a.get("brand"),
                "event_id_a": a.get("event_id"),
                "drug_b": b.get("medication"), "brand_b": b.get("brand"),
                "event_id_b": b.get("event_id"),
                "effect": entry["effect"],
                "plain_effect": entry["plain_effect"],
                "advice": entry["advice"],
                "source": INTERACTION_SOURCE,
            })

    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["patient"]))
    return findings


def attach_interaction_alerts(events, findings):
    """Takes events and screen findings and attaches per-event alerts.

    Each involved prescription gets an `interaction_alerts` list naming
    the other drug, so any surface can warn inline without re-screening.
    """
    for event in events:
        event["interaction_alerts"] = []
    by_id = {e.get("event_id"): e for e in events}
    for f in findings:
        for own, other_drug, other_brand in (
            (f["event_id_a"], f["drug_b"], f["brand_b"]),
            (f["event_id_b"], f["drug_a"], f["brand_a"]),
        ):
            event = by_id.get(own)
            if event is not None:
                event["interaction_alerts"].append({
                    "with_medication": other_drug,
                    "with_brand": other_brand,
                    "severity": f["severity"],
                    "effect": f["effect"],
                    "plain_effect": f["plain_effect"],
                    "advice": f["advice"],
                })
    return events
