import urllib.error

from rce_cho_mcp.config import DEFAULT_DATASET_GRAPH, KNOWN_GRAPHS
from rce_cho_mcp.pitfalls import LANGUAGE_TAG_WARNING
from rce_cho_mcp.sparql import escape_sparql_string, execute_sparql, rows


PREFIXES = """PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""


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
    """Resolveer een SKOS prefLabel in een named graph naar alle matchende concepten.

    Geeft elke match terug met zijn URI en type(s). De aanroeper beslist welk
    resultaat relevant is; deze resolver gokt niet.
    """
    _validate_graph_name(graph_name)

    safe_label = escape_sparql_string(label)
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

    bindings = rows(data)

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


# Opgebouwd uit de gedeelde constante in pitfalls.py in plaats van een eigen
# kopie van deze waarschuwing (zie ook server.py's resolve_concept_label(),
# query_sparql() en validator.py, die dezelfde constante gebruiken).
resolve_label.__doc__ += f"""

    BELANGRIJK: {LANGUAGE_TAG_WARNING} Gebruik deze resolver eerst om de
    concept-URI op te halen, en filter of join daarna op die URI in plaats
    van op de labeltekst.
    """


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

    bindings = rows(data)

    return [
        {
            "predicate": binding["predicate"]["value"],
            "object": binding["object"]["value"],
        }
        for binding in bindings
    ]