from rce_cho_mcp.sparql import execute_sparql

_EXPLORE_TIMEOUT = 60


def verken_klasse(klasse: str, steekproef: int = 1000) -> list[dict]:
    """Discover which predicates lead out of a class, and to what, based on
    a sample of instances.

    Use this to navigate the graph iteratively when building a query path:
    start at the class the question is about, follow the relevant predicate
    to its target class, and explore that in turn until reaching the
    desired literal. Counts reflect fill rate within the sample only.
    """
    query = f"""
SELECT ?p ?doel ?soort (COUNT(*) AS ?n) WHERE {{
  {{ SELECT ?s WHERE {{ ?s a <{klasse}> }} LIMIT {steekproef} }}
  ?s ?p ?o .
  OPTIONAL {{ ?o a ?otype }}
  BIND(
    IF(BOUND(?otype), STR(?otype),
      IF(isLiteral(?o), STR(DATATYPE(?o)), "iri-zonder-type")
    ) AS ?doel)
  BIND(
    IF(BOUND(?otype), "klasse",
      IF(isLiteral(?o), "datatype", "iri-zonder-type")
    ) AS ?soort)
}}
GROUP BY ?p ?doel ?soort
ORDER BY DESC(?n)
"""
    data = execute_sparql(query, timeout=_EXPLORE_TIMEOUT)
    bindings = data.get("results", {}).get("bindings", [])
    return [
        {
            "predicaat": b.get("p", {}).get("value", ""),
            "doel": b.get("doel", {}).get("value", ""),
            "soort": b.get("soort", {}).get("value", ""),
            "aantal": int(b.get("n", {}).get("value", 0)),
        }
        for b in bindings
    ]


def verken_inkomend(klasse: str, steekproef: int = 1000) -> list[dict]:
    """Discover which classes and predicates point INTO instances of this
    class, based on a sample -- the reverse direction of verken_klasse.

    Use this for questions where the path runs backwards, such as "which
    complex does this monument belong to": exploring incoming on
    Rijksmonument finds Complex -> heeftRijksmonument.
    """
    query = f"""
SELECT ?bron ?p (COUNT(*) AS ?n) WHERE {{
  {{ SELECT ?o WHERE {{ ?o a <{klasse}> }} LIMIT {steekproef} }}
  ?s ?p ?o .
  OPTIONAL {{ ?s a ?bron }}
}}
GROUP BY ?bron ?p
ORDER BY DESC(?n)
"""
    data = execute_sparql(query, timeout=_EXPLORE_TIMEOUT)
    bindings = data.get("results", {}).get("bindings", [])
    return [
        {
            "bronklasse": b.get("bron", {}).get("value", "onbekend"),
            "predicaat": b.get("p", {}).get("value", ""),
            "aantal": int(b.get("n", {}).get("value", 0)),
        }
        for b in bindings
    ]
