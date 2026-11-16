"""FAERS pharmacovigilance signal statistics.

The FDA Adverse Event Reporting System collects voluntary reports of
suspected adverse drug events. Disproportionality analysis asks whether
an event is reported for one drug more often than for all drugs, using
a 2x2 contingency table per drug and event pair. Network fetching and
the statistics are separate functions so the math is testable without
a network.
"""

import json
import math
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Mapping, Optional

from src.constants.signal_thresholds import (
    CASE_COUNT_SIGNAL_MINIMUM,
    CHI_SQUARE_SIGNAL_MINIMUM,
    CONFIDENCE_Z_95,
    OPENFDA_RATE_LIMIT_SLEEP_SECONDS,
    PRR_SIGNAL_MINIMUM,
    TOP_SIGNALS_LIMIT,
)
from src.drug_lookup import is_valid_term

FAERS_EVENT_URL = ("https://api.fda.gov/drug/event.json"
                   "?count=patient.reaction.reactionmeddrapt.exact&limit=1000")

FAERS_SOURCE = "FDA Adverse Event Reporting System (FAERS) via openFDA"

FAERS_DISCLAIMER = (
    "These are disproportionality signals computed from voluntary FAERS "
    "reports. They show reporting patterns, not proven causation.")


@dataclass(frozen=True)
class FaersCounts:
    """One drug and event pair's 2x2 contingency table.

    drug_event counts reports naming both the drug and the event.
    drug_no_event counts reports naming the drug without the event.
    event_no_drug counts reports naming the event without the drug.
    no_drug_no_event counts reports naming neither.
    """
    event: str
    drug_event: int
    drug_no_event: int
    event_no_drug: int
    no_drug_no_event: int


@dataclass(frozen=True)
class SignalStat:
    """One disproportionality statistic with its 95 percent interval."""
    statistic: str
    value: float
    ci_low: float
    ci_high: float
    case_count: int


def _get_json(url: str, timeout: int = 6) -> dict:
    """Takes a URL. Returns its parsed JSON response."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "prescription-event-stream-demo"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def fetch_reaction_counts(drug: Optional[str]) -> "dict[str, int]":
    """Takes a generic drug name, or None for all reports. Returns FAERS
    reaction counts keyed by MedDRA preferred term."""
    url = FAERS_EVENT_URL
    if drug:
        quoted = urllib.parse.quote(f'"{drug}"')
        url += f"&search=patient.drug.openfda.generic_name:{quoted}"
    try:
        payload = _get_json(url)
    except Exception:
        return {}
    results = payload.get("results") or []
    return {r["term"]: r["count"] for r in results
            if r.get("term") and isinstance(r.get("count"), int)}


def build_contingency_tables(drug_counts: "Mapping[str, int]",
                             background_counts: "Mapping[str, int]",
                             ) -> "list[FaersCounts]":
    """Takes reaction counts for one drug and for all reports. Returns a
    2x2 contingency table per event both tables can support."""
    drug_total = sum(drug_counts.values())
    background_total = sum(background_counts.values())
    tables = []
    for event, with_drug in drug_counts.items():
        background_event = background_counts.get(event)
        if background_event is None:
            continue
        drug_no_event = drug_total - with_drug
        event_no_drug = background_event - with_drug
        no_drug_no_event = (background_total - with_drug - drug_no_event
                            - event_no_drug)
        cells = (with_drug, drug_no_event, event_no_drug, no_drug_no_event)
        if any(cell <= 0 for cell in cells):
            continue
        tables.append(FaersCounts(event, *cells))
    return tables


def fetch_faers_counts(drug: str) -> "list[FaersCounts]":
    """Takes a generic drug name. Returns the 2x2 contingency counts for
    every adverse event reported with it, from two openFDA count queries
    spaced to respect the public rate limit."""
    drug_counts = fetch_reaction_counts(drug)
    if not drug_counts:
        return []
    time.sleep(OPENFDA_RATE_LIMIT_SLEEP_SECONDS)
    background_counts = fetch_reaction_counts(None)
    return build_contingency_tables(drug_counts, background_counts)


def compute_prr(counts: FaersCounts) -> SignalStat:
    """Takes contingency counts. Returns the proportional reporting ratio
    with its 95 percent interval from the log-scale standard error."""
    a, b = counts.drug_event, counts.drug_no_event
    c, d = counts.event_no_drug, counts.no_drug_no_event
    prr = (a / (a + b)) / (c / (c + d))
    standard_error = math.sqrt(1 / a - 1 / (a + b) + 1 / c - 1 / (c + d))
    spread = CONFIDENCE_Z_95 * standard_error
    return SignalStat(
        statistic="PRR",
        value=prr,
        ci_low=math.exp(math.log(prr) - spread),
        ci_high=math.exp(math.log(prr) + spread),
        case_count=a,
    )


def compute_ror(counts: FaersCounts) -> SignalStat:
    """Takes contingency counts. Returns the reporting odds ratio with
    its 95 percent interval from the log-scale standard error."""
    a, b = counts.drug_event, counts.drug_no_event
    c, d = counts.event_no_drug, counts.no_drug_no_event
    ror = (a * d) / (b * c)
    standard_error = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    spread = CONFIDENCE_Z_95 * standard_error
    return SignalStat(
        statistic="ROR",
        value=ror,
        ci_low=math.exp(math.log(ror) - spread),
        ci_high=math.exp(math.log(ror) + spread),
        case_count=a,
    )


def compute_chi_square(counts: FaersCounts) -> float:
    """Takes contingency counts. Returns the Yates-corrected chi-square
    statistic for the 2x2 table."""
    a, b = counts.drug_event, counts.drug_no_event
    c, d = counts.event_no_drug, counts.no_drug_no_event
    n = a + b + c + d
    deviation = abs(a * d - b * c) - n / 2
    if deviation < 0:
        deviation = 0
    denominator = (a + b) * (c + d) * (a + c) * (b + d)
    return n * deviation * deviation / denominator


def is_signal(prr_value: float, chi_square: float, case_count: int) -> bool:
    """Takes a PRR, a chi-square, and a case count. Returns True when all
    three meet the Evans 2001 signal criteria."""
    return (prr_value >= PRR_SIGNAL_MINIMUM
            and chi_square >= CHI_SQUARE_SIGNAL_MINIMUM
            and case_count >= CASE_COUNT_SIGNAL_MINIMUM)


def shape_signal(counts: FaersCounts) -> dict:
    """Takes one contingency table. Returns the JSON-ready signal entry
    with PRR, ROR, intervals, case count, and the flagged verdict."""
    prr = compute_prr(counts)
    ror = compute_ror(counts)
    chi_square = compute_chi_square(counts)
    return {
        "event": counts.event.title(),
        "prr": round(prr.value, 2),
        "prr_ci_low": round(prr.ci_low, 2),
        "prr_ci_high": round(prr.ci_high, 2),
        "ror": round(ror.value, 2),
        "ror_ci_low": round(ror.ci_low, 2),
        "ror_ci_high": round(ror.ci_high, 2),
        "chi_square": round(chi_square, 1),
        "case_count": counts.drug_event,
        "flagged": is_signal(prr.value, chi_square, counts.drug_event),
    }


def rank_signals(tables: "list[FaersCounts]",
                 limit: int = TOP_SIGNALS_LIMIT) -> "list[dict]":
    """Takes contingency tables. Returns the top signal entries by PRR,
    keeping only events with enough cases for a stable estimate."""
    stable = [t for t in tables if t.drug_event >= CASE_COUNT_SIGNAL_MINIMUM]
    shaped = [shape_signal(t) for t in stable]
    shaped.sort(key=lambda s: s["prr"], reverse=True)
    return shaped[:limit]


def shape_signal_payload(drug: str, signals: "list[dict]") -> dict:
    """Takes a drug name and its signal entries. Returns the payload the
    signal endpoint serves."""
    return {
        "found": bool(signals),
        "drug": drug.title(),
        "signals": signals,
        "disclaimer": FAERS_DISCLAIMER,
        "source": FAERS_SOURCE,
    }


def lookup_signals(term: str) -> dict:
    """Takes a search term. Returns the shaped signal payload for it, or
    a not-found payload when the term is invalid or FAERS has nothing."""
    term = (term or "").strip()
    if not is_valid_term(term):
        return shape_signal_payload(term, [])
    tables = fetch_faers_counts(term)
    return shape_signal_payload(term, rank_signals(tables))
