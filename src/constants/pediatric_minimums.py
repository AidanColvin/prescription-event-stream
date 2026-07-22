"""Approved minimum ages, keyed by generic name in lowercase.

Sourced from the DailyMed Structured Product Label, section 8.4
Pediatric Use, for each drug. Only drugs with an encoded floor are
checked; absence from this table means R1 stays silent.
"""

DEFAULT_LABEL_SOURCE_URL = "https://dailymed.nlm.nih.gov/dailymed/"

PEDIATRIC_MINIMUM_AGE_YEARS = {
    "zolpidem tartrate": {
        "minimum_age_years": 18,
        "label_section": "DailyMed SPL 8.4 Pediatric Use",
        "label_finding": "Safety and effectiveness in pediatric patients "
                         "have not been established.",
    },
    "tramadol hcl": {
        "minimum_age_years": 12,
        "label_section": "DailyMed SPL 8.4 Pediatric Use",
        "label_finding": "Contraindicated in children younger than 12 years.",
    },
}
