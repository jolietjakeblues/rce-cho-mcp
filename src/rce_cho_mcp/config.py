import os

from rce_cho_mcp.graphs import KNOWN_GRAPH_ROWS, NON_QUERYABLE_GRAPH_KEYS


# "Virtuoso" endpoint. Live getest (2026-10-30): mist de GeoSPARQL-functie
# geof:area() (HTTP 400 "Unknown function ...geosparql/area()") -- dus NIET
# het endpoint waar de geof:area()/geof:sfIntersects()-aanroepen in area.py/
# brk_spatial.py tegen draaien (die lopen standaard via CHO_DATASET_ENDPOINT
# hieronder). Wel nog in gebruik als fallback-endpoint; de query-valkuilen
# die elders in deze codebase (validator.py/semantics.py) aan "Virtuoso"
# worden toegeschreven (GROUP BY-overflow, ORDER BY + OPTIONAL 504s,
# geof:sfWithin-timeouts) zijn niet opnieuw per-endpoint herverifieerd, dus
# behandel die toeschrijving als een naam, niet als een geverifieerd feit
# over welk van de twee endpoints hieronder de fout daadwerkelijk geeft.
CHO_SERVICE_ENDPOINT = os.getenv(
    "CHO_SERVICE_ENDPOINT",
    "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/services/cho/sparql",
)

# "Speedy" endpoint: standards-compliant SPARQL 1.1. Live getest
# (2026-10-30): ondersteunt geof:area() wel (HTTP 200, correct resultaat) --
# dit is het endpoint dat area.py/brk_spatial.py in de praktijk gebruiken,
# want dit is ook de standaard SPARQL_ENDPOINT hieronder.
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
    if _row["key"] not in KNOWN_GRAPHS and _row["key"] not in NON_QUERYABLE_GRAPH_KEYS:
        KNOWN_GRAPHS[_row["key"]] = _row["uri"]

del _row

USER_AGENT = "rce-cho-mcp/0.2.0b1"

# Kadaster Kennisgraph (KKG) SPARQL-endpoint, gebruikt door brk_spatial.py voor
# de spatial join tussen RCE-monumentgeometrie en Kadaster-percelen. Zelfde
# endpoint als de losse kadaster-kkg-mcp server (mcp__kadaster-kkg__*); hier
# rechtstreeks aangeroepen zodat brk_spatial geen afhankelijkheid heeft op die
# losse MCP-server-runtime.
KKG_SPARQL_ENDPOINT = os.getenv(
    "KKG_SPARQL_ENDPOINT",
    "https://api.labs.kadaster.nl/datasets/kadaster/kkg/services/kkg/sparql",
)

# Public, unauthenticated GraphQL API of the NDE Network of Terms
# (https://termennetwerk.netwerkdigitaalerfgoed.nl/), used for fuzzy
# concept search with synonyms across published thesauri (CHT, ABR, ...).
TERMENNETWERK_ENDPOINT = os.getenv(
    "TERMENNETWERK_ENDPOINT",
    "https://termennetwerk-api.netwerkdigitaalerfgoed.nl/graphql",
)
