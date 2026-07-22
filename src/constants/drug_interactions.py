"""Known drug-drug interaction pairs, keyed by generic name in lowercase.

Each entry describes what happens when the two drugs are taken by the
same patient, in both clinical and plain language, with the action the
reader should take. Severity is `major` (avoid the combination) or
`moderate` (use with caution and monitoring).
"""

INTERACTION_SOURCE = "AHFS Drug Information; FDA prescribing information"


def _pair(a, b):
    """Takes two generic names and returns the canonical dictionary key."""
    return tuple(sorted((a.lower(), b.lower())))


DRUG_INTERACTIONS = {
    _pair("Sertraline", "Tramadol HCl"): {
        "severity": "major",
        "effect": "Both drugs raise serotonin. Together they can trigger "
                  "serotonin syndrome: agitation, rapid heart rate, high "
                  "temperature, muscle rigidity.",
        "plain_effect": "Taking these two together can cause a dangerous "
                        "reaction called serotonin syndrome.",
        "advice": "Avoid the combination. Contact the prescriber about an "
                  "alternative pain medication.",
    },
    _pair("Sertraline", "Ibuprofen"): {
        "severity": "moderate",
        "effect": "SSRIs impair platelet function; combined with an NSAID "
                  "the risk of GI bleeding roughly doubles.",
        "plain_effect": "Taking these two together raises the chance of "
                        "stomach bleeding.",
        "advice": "Watch for dark stools or stomach pain. Ask about a "
                  "stomach-protecting medication if both are needed.",
    },
    _pair("Warfarin Sodium", "Omeprazole"): {
        "severity": "moderate",
        "effect": "Omeprazole inhibits warfarin metabolism and can raise "
                  "INR, increasing bleeding risk.",
        "plain_effect": "The reflux medication can make the blood thinner "
                        "work harder than intended.",
        "advice": "Monitor INR more closely after starting or stopping "
                  "omeprazole.",
    },
    _pair("Warfarin Sodium", "Ibuprofen"): {
        "severity": "major",
        "effect": "NSAIDs impair platelets and can injure gastric mucosa; "
                  "with warfarin the risk of serious bleeding rises sharply.",
        "plain_effect": "Taking these two together sharply raises the "
                        "chance of serious bleeding.",
        "advice": "Avoid the combination. Use acetaminophen for pain unless "
                  "the prescriber directs otherwise.",
    },
    _pair("Lisinopril", "Ibuprofen"): {
        "severity": "moderate",
        "effect": "NSAIDs blunt the antihypertensive effect of ACE "
                  "inhibitors and add kidney strain, especially with "
                  "dehydration.",
        "plain_effect": "The pain reliever can make the blood pressure "
                        "medication work less well and stress the kidneys.",
        "advice": "Limit regular NSAID use; recheck blood pressure and "
                  "kidney function if both continue.",
    },
    _pair("Zolpidem Tartrate", "Tramadol HCl"): {
        "severity": "moderate",
        "effect": "Additive central nervous system depression: sedation, "
                  "respiratory depression, impaired coordination.",
        "plain_effect": "Taking these two together can cause dangerous "
                        "levels of sleepiness and slowed breathing.",
        "advice": "Avoid taking doses close together; do not drive after "
                  "either dose.",
    },
    _pair("Zolpidem Tartrate", "Temazepam"): {
        "severity": "major",
        "effect": "Two hypnotics with additive CNS and respiratory "
                  "depression. No indication supports combining them.",
        "plain_effect": "These are two sleep medications that should not "
                        "be taken together.",
        "advice": "Use one hypnotic only. Contact the prescriber.",
    },
}


def interactions_for_pair(generic_a, generic_b):
    """Takes two generic names and returns the interaction entry or None."""
    return DRUG_INTERACTIONS.get(_pair(generic_a, generic_b))
