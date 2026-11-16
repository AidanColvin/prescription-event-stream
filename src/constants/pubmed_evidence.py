"""Constants for the PubMed evidence lookup.

References come from NCBI E-utilities: esearch finds recent reviews and
clinical trials for the drug, esummary returns their titles, journals,
and years. No API key. The public limit without a key is 3 requests per
second, so calls are spaced by a short sleep.
"""

PUBMED_ESEARCH_URL = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
                      "esearch.fcgi")
PUBMED_ESUMMARY_URL = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
                       "esummary.fcgi")
PUBMED_ARTICLE_URL = "https://pubmed.ncbi.nlm.nih.gov/{}/"

# Restrict results to the two evidence tiers worth surfacing.
PUBMED_PUBLICATION_FILTER = "(Review[ptyp] OR Clinical Trial[ptyp])"

# References shown per drug.
PUBMED_MAX_REFS: int = 5

# Seconds between NCBI calls, respecting the 3 requests per second limit.
PUBMED_RATE_LIMIT_SLEEP_SECONDS: float = 0.34

PUBMED_SOURCE = "PubMed via NCBI E-utilities"

PUBMED_SELECTION_NOTE = ("The most relevant recent reviews and trials, "
                         "selected automatically.")
