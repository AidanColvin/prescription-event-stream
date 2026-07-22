"""R1. Patient age below the drug's approved minimum.

This is the rule that catches an eleven year old holding a prescription
for an adult hypnotic.
"""

from src.constants.pediatric_minimums import (
    DEFAULT_LABEL_SOURCE_URL,
    PEDIATRIC_MINIMUM_AGE_YEARS,
)
from src.rules.clinical_math import age_in_years
from src.rules.types import make_finding

RULE_ID = "R1"


def check_pediatric_contraindication(event, as_of=None):
    """Given a prescription event, returns a Finding if the patient is under
    the drug's approved minimum age. Returns None when the patient is old
    enough or when the drug has no encoded age floor."""
    generic = (event.get("medication") or "").strip().lower()
    limit = PEDIATRIC_MINIMUM_AGE_YEARS.get(generic)
    if not limit:
        return None

    age = event.get("age")
    if not isinstance(age, int):
        age = age_in_years(event.get("dob"), as_of)
    if age is None or age >= limit["minimum_age_years"]:
        return None

    patient = event.get("patient") or "This patient"
    brand = event.get("brand") or event.get("medication") or "This medication"
    minimum = limit["minimum_age_years"]

    return make_finding(
        rule_id=RULE_ID,
        severity="blocked",
        headline=f"{patient} is {age} years old.",
        pharmacist_message=(
            f"{brand} carries no approved pediatric indication. The label "
            f"establishes a minimum age of {minimum}. {limit['label_finding']}"
        ),
        patient_message=(
            f"{brand} is not approved for children. The pharmacy paused this "
            f"prescription until the prescriber confirms it."
        ),
        prescriber_message=(
            f"{patient}, age {age}, was prescribed {brand}. Approved minimum "
            f"age is {minimum}."
        ),
        citation=limit["label_section"],
        citation_url=DEFAULT_LABEL_SOURCE_URL,
        suggested_action="Call the prescriber before dispensing.",
        evidence={
            "patient_age_years": age,
            "minimum_age_years": minimum,
            "generic_name": generic,
        },
    )
