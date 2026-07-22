def transform_events(events):
    total = len(events)
    large = sum(1 for e in events if e["quantity"] > 60)
    qty = sum(e["quantity"] for e in events)
    return {
        "events": events,
        "stats": {
            "total": total,
            "large_refills": large,
            "avg_quantity": round(qty / total, 1) if total > 0 else 0
        }
    }
