"""Federal refill limits per controlled-substance schedule.

21 CFR 1306.12 forbids refilling a Schedule II prescription. 21 CFR
1306.22 allows Schedule III through V prescriptions five refills within
six months of the issue date.
"""

CFR_SOURCE_URL = "https://www.ecfr.gov/current/title-21/chapter-II/part-1306"

# DEA registrant first letters that can appear on a valid registration.
VALID_DEA_PREFIX_LETTERS = frozenset("ABFGMPRX")

SCHEDULE_LIMITS = {
    "CII": {"max_refills": 0, "max_days_from_issue": None,
            "citation": "21 CFR 1306.12"},
    "CIII": {"max_refills": 5, "max_days_from_issue": 180,
             "citation": "21 CFR 1306.22"},
    "CIV": {"max_refills": 5, "max_days_from_issue": 180,
            "citation": "21 CFR 1306.22"},
    "CV": {"max_refills": 5, "max_days_from_issue": 180,
           "citation": "21 CFR 1306.22"},
}

_ALIASES = {
    "schedule ii": "CII", "c-ii": "CII", "cii": "CII", "ii": "CII",
    "schedule iii": "CIII", "c-iii": "CIII", "ciii": "CIII", "iii": "CIII",
    "schedule iv": "CIV", "c-iv": "CIV", "civ": "CIV", "iv": "CIV",
    "schedule v": "CV", "c-v": "CV", "cv": "CV", "v": "CV",
}


def normalize_schedule(raw):
    """Takes schedule text and returns CII, CIII, CIV, CV, or None."""
    text = (raw or "").strip().lower()
    return _ALIASES.get(text)
