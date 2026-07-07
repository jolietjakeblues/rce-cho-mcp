import os

from rce_cho_mcp.graphs import KNOWN_GRAPH_ROWS


# "Virtuoso" endpoint: supports GeoSPARQL, but has the query quirks documented
# in semantics.py/validator.py (GROUP BY overflow on long text fields,
# ORDER BY + OPTIONAL 504s, geof:sfWithin timeouts).
CHO_SERVICE_ENDPOINT = os.getenv(
    "CHO_SERVICE_ENDPOINT",
    "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/services/cho/sparql",
)

# "Speedy" endpoint: standards-compliant SPARQL 1.1.
CHO_DATASET_ENDPOINT = os.getenv(
    "CHO_DATASET_ENDPOINT",
    "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/sparql",
)

# Speedy is the default; Virtuoso is used as a fallback by execute_sparql()
# when Speedy is unreachable or returns a gateway-level error (502/503/504).
SPARQL_ENDPOINT = os.getenv(
    "SPARQL_ENDPOINT",
    CHO_DATASET_ENDPOINT,
)

SPARQL_FALLBACK_ENDPOINT = os.getenv(
    "SPARQL_FALLBACK_ENDPOINT",
    CHO_SERVICE_ENDPOINT,
)

DEFAULT_DATASET_GRAPH = os.getenv(
    "RCE_CHO_GRAPH",
    "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce",
)

# Graphs that graphs_list() lists for discovery but that are not queryable
# named graphs on the RCE CHO SPARQL endpoint itself: "ceo-ontology" is a raw
# ontology file on GitHub and "triply-owms" lives on a separate external
# TriplyDB service. A GRAPH <...> clause against either silently returns zero
# results rather than an error, so they are excluded from the graph_name
# allowlist below.
_NON_QUERYABLE_GRAPH_KEYS = {"ceo-ontology", "triply-owms"}

# Short, stable aliases kept for backward compatibility with existing callers.
KNOWN_GRAPHS = {
    "owms": "https://linkeddata.cultureelerfgoed.nl/graph/owms",
    "instanties-rce": "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce",
    "abr": "https://data.cultureelerfgoed.nl/term/id/abr/thesaurus",
    "cht": "https://data.cultureelerfgoed.nl/term/id/cht/thesaurus",
    "bebouwdeomgeving": "https://linkeddata.cultureelerfgoed.nl/graph/bebouwdeomgeving",
}

# Fill in every other graph known to graphs_list() so a graph_name a client
# just discovered there is guaranteed to also work in resolve_concept_label().
for _row in KNOWN_GRAPH_ROWS:
    if _row["key"] not in KNOWN_GRAPHS and _row["key"] not in _NON_QUERYABLE_GRAPH_KEYS:
        KNOWN_GRAPHS[_row["key"]] = _row["uri"]

del _row

USER_AGENT = "rce-cho-mcp/0.2.0b1"
