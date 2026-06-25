from rdflib import Graph, URIRef

from rce_cho_mcp.sparql import SPARQL_ENDPOINT


PREFIXES = """
PREFIX graph: <https://linkeddata.cultureelerfgoed.nl/graph/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>

"""


def resolve_label(label: str, graph_name: str = "owms", lang: str = "nl") -> str | None:
    """Resolve a SKOS prefLabel in a named graph to a concept URI."""
    query = f"""{PREFIXES}

SELECT DISTINCT ?concept
WHERE {{
  GRAPH graph:{graph_name} {{
    ?concept skos:prefLabel "{label}"@{lang} .
  }}
}}
LIMIT 1
"""

    graph = Graph()
    result = graph.query(
        query,
        initNs={},
        service=SPARQL_ENDPOINT,
    )

    for row in result:
        concept = row.get("concept")
        if isinstance(concept, URIRef):
            return str(concept)

    return None