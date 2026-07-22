"""Severity ladder and verdict language shared by every rule.

A Finding is a plain dict carrying one message per audience, so the same
object renders on the pharmacist, patient, and prescriber surfaces without
any rule knowing which surface is asking.
"""

SEVERITY_RANK = {"clear": 0, "advisory": 1, "review": 2, "blocked": 3}

_VERDICTS = {
    "blocked": "Do not fill.",
    "review": "Needs a look.",
    "advisory": "Worth knowing.",
    "clear": "Clear.",
}


def highest_severity(findings):
    """Takes findings and returns the worst severity among them, or clear."""
    worst = "clear"
    for finding in findings:
        if SEVERITY_RANK[finding["severity"]] > SEVERITY_RANK[worst]:
            worst = finding["severity"]
    return worst


def verdict_for(severity):
    """Takes a severity and returns the three-word verdict a human reads."""
    return _VERDICTS[severity]


def make_finding(rule_id, severity, headline, pharmacist_message, patient_message,
                 prescriber_message, citation, citation_url, suggested_action,
                 evidence):
    """Builds the Finding dict every rule returns."""
    return {
        "rule_id": rule_id,
        "severity": severity,
        "headline": headline,
        "pharmacist_message": pharmacist_message,
        "patient_message": patient_message,
        "prescriber_message": prescriber_message,
        "citation": citation,
        "citation_url": citation_url,
        "suggested_action": suggested_action,
        "evidence": evidence,
    }
