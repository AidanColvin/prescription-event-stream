"""Thresholds for flagging a pharmacovigilance disproportionality signal.

The criteria follow Evans SJ, Waller PC, Davis S (2001), "Use of
proportional reporting ratios (PRRs) for signal generation from
spontaneous adverse drug reaction reports", Pharmacoepidemiology and
Drug Safety 10:483-486. A signal requires all three: PRR of at least 2,
chi-square of at least 4, and at least 3 reported cases.
"""

PRR_SIGNAL_MINIMUM: float = 2.0
CHI_SQUARE_SIGNAL_MINIMUM: float = 4.0
CASE_COUNT_SIGNAL_MINIMUM: int = 3

# Two-sided z value for a 95 percent confidence interval.
CONFIDENCE_Z_95: float = 1.96

# How many adverse events the signal endpoint reports per drug.
TOP_SIGNALS_LIMIT: int = 5

# Seconds to pause between openFDA calls, respecting the public rate
# limit of 240 requests per minute without an API key.
OPENFDA_RATE_LIMIT_SLEEP_SECONDS: float = 0.3
