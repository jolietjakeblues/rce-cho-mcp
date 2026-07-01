import urllib.error

from rce_cho_mcp.config import DEFAULT_DATASET_GRAPH, KNOWN_GRAPHS
from rce_cho_mcp.sparql import execute_sparql


PREFIXES = """PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""


def _escape_sparql_string(value: str) -> str:
    """Escape a string value for safe use in a SPARQL string literal."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _validate_graph_name(graph_name: str) -> None:
    """Allow only known short graph names for graph:localName syntax."""
    if graph_name not in KNOWN_GRAPHS:
        allowed = ", ".join(sorted(KNOWN_GRAPHS.keys()))
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

    IMPORTANT: prefLabel values in this dataset are language-tagged
    (e.g. "Zwolle"@nl). Do not filter or match on skos:prefLabel strings
    directly in hand-written SPARQL (e.g. FILTER(?label = "Zwolle") or
    FILTER(?label IN (...))) — a plain string literal will not match a
    language-tagged RDF term and the query will silently return zero
    results. Call this resolver first to get the concept URI, then filter
    or join on that URI instead of on the label text.
    """
    _validate_graph_name(graph_name)

    safe_label = _escape_sparql_string(label)
    graph_uri = KNOWN_GRAPHS[graph_name]

    query = f"""{PREFIXES}

SELECT DISTINCT ?concept ?type
WHERE {{
  GRAPH <{graph_uri}> {{
    ?concept skos:prefLabel "{safe_label}"@{lang} .
    OPTIONAL {{ ?concept a ?type . }}
  }}
}}
"""

    try:
        data = execute_sparql(query)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP fout {e.code} bij resolven van label '{label}': {body[:300]}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Fout bij resolven van label '{label}': {type(e).__name__}: {e}"
        ) from e

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

    try:
        data = execute_sparql(query)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP fout {e.code} bij opvragen van resource '{uri}': {body[:300]}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Fout bij opvragen van resource '{uri}': {type(e).__name__}: {e}"
        ) from e

    bindings = data.get("results", {}).get("bindings", [])

    return [
        {
            "predicate": binding["predicate"]["value"],
            "object": binding["object"]["value"],
        }
        for binding in bindings
    ]