"""R3. Prescriber DEA registration missing or invalid for the schedule.

The DEA number carries its own check digit: sum the first, third, and
fifth digits, add twice the sum of the second, fourth, and sixth, and the
last digit of the total must match the seventh digit.
"""

import re

from src.constants.controlled_schedules import (
    CFR_SOURCE_URL,
    VALID_DEA_PREFIX_LETTERS,
    normalize_schedule,
)
from src.rules.types import make_finding

RULE_ID = "R3"

# Values the stream uses when no registration is on file.
_MISSING_DEA_VALUES = frozenset({"", "none", "n/a", "na", "null", "-"})


def validate_dea_checksum(candidate):
    """Takes a normalized DEA number and returns True when the check digit
    matches. Expects two letters followed by seven digits."""
    if not re.fullmatch(r"[A-Z]{2}\d{7}", candidate):
        return False
    digits = [int(c) for c in candidate[2:]]
    total = (digits[0] + digits[2] + digits[4]) + 2 * (digits[1] + digits[3] + digits[5])
    return total % 10 == digits[6]


def is_valid_dea_number(raw):
    """Takes a DEA number and returns True when format, prefix, and
    checksum all pass."""
    if not isinstance(raw, str):
        return False
    candidate = raw.strip().upper().replace(" ", "")
    if not candidate or candidate[0] not in VALID_DEA_PREFIX_LETTERS:
        return False
    return validate_dea_checksum(candidate)


def check_dea_validity(event):
    """Given a prescription event for a controlled substance, returns a
    Finding when the prescriber has no DEA registration on file or when the
    registration fails its checksum. Returns None otherwise."""
    schedule = normalize_schedule(event.get("dea_schedule"))
    if schedule is None:
        return None

    prescriber = event.get("prescriber") or "The prescriber"
    raw = (event.get("dea") or "").strip()
    normalized = re.sub(r"\(.*?\)", "", raw).strip()

    if normalized.lower() in _MISSING_DEA_VALUES:
        return make_finding(
            rule_id=RULE_ID,
            severity="blocked",
            headline=f"{prescriber} has no DEA registration on file.",
            pharmacist_message=(
                f"A {schedule} prescription requires a valid DEA registration. "
                f"None is recorded for this prescriber."
            ),
            patient_message=(
                "The pharmacy has to confirm the prescriber's federal "
                "registration before filling this one."
            ),
            prescriber_message=(
                f"No DEA registration is attached to this {schedule} prescription."
            ),
            citation="21 CFR 1306.03",
            citation_url=CFR_SOURCE_URL,
            suggested_action="Verify registration with the prescriber before dispensing.",
            evidence={"schedule": schedule, "dea_on_file": raw or None},
        )

    if is_valid_dea_number(normalized):
        return None

    return make_finding(
        rule_id=RULE_ID,
        severity="blocked",
        headline=f"DEA {normalized} does not validate.",
        pharmacist_message=(
            f"The registration on this {schedule} prescription fails the DEA "
            f"check digit. Either the number is transcribed wrong or it is "
            f"not a real registration."
        ),
        patient_message=(
            "The prescriber's federal registration number did not check out. "
            "The pharmacy is confirming it."
        ),
        prescriber_message=(
            f"DEA {normalized} fails checksum validation on a {schedule} "
            f"prescription."
        ),
        citation="21 CFR 1301.13",
        citation_url=CFR_SOURCE_URL,
        suggested_action="Reconfirm the registration number with the prescriber.",
        evidence={"schedule": schedule, "dea_on_file": normalized},
    )
