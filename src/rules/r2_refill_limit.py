"""R2. Authorized refills exceed the federal limit for the schedule.

Two failures live here because both come from the same statute. A
Schedule II prescription may not be refilled. A Schedule III through V
prescription may be refilled five times, and only within six months of
issue, which caps the total days one document can authorize.
"""

from src.constants.controlled_schedules import (
    CFR_SOURCE_URL,
    SCHEDULE_LIMITS,
    normalize_schedule,
)
from src.rules.clinical_math import days_supply, total_days_authorized
from src.rules.types import make_finding

RULE_ID = "R2"


def check_schedule_refill_limit(event):
    """Given a prescription event, returns a Finding when the authorized
    refills or the total days supply exceed the federal limit for that
    schedule. Returns None for uncontrolled drugs and compliant ones."""
    schedule = normalize_schedule(event.get("dea_schedule"))
    if schedule is None:
        return None

    limits = SCHEDULE_LIMITS[schedule]
    refills = max(0, int(event.get("refills") or 0))
    quantity = event.get("quantity")
    sig = event.get("sig")

    if refills > limits["max_refills"]:
        return make_finding(
            rule_id=RULE_ID,
            severity="blocked",
            headline=f"{refills} refills authorized on a {schedule} prescription.",
            pharmacist_message=(
                f"{schedule} permits {limits['max_refills']} refills. This "
                f"prescription authorizes {refills}."
            ),
            patient_message=(
                "This prescription lists more refills than the law allows for "
                "this medication. The pharmacy has to confirm it first."
            ),
            prescriber_message=(
                f"Refill count of {refills} exceeds the {schedule} limit of "
                f"{limits['max_refills']}."
            ),
            citation=limits["citation"],
            citation_url=CFR_SOURCE_URL,
            suggested_action="Return to the prescriber for a corrected prescription.",
            evidence={
                "schedule": schedule,
                "refills_authorized": refills,
                "refills_allowed": limits["max_refills"],
            },
        )

    window = limits["max_days_from_issue"]
    if window is None:
        return None

    authorized_days = total_days_authorized(quantity, sig, refills)
    if authorized_days is None or authorized_days <= window:
        return None

    per_fill = days_supply(quantity, sig)
    fills = refills + 1

    return make_finding(
        rule_id=RULE_ID,
        severity="blocked",
        headline=f"{authorized_days} days authorized on a {schedule} prescription.",
        pharmacist_message=(
            f"Quantity {quantity} lasts {per_fill} days. {fills} fills covers "
            f"{authorized_days} days. {schedule} refills expire {window} days "
            f"after the issue date, so the later fills are not dispensable."
        ),
        patient_message=(
            "This prescription covers more time than the law allows before it "
            "has to be rewritten. Ask the prescriber for a new one."
        ),
        prescriber_message=(
            f"Quantity {quantity} with {refills} refills authorizes "
            f"{authorized_days} days. The {schedule} window is {window} days."
        ),
        citation=limits["citation"],
        citation_url=CFR_SOURCE_URL,
        suggested_action="Reduce the quantity or the refill count, then reissue.",
        evidence={
            "schedule": schedule,
            "days_per_fill": per_fill,
            "fills_authorized": fills,
            "total_days_authorized": authorized_days,
            "days_allowed": window,
        },
    )
