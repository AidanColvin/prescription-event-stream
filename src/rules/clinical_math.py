"""Age, sig parsing, and days-supply arithmetic used by the rules."""

import re
from datetime import date, datetime


def age_in_years(dob, as_of=None):
    """Takes an ISO date of birth and returns whole years, or None."""
    if not dob:
        return None
    try:
        born = datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        return None
    today = as_of or date.today()
    years = today.year - born.year
    if (today.month, today.day) < (born.month, born.day):
        years -= 1
    return years


def doses_per_day_from_sig(sig):
    """Takes a sig and returns how many doses one day consumes.

    Reads the frequency, not the quantity: 'twice daily' is 2 whether the
    dose is one tablet or two.
    """
    text = (sig or "").lower()
    if re.search(r"four times|every 6 hours|q6h", text):
        return 4
    if re.search(r"three times|every 8 hours|q8h|tid", text):
        return 3
    if re.search(r"twice|two times|every 12 hours|q12h|bid", text):
        return 2
    return 1


def units_per_dose_from_sig(sig):
    """Takes a sig and returns tablets or capsules consumed per dose."""
    match = re.search(r"take\s+(\d+)", (sig or "").lower())
    return int(match.group(1)) if match else 1


def days_supply(quantity, sig):
    """Takes a quantity and sig and returns how many days one fill lasts."""
    if not isinstance(quantity, (int, float)) or quantity <= 0:
        return None
    per_day = doses_per_day_from_sig(sig) * units_per_dose_from_sig(sig)
    return round(quantity / per_day)


def total_days_authorized(quantity, sig, refills):
    """Takes one fill's quantity and the refill count and returns total days."""
    per_fill = days_supply(quantity, sig)
    if per_fill is None:
        return None
    return per_fill * (refills + 1)
