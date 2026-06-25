from rce_cho_mcp.sparql import execute_sparql


PREFIXES = """PREFIX graph: <https://linkeddata.cultureelerfgoed.nl/graph/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
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

    data = execute_sparql(query)
    bindings = data.get("results", {}).get("bindings", [])

    if not bindings:
        return None

    return bindings[0]["concept"]["value"]