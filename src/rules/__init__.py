"""Rule engine entry point.

Adding a rule means writing one function and appending it to REGISTERED_RULES.
"""

from src.rules.r1_pediatric import check_pediatric_contraindication
from src.rules.r2_refill_limit import check_schedule_refill_limit
from src.rules.r3_dea_validity import check_dea_validity
from src.rules.types import SEVERITY_RANK, highest_severity, verdict_for

REGISTERED_RULES = (
    check_pediatric_contraindication,
    check_schedule_refill_limit,
    check_dea_validity,
)


def run_rules(event):
    """Takes one prescription event and returns every Finding it trips."""
    findings = []
    for rule in REGISTERED_RULES:
        finding = rule(event)
        if finding is not None:
            findings.append(finding)
    return findings


def evaluate_event(event):
    """Takes an event and returns it with severity, verdict, and findings."""
    findings = run_rules(event)
    severity = highest_severity(findings)
    out = dict(event)
    out["severity"] = severity
    out["verdict"] = verdict_for(severity)
    out["findings"] = findings
    return out


def summarize_queue(evaluated):
    """Takes evaluated events and returns the counts the interface reports.

    The cleared count is what lets a screen show three cards instead of the
    whole queue without the reader wondering what happened to the rest.
    """
    stopped = [e for e in evaluated if e["severity"] != "clear"]
    return {
        "read": len(evaluated),
        "stopped": len(stopped),
        "cleared": len(evaluated) - len(stopped),
        "blocked": sum(1 for e in evaluated if e["severity"] == "blocked"),
        "findings": sum(len(e["findings"]) for e in evaluated),
    }


def sort_by_severity(evaluated):
    """Takes evaluated events and returns them worst first."""
    return sorted(evaluated, key=lambda e: SEVERITY_RANK[e["severity"]], reverse=True)
