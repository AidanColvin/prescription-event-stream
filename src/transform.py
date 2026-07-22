def process_events(events):
    """Processes prescription events, flags high volume, and calculates metrics."""
    processed = []
    total_qty = 0
    large_count = 0
    
    for ev in events:
        qty = ev["quantity"]
        is_large = qty > 60
        if is_large:
            large_count += 1
        total_qty += qty
        
        item = ev.copy()
        item["high_volume"] = "Review Required" if is_large else "Standard"
        processed.append(item)
        
    avg_qty = round(total_qty / len(events)) if events else 0
    stats = {
        "total": len(events),
        "large_refills": large_count,
        "avg_quantity": avg_qty
    }
    return {"events": processed, "stats": stats}
