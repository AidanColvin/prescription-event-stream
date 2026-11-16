"""PubMed evidence lookup against NCBI E-utilities.

esearch returns the PubMed ids of recent reviews and clinical trials for
a drug; esummary returns each article's title, journal, and year. Network
fetching and response parsing are separate functions so the parsing is
testable without a network.
"""

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass

from src.constants.pubmed_evidence import (
    PUBMED_ARTICLE_URL,
    PUBMED_ESEARCH_URL,
    PUBMED_ESUMMARY_URL,
    PUBMED_MAX_REFS,
    PUBMED_PUBLICATION_FILTER,
    PUBMED_RATE_LIMIT_SLEEP_SECONDS,
    PUBMED_SELECTION_NOTE,
)
from src.drug_lookup import is_valid_term


@dataclass(frozen=True)
class PubmedRef:
    """One peer-reviewed reference with a link to its PubMed page."""
    pmid: str
    title: str
    journal: str
    year: str
    url: str


def _get_json(url: str, timeout: int = 6) -> dict:
    """Takes a URL. Returns its parsed JSON response."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "prescription-event-stream-demo"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def parse_esearch_ids(payload: dict) -> "list[str]":
    """Takes an esearch JSON payload. Returns its PubMed ids."""
    id_list = (payload.get("esearchresult") or {}).get("idlist") or []
    return [str(pmid) for pmid in id_list if pmid]


def _year_from_pubdate(pubdate: str) -> str:
    """Takes a PubMed pubdate string. Returns its four-digit year, or empty."""
    for token in (pubdate or "").split():
        if len(token) == 4 and token.isdigit():
            return token
    return ""


def shape_reference(pmid: str, entry: dict) -> "PubmedRef | None":
    """Takes a PubMed id and its esummary entry. Returns a PubmedRef, or
    None when the entry carries no usable title."""
    title = (entry.get("title") or "").strip().rstrip(".")
    if not title:
        return None
    journal = (entry.get("fulljournalname") or entry.get("source") or "").strip()
    year = _year_from_pubdate(entry.get("pubdate", ""))
    return PubmedRef(
        pmid=pmid,
        title=title,
        journal=journal,
        year=year,
        url=PUBMED_ARTICLE_URL.format(pmid),
    )


def parse_esummary_refs(payload: dict, ids: "list[str]") -> "list[PubmedRef]":
    """Takes an esummary payload and the id order. Returns references in
    that order, skipping entries without a title."""
    result = payload.get("result") or {}
    refs = []
    for pmid in ids:
        entry = result.get(pmid)
        if not isinstance(entry, dict):
            continue
        ref = shape_reference(pmid, entry)
        if ref is not None:
            refs.append(ref)
    return refs


def refs_to_json(refs: "list[PubmedRef]") -> "list[dict]":
    """Takes references. Returns the JSON-ready list the card renders."""
    return [{"pmid": r.pmid, "title": r.title, "journal": r.journal,
             "year": r.year, "url": r.url} for r in refs]


def _esearch_url(drug: str) -> str:
    """Takes a drug name. Returns its esearch request URL."""
    term = f"{drug} AND {PUBMED_PUBLICATION_FILTER}"
    query = urllib.parse.urlencode({
        "db": "pubmed",
        "term": term,
        "retmax": PUBMED_MAX_REFS,
        "retmode": "json",
        "sort": "relevance",
    })
    return f"{PUBMED_ESEARCH_URL}?{query}"


def _esummary_url(ids: "list[str]") -> str:
    """Takes PubMed ids. Returns their esummary request URL."""
    query = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json",
    })
    return f"{PUBMED_ESUMMARY_URL}?{query}"


def fetch_pubmed_ids(drug: str) -> "list[PubmedRef]":
    """Takes a generic drug name. Returns up to five recent reviews and
    clinical trials for it from PubMed, spaced to respect the rate limit."""
    drug = (drug or "").strip()
    if not is_valid_term(drug):
        return []
    try:
        search = _get_json(_esearch_url(drug))
    except Exception:
        return []
    ids = parse_esearch_ids(search)[:PUBMED_MAX_REFS]
    if not ids:
        return []
    time.sleep(PUBMED_RATE_LIMIT_SLEEP_SECONDS)
    try:
        summary = _get_json(_esummary_url(ids))
    except Exception:
        return []
    return parse_esummary_refs(summary, ids)


def fetch_references(drug: str) -> "list[dict]":
    """Takes a generic drug name. Returns its references as JSON-ready dicts."""
    return refs_to_json(fetch_pubmed_ids(drug))


def attach_references(info: dict) -> dict:
    """Takes a shaped drug info dict. Returns it with PubMed references and
    the selection note attached when the lookup found a drug."""
    if not isinstance(info, dict) or not info.get("found"):
        return info
    refs = fetch_references(info.get("generic_name") or "")
    info["references"] = refs
    info["references_note"] = PUBMED_SELECTION_NOTE if refs else ""
    return info
