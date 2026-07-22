"""Transform: evaluates every event against the rule engine and shapes
the API payload the four surfaces render."""

from src.rules import evaluate_event, summarize_queue
from src.rules.r3_dea_validity import is_valid_dea_number
from src.constants.controlled_schedules import normalize_schedule

LARGE_REFILL_THRESHOLD = 60


def flag_high_quantity(event):
    """Takes an event and returns a copy with the large-refill flag set."""
    out = dict(event)
    out["is_large_refill"] = out.get("quantity", 0) > LARGE_REFILL_THRESHOLD
    out["high_volume"] = "Review Required" if out["is_large_refill"] else "Standard"
    return out


def transform_batch(events):
    """Takes a batch of events and returns each with the large-refill flag."""
    return [flag_high_quantity(event) for event in events]


def dea_status(event):
    """Takes an event and returns how its DEA registration checks out:
    not_required, missing, invalid, or valid."""
    if normalize_schedule(event.get("dea_schedule")) is None:
        return "not_required"
    raw = (event.get("dea") or "").strip()
    normalized = raw.split("(")[0].strip()
    if not normalized or normalized.lower() in {"none", "n/a", "na", "null", "-"}:
        return "missing"
    return "valid" if is_valid_dea_number(normalized) else "invalid"


def process_events(events):
    """Takes raw events, runs every rule on each, and returns the payload
    the frontend renders. Every count in the payload is computed here;
    nothing a screen shows is hardcoded.

    Each event keeps a nested `patient_data` block for surfaces that read
    the older shape, alongside the flat fields.
    """
    evaluated = [evaluate_event(e) for e in transform_batch(events)]
    for event in evaluated:
        event["dea_status"] = dea_status(event)
        event["patient_data"] = {
            "name": event.get("patient", ""),
            "dob": event.get("dob", ""),
            "adherence_score": event.get("adherence_score", ""),
        }

    total = len(evaluated)
    large = sum(1 for e in evaluated if e["is_large_refill"])
    quantities = [e.get("quantity", 0) for e in evaluated]
    avg_quantity = round(sum(quantities) / total) if total else 0

    return {
        "events": evaluated,
        "summary": summarize_queue(evaluated),
        "stats": {
            "total": total,
            "large_refills": large,
            "avg_quantity": avg_quantity,
        },
    }
