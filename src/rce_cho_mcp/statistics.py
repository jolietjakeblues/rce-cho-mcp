from rce_cho_mcp.config import SPARQL_ENDPOINT
from rce_cho_mcp.sparql import execute_sparql

# Prefix used to filter partition results down to CEO-namespace terms only,
# excluding infrastructure predicates (rdf:type, skos:*, edm:*, ...) that
# would otherwise dominate the property partition.
CEO_NS = "https://linkeddata.cultureelerfgoed.nl/def/ceo#"

# These are full-dataset scans (~58M triples, no GRAPH restriction picks up
# the whole union) and are slow even though they are cheap aggregates: a
# plain COUNT(*) has taken up to ~60s in practice. Generous timeouts, no
# retries beyond what execute_sparql already does.
_TOTALS_TIMEOUT = 90
_PARTITION_TIMEOUT = 150


def _count(where: str, distinct_var: str | None = None, timeout: int = _TOTALS_TIMEOUT) -> int:
    select = f"COUNT(DISTINCT ?{distinct_var})" if distinct_var else "COUNT(*)"
    data = execute_sparql(f"SELECT ({select} AS ?n) WHERE {{ {where} }}", timeout=timeout)
    bindings = data.get("results", {}).get("bindings", [])
    return int(bindings[0]["n"]["value"]) if bindings else 0


def dataset_totalen() -> dict:
    """Return dataset-wide totals: triples, entities, classes, properties.

    Each is a separate full-dataset aggregate query; expect this to take
    over a minute in total (measured: ~114s).
    """
    return {
        "triples": _count("?s ?p ?o"),
        "entiteiten": _count("?s a []", distinct_var="s"),
        "klassen": _count("[] a ?c", distinct_var="c"),
        "properties": _count("[] ?p []", distinct_var="p"),
        "endpoint": SPARQL_ENDPOINT,
    }


def klasse_partities(alleen_ceo: bool = True) -> list[dict]:
    """Count instances per class across the whole dataset.

    Classes with a low or zero count -- or entirely absent from this list --
    are a sign the ontology declares more than what the live data contains.
    """
    data = execute_sparql(
        "SELECT ?c (COUNT(?s) AS ?n) WHERE { ?s a ?c } GROUP BY ?c ORDER BY DESC(?n)",
        timeout=_PARTITION_TIMEOUT,
    )
    bindings = data.get("results", {}).get("bindings", [])
    return [
        {"klasse": b["c"]["value"], "aantal": int(b["n"]["value"])}
        for b in bindings
        if not alleen_ceo or b["c"]["value"].startswith(CEO_NS)
    ]


def property_partities(alleen_ceo: bool = True) -> list[dict]:
    """Count triples per property across the whole dataset.

    Sparsely-populated properties are a sign a query path exists in theory
    but rarely has data to return.
    """
    data = execute_sparql(
        "SELECT ?p (COUNT(*) AS ?n) WHERE { ?s ?p ?o } GROUP BY ?p ORDER BY DESC(?n)",
        timeout=_PARTITION_TIMEOUT,
    )
    bindings = data.get("results", {}).get("bindings", [])
    return [
        {"property": b["p"]["value"], "aantal": int(b["n"]["value"])}
        for b in bindings
        if not alleen_ceo or b["p"]["value"].startswith(CEO_NS)
    ]
