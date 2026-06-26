from rce_cho_mcp.config import DEFAULT_DATASET_GRAPH
from rce_cho_mcp.sparql import execute_sparql


PREFIXES = """PREFIX graph: <https://linkeddata.cultureelerfgoed.nl/graph/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""


ALLOWED_GRAPH_NAMES = {
    "owms",
    "instanties-rce",
    "kennisregistratie-rce",
    "bronnen-rce",
    "void",
}


def _escape_sparql_string(value: str) -> str:
    """Escape a string value for safe use in a SPARQL string literal."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _validate_graph_name(graph_name: str) -> None:
    """Allow only known short graph names for graph:localName syntax."""
    if graph_name not in ALLOWED_GRAPH_NAMES:
        allowed = ", ".join(sorted(ALLOWED_GRAPH_NAMES))
        raise ValueError(
            f"Unknown graph_name '{graph_name}'. Allowed: {allowed}"
        )


def resolve_label(
    label: str,
    graph_name: str = "owms",
    lang: str = "nl",
) -> list[dict]:
    """Resolve a SKOS prefLabel in a named graph to all matching concepts.

    Returns every match with its URI and type(s). The caller decides which
    result is relevant. The resolver does not guess.
    """
    _validate_graph_name(graph_name)

    safe_label = _escape_sparql_string(label)

    query = f"""{PREFIXES}

SELECT DISTINCT ?concept ?type
WHERE {{
  GRAPH graph:{graph_name} {{
    ?concept skos:prefLabel "{safe_label}"@{lang} .
    OPTIONAL {{ ?concept a ?type . }}
  }}
}}
"""

    data = execute_sparql(query)
    bindings = data.get("results", {}).get("bindings", [])

    results: dict[str, dict] = {}

    for binding in bindings:
        uri = binding["concept"]["value"]

        entry = results.setdefault(
            uri,
            {
                "uri": uri,
                "types": [],
            },
        )

        if "type" in binding:
            type_uri = binding["type"]["value"]

            if type_uri not in entry["types"]:
                entry["types"].append(type_uri)

    return list(results.values())


def describe_resource(
    uri: str,
    graph: str = DEFAULT_DATASET_GRAPH,
) -> list[dict]:
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