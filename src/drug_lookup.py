"""Live drug lookup against the real sources.

openFDA serves the FDA drug label (indications, contraindications,
interactions, mechanism). RxNorm normalizes whatever the user typed --
brand names, misspellings -- into a name the label search can hit.
Network fetching and response shaping are separate functions so the
shaping is testable without a network.
"""

import json
import re
import urllib.parse
import urllib.request

OPENFDA_LABEL_URL = "https://api.fda.gov/drug/label.json?search={}&limit=1"
RXNORM_APPROX_URL = ("https://rxnav.nlm.nih.gov/REST/approximateTerm.json"
                     "?term={}&maxEntries=1&option=1")
RXNORM_NAME_URL = ("https://rxnav.nlm.nih.gov/REST/rxcui/{}/property.json"
                   "?propName=RxNorm%20Name")

_TERM_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9 .'/-]{1,63}$")


def is_valid_term(term):
    """Takes user input and returns True when it is safe to look up."""
    return bool(term) and bool(_TERM_PATTERN.fullmatch(term.strip()))


def _get_json(url, timeout=4):
    request = urllib.request.Request(
        url, headers={"User-Agent": "prescription-event-stream-demo"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def trim_label_text(text, limit=380):
    """Takes raw label text and returns the first sentences within limit.

    Labels open with numbered headings like '1 INDICATIONS AND USAGE';
    those are navigation, not content, so they are stripped.
    """
    if not text:
        return None
    headings = (r"(INDICATIONS AND USAGE|CONTRAINDICATIONS|DRUG INTERACTIONS"
                r"|WARNINGS( AND PRECAUTIONS)?|Pediatric Use"
                r"|Mechanism of Action|Use in Specific Populations)")
    text = re.sub(rf"^\s*\d+(\.\d+)*\s+{headings}\s*", "", text)
    text = re.sub(r"^\s*\d+(\.\d+)*\s+[A-Z][A-Z &,]+\s", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    if len(text) <= limit:
        return text
    cut = text[:limit]
    sentence_end = max(cut.rfind(". "), cut.rfind("; "))
    if sentence_end > 80:
        return cut[:sentence_end + 1]
    return cut.rstrip() + "…"


def _first(label, field):
    values = label.get(field)
    return values[0] if isinstance(values, list) and values else None


def _clean_classes(values, suffix):
    if not values:
        return None
    cleaned = [v.replace(suffix, "").strip() for v in values]
    return ", ".join(dict.fromkeys(cleaned))


def shape_drug_info(label):
    """Takes one openFDA label result and returns the card the pages render."""
    openfda = label.get("openfda", {})
    generic = (openfda.get("generic_name") or [None])[0]
    brand = (openfda.get("brand_name") or [None])[0]
    if not generic and not brand:
        return None

    name = (generic or brand).title()
    mechanism = trim_label_text(_first(label, "mechanism_of_action"))
    moa_class = _clean_classes(openfda.get("pharm_class_moa"), " [MoA]")
    if not mechanism and moa_class:
        mechanism = f"Pharmacologic mechanism class: {moa_class}."

    return {
        "found": True,
        "generic_name": name,
        "brand_name": brand.title() if brand else None,
        "drug_class": _clean_classes(openfda.get("pharm_class_epc"), " [EPC]"),
        "mechanism": mechanism,
        "approved_uses": trim_label_text(_first(label, "indications_and_usage")),
        "interactions": trim_label_text(_first(label, "drug_interactions")),
        "contraindications": trim_label_text(_first(label, "contraindications")),
        "pediatric_use": trim_label_text(_first(label, "pediatric_use")),
        "dailymed_url": ("https://dailymed.nlm.nih.gov/dailymed/search.cfm?query="
                         + urllib.parse.quote(name)),
        "source": "FDA drug label via openFDA",
    }


def fetch_label(name):
    """Takes a drug name and returns the first matching openFDA label, or None."""
    quoted = urllib.parse.quote(f'"{name}"')
    search = (f"openfda.generic_name:{quoted}+openfda.brand_name:{quoted}")
    try:
        payload = _get_json(OPENFDA_LABEL_URL.format(search))
        results = payload.get("results")
        return results[0] if results else None
    except Exception:
        return None


def normalize_name(term):
    """Takes whatever the user typed and returns RxNorm's name for it, or None."""
    try:
        approx = _get_json(RXNORM_APPROX_URL.format(urllib.parse.quote(term)))
        candidates = (approx.get("approximateGroup") or {}).get("candidate") or []
        if not candidates:
            return None
        rxcui = candidates[0].get("rxcui")
        prop = _get_json(RXNORM_NAME_URL.format(rxcui))
        values = (prop.get("propConceptGroup") or {}).get("propConcept") or []
        return values[0].get("propValue") if values else None
    except Exception:
        return None


def lookup_drug(term):
    """Takes a search term and returns drug info from the real sources.

    Tries the label directly first, since exact generic and brand names
    hit without help. Falls back to RxNorm normalization for brand
    variants and misspellings.
    """
    term = (term or "").strip()
    if not is_valid_term(term):
        return {"found": False}

    label = fetch_label(term)
    if label is None:
        normalized = normalize_name(term)
        if normalized and normalized.lower() != term.lower():
            # RxNorm names are verbose ("ibuprofen 200 MG Oral Tablet");
            # the first word is the ingredient the label search needs.
            ingredient = normalized.split()[0]
            label = fetch_label(ingredient)

    if label is None:
        return {"found": False}
    shaped = shape_drug_info(label)
    return shaped if shaped else {"found": False}
