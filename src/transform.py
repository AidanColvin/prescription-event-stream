"""Transformations applied to raw refill events before serving them."""

LARGE_REFILL_THRESHOLD = 60


def flag_high_quantity(event):
    """Return a copy of the event with the large-refill compliance flag set."""
    flagged = dict(event)
    flagged["is_large_refill"] = event.get("quantity", 0) > LARGE_REFILL_THRESHOLD
    flagged["high_volume"] = "Review Required" if flagged["is_large_refill"] else "Standard"
    return flagged


def transform_batch(batch):
    """Apply compliance flags to every event in a batch."""
    return [flag_high_quantity(event) for event in batch]


def process_events(events):
    """Flag a batch and compute summary stats for the API response."""
    processed = transform_batch(events)
    total = len(processed)
    large_refills = sum(1 for e in processed if e["is_large_refill"])
    quantity_sum = sum(e.get("quantity", 0) for e in processed)
    return {
        "events": processed,
        "stats": {
            "total": total,
            "large_refills": large_refills,
            "avg_quantity": round(quantity_sum / total) if total else 0,
        },
    }
