import os


CHO_SERVICE_ENDPOINT = os.getenv(
    "CHO_SERVICE_ENDPOINT",
    "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/services/cho/sparql",
)

CHO_DATASET_ENDPOINT = os.getenv(
    "CHO_DATASET_ENDPOINT",
    "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/sparql",
)

SPARQL_ENDPOINT = os.getenv(
    "SPARQL_ENDPOINT",
    CHO_SERVICE_ENDPOINT,
)

DEFAULT_DATASET_GRAPH = os.getenv(
    "RCE_CHO_GRAPH",
    "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce",
)

KNOWN_GRAPHS = {
    "owms": "https://linkeddata.cultureelerfgoed.nl/graph/owms",
    "instanties-rce": "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce",
    "abr": "https://data.cultureelerfgoed.nl/term/id/abr/thesaurus",
    "cht": "https://data.cultureelerfgoed.nl/term/id/cht/thesaurus",
    "bebouwdeomgeving": "https://linkeddata.cultureelerfgoed.nl/graph/bebouwdeomgeving",
    "ceo": "https://raw.githubusercontent.com/cultureelerfgoed/CEO/master/CEO_RCE.ttl",
}

USER_AGENT = "rce-cho-mcp/0.2.0"