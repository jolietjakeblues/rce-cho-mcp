from rce_cho_mcp.config import DEFAULT_GRAPH
from rce_cho_mcp.sparql import execute_sparql


PREFIXES = """PREFIX graph: <https://linkeddata.cultureelerfgoed.nl/graph/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""


def resolve_label(label: str, graph_name: str = "owms", lang: str = "nl") -> list[dict]:
    """Resolve a SKOS prefLabel in a named graph to all matching concepts.

    Returns every match with its URI and type(s) — the caller decides which
    one is relevant, the resolver does not guess.
    """
    query = f"""{PREFIXES}

SELECT DISTINCT ?concept ?type
WHERE {{
  GRAPH graph:{graph_name} {{
    ?concept skos:prefLabel "{label}"@{lang} .
    OPTIONAL {{ ?concept a ?type . }}
  }}
}}
"""

    data = execute_sparql(query)
    bindings = data.get("results", {}).get("bindings", [])

    results: dict[str, dict] = {}
    for binding in bindings:
        uri = binding["concept"]["value"]
        entry = results.setdefault(uri, {"uri": uri, "types": []})
        if "type" in binding:
            type_uri = binding["type"]["value"]
            if type_uri not in entry["types"]:
                entry["types"].append(type_uri)

    return list(results.values())


def describe_resource(uri: str, graph: str = DEFAULT_GRAPH) -> list[dict]:
    """Return every property/value pair known about a resource URI."""
    query = f"""SELECT ?predicate ?object
WHERE {{
  GRAPH <{graph}> {{
    <{uri}> ?predicate ?object .
  }}
}}
"""

    data = execute_sparql(query)
    bindings = data.get("results", {}).get("bindings", [])

    return [
        {
            "predicate": binding["predicate"]["value"],
            "object": binding["object"]["value"],
        }
        for binding in bindings
    ]