"""Live datasetstatistieken: instanties per klasse, triples per property, en
pad-verkenning (voorwaarts en achterwaarts) op basis van een steekproef.

In tegenstelling tot ontology.api.statistics() (die telt wat er in het
gebundelde CEO-ontologiebestand is *gedefinieerd*) tellen deze functies wat
er daadwerkelijk in de live data staat, inclusief klassen/properties die wel
gedefinieerd maar (nog) niet gebruikt zijn.
"""

from rce_cho_mcp.sparql import execute_sparql

CEO_NS = "https://linkeddata.cultureelerfgoed.nl/def/ceo#"

_MIN_SAMPLE_SIZE = 100
_MAX_SAMPLE_SIZE = 10_000
_LONG_QUERY_TIMEOUT = 120


def _rows(data: dict) -> list[dict]:
    return data.get("results", {}).get("bindings", [])


def _clamp_sample_size(sample_size: int) -> int:
    return max(_MIN_SAMPLE_SIZE, min(sample_size, _MAX_SAMPLE_SIZE))


def dataset_totals() -> dict[str, int | str]:
    """Kerncijfers van de live dataset: aantal triples, entiteiten, klassen
    en properties."""
    queries = {
        "triples": "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }",
        "entiteiten": "SELECT (COUNT(DISTINCT ?s) AS ?n) WHERE { ?s a [] }",
        "klassen": "SELECT (COUNT(DISTINCT ?c) AS ?n) WHERE { [] a ?c }",
        "properties": "SELECT (COUNT(DISTINCT ?p) AS ?n) WHERE { [] ?p [] }",
    }
    totals: dict[str, int | str] = {}
    for name, query in queries.items():
        rows = _rows(execute_sparql(query, timeout=_LONG_QUERY_TIMEOUT))
        totals[name] = int(rows[0]["n"]["value"]) if rows else 0
    return totals


def class_partitions(only_ceo: bool = True, limit: int = 100) -> list[dict]:
    """Telt per klasse het aantal instanties in de live dataset.

    Toont ook welke ontologieklassen NIET in de data voorkomen: klassen die
    in ontology_describe_class() bestaan maar hier ontbreken hebben nul
    instanties in de praktijk.
    """
    query = (
        "SELECT ?c (COUNT(?s) AS ?n) WHERE { ?s a ?c } "
        "GROUP BY ?c ORDER BY DESC(?n)"
    )
    rows = _rows(execute_sparql(query, timeout=_LONG_QUERY_TIMEOUT))
    result = []
    for row in rows:
        class_uri = row["c"]["value"]
        if only_ceo and not class_uri.startswith(CEO_NS):
            continue
        result.append({"class": class_uri, "count": int(row["n"]["value"])})
    return result[:limit]


def property_partitions(only_ceo: bool = True, limit: int = 100) -> list[dict]:
    """Telt per property het aantal triples in de live dataset.

    Properties met lage aantallen zijn dun gevuld -- relevant om in te
    schatten of een querypad kansrijk is voordat je 'm schrijft.
    """
    query = (
        "SELECT ?p (COUNT(*) AS ?n) WHERE { ?s ?p ?o } "
        "GROUP BY ?p ORDER BY DESC(?n)"
    )
    rows = _rows(execute_sparql(query, timeout=_LONG_QUERY_TIMEOUT))
    result = []
    for row in rows:
        property_uri = row["p"]["value"]
        if only_ceo and not property_uri.startswith(CEO_NS):
            continue
        result.append({"property": property_uri, "count": int(row["n"]["value"])})
    return result[:limit]


def explore_class_paths(class_uri: str, sample_size: int = 1000) -> dict:
    """Ontdekt welke predicaten vanaf een klasse vertrekken en waar ze
    naartoe leiden (doelklasse of datatype), op basis van een steekproef
    van instanties.

    Gebruik dit om iteratief door de graaf te navigeren bij het opbouwen van
    een querypad: start bij de klasse van de vraag, volg het relevante
    predicaat naar de doelklasse, en verken die opnieuw tot je bij de
    gewenste waarde (literal) bent. In tegenstelling tot
    ontology_describe_class() (statisch, uit het ontologiebestand) is dit
    empirisch: het toont ook paden die niet in de ontologie gedocumenteerd
    staan, en hoe goed een pad gevuld is binnen de steekproef.
    """
    sample_size = _clamp_sample_size(sample_size)
    query = f"""
SELECT ?p ?target ?kind (COUNT(*) AS ?n) WHERE {{
  {{ SELECT ?s WHERE {{ ?s a <{class_uri}> }} LIMIT {sample_size} }}
  ?s ?p ?o .
  OPTIONAL {{ ?o a ?otype }}
  BIND(
    IF(BOUND(?otype), STR(?otype),
      IF(isLiteral(?o), STR(DATATYPE(?o)), "iri-zonder-type")
    ) AS ?target)
  BIND(
    IF(BOUND(?otype), "class",
      IF(isLiteral(?o), "datatype", "iri-zonder-type")
    ) AS ?kind)
}}
GROUP BY ?p ?target ?kind
ORDER BY DESC(?n)
"""
    rows = _rows(execute_sparql(query, timeout=_LONG_QUERY_TIMEOUT))
    paths = [
        {
            "predicate": row.get("p", {}).get("value", ""),
            "target": row.get("target", {}).get("value", ""),
            "kind": row.get("kind", {}).get("value", ""),
            "count": int(row.get("n", {}).get("value", 0)),
        }
        for row in rows
    ]
    return {"class": class_uri, "sample_size": sample_size, "paths": paths}


def explore_incoming_paths(class_uri: str, sample_size: int = 1000) -> dict:
    """Ontdekt vanuit welke klassen en via welke predicaten er naar
    instanties van deze klasse wordt verwezen (achteruit navigeren).

    Gebruik dit voor vragen waarbij het pad omgekeerd loopt, zoals "bij
    welk complex hoort dit rijksmonument": verken inkomend op Rijksmonument
    en je vindt Complex -> heeftRijksmonument.
    """
    sample_size = _clamp_sample_size(sample_size)
    query = f"""
SELECT ?source_class ?p (COUNT(*) AS ?n) WHERE {{
  {{ SELECT ?o WHERE {{ ?o a <{class_uri}> }} LIMIT {sample_size} }}
  ?s ?p ?o .
  OPTIONAL {{ ?s a ?source_class }}
}}
GROUP BY ?source_class ?p
ORDER BY DESC(?n)
"""
    rows = _rows(execute_sparql(query, timeout=_LONG_QUERY_TIMEOUT))
    paths = [
        {
            "source_class": row.get("source_class", {}).get("value", "onbekend"),
            "predicate": row.get("p", {}).get("value", ""),
            "count": int(row.get("n", {}).get("value", 0)),
        }
        for row in rows
    ]
    return {"class": class_uri, "sample_size": sample_size, "incoming_paths": paths}


def format_totals(totals: dict[str, int | str]) -> str:
    return (
        "Live datasettotalen:\n"
        f"Triples: {totals['triples']}\n"
        f"Entiteiten: {totals['entiteiten']}\n"
        f"Klassen: {totals['klassen']}\n"
        f"Properties: {totals['properties']}"
    )


def format_class_partitions(partitions: list[dict]) -> str:
    if not partitions:
        return "Geen klassen gevonden."
    lines = [f"{len(partitions)} klasse(n) met instanties:\n", "klasse | aantal", "-" * 60]
    lines.extend(f"{p['class']} | {p['count']}" for p in partitions)
    return "\n".join(lines)


def format_property_partitions(partitions: list[dict]) -> str:
    if not partitions:
        return "Geen properties gevonden."
    lines = [
        f"{len(partitions)} property/properties met triples:\n",
        "property | aantal",
        "-" * 60,
    ]
    lines.extend(f"{p['property']} | {p['count']}" for p in partitions)
    return "\n".join(lines)


def format_class_paths(result: dict) -> str:
    paths = result["paths"]
    if not paths:
        return (
            f"Geen uitgaande paden gevonden voor {result['class']} "
            f"(steekproef {result['sample_size']})."
        )
    lines = [
        f"{len(paths)} uitgaand pad/paden voor {result['class']} "
        f"(steekproef {result['sample_size']}):\n",
        "predicaat | doel | soort | aantal",
        "-" * 60,
    ]
    lines.extend(
        f"{p['predicate']} | {p['target']} | {p['kind']} | {p['count']}" for p in paths
    )
    return "\n".join(lines)


def format_incoming_paths(result: dict) -> str:
    paths = result["incoming_paths"]
    if not paths:
        return (
            f"Geen inkomende paden gevonden voor {result['class']} "
            f"(steekproef {result['sample_size']})."
        )
    lines = [
        f"{len(paths)} inkomend pad/paden voor {result['class']} "
        f"(steekproef {result['sample_size']}):\n",
        "bronklasse | predicaat | aantal",
        "-" * 60,
    ]
    lines.extend(f"{p['source_class']} | {p['predicate']} | {p['count']}" for p in paths)
    return "\n".join(lines)
