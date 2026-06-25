import os

SPARQL_ENDPOINT = os.getenv(
    "SPARQL_ENDPOINT",
    "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/services/cho/sparql",
)

DEFAULT_GRAPH = os.getenv(
    "RCE_CHO_GRAPH",
    "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce",
)

USER_AGENT = "rce-cho-mcp/0.1.0"