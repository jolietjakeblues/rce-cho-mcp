import urllib.error

from mcp.server.fastmcp import FastMCP

from rce_cho_mcp.ontology.api import (
    describe_class,
    describe_property,
    search_ontology,
    statistics,
)
from rce_cho_mcp.prompts import WORKFLOW_INSTRUCTIONS
from rce_cho_mcp.resolver import describe_resource, resolve_label
from rce_cho_mcp.semantics import format_topic, format_topics
from rce_cho_mcp.sparql import classify_error, execute_sparql, format_results, rd_to_wgs84, to_geojson
from rce_cho_mcp.graphs import format_graphs
from rce_cho_mcp.validator import format_validation_report, validate_sparql


mcp = FastMCP("RCE CHO SPARQL", instructions=WORKFLOW_INSTRUCTIONS)


@mcp.tool()
def ping() -> str:
    """Test of de MCP-server bereikbaar is."""
    return "RCE CHO MCP werkt."

@mcp.tool()
def graphs_list() -> str:
    """Toon bekende CHO named graphs."""
    return format_graphs()

@mcp.tool()
def ontology_statistics() -> str:
    """Geef statistieken over de ingelezen CEO-ontologie."""
    stats = statistics()
    return (
        "CEO-ontologie geladen.\n"
        f"Classes: {stats['classes']}\n"
        f"Properties: {stats['properties']}"
    )

@mcp.tool()
def ontology_search(term: str) -> str:
    """Zoek classes en properties in de CEO-ontologie."""
    return search_ontology(term)


@mcp.tool()
def ontology_describe_class(class_name: str) -> str:
    """Beschrijf een CEO-class op basis van de ingelezen ontologie."""
    return describe_class(class_name)

@mcp.tool()
def ontology_describe_property(property_name: str) -> str:
    """Beschrijf een CEO-property op basis van de ingelezen ontologie."""
    return describe_property(property_name)

@mcp.tool()
def semantics_list_topics() -> str:
    """Toon beschikbare dataset-semantiek onderwerpen."""
    return format_topics()

@mcp.tool()
def semantics_describe_topic(topic: str) -> str:
    """Geef interpretatieregels voor een dataset-semantiek onderwerp."""
    return format_topic(topic)

@mcp.tool()
def resolve_concept_label(label: str, graph_name: str = "owms", lang: str = "nl") -> str:
    """Resolveer een SKOS prefLabel in een specifieke named graph.

    Gebruik graph_name="owms" alleen voor overheidstermen zoals gemeenten en provincies.
    Gebruik deze tool niet blind voor functies, juridische status of monumentaard.
    Raadpleeg eerst semantics_describe_topic() en graphs_list() wanneer je niet weet
    in welke graph een concept staat.

    BELANGRIJK: skos:prefLabel-waarden zijn taalgetagd (bv. "Zwolle"@nl). Filter
    of match nooit rechtstreeks op een label-string in zelfgeschreven SPARQL
    (bv. FILTER(?label = "Zwolle") of FILTER(?label IN (...))) — dat matcht een
    taalgetagde RDF-term niet en geeft stil 0 resultaten, zonder foutmelding.
    Gebruik altijd eerst deze tool om de concept-URI op te halen, en filter of
    join daarna op die URI in plaats van op de labeltekst.
    """
    try:
        matches = resolve_label(label, graph_name=graph_name, lang=lang)
    except (ValueError, RuntimeError) as e:
        return f"Fout bij resolven van label '{label}': {e}"

    if not matches:
        return f"Geen concept gevonden voor label '{label}' in graph:{graph_name}."

    lines = [f"{len(matches)} match(es) gevonden voor '{label}' in graph:{graph_name}:"]

    for match in matches:
        types = ", ".join(match["types"]) if match["types"] else "onbekend"
        lines.append(f"- {match['uri']} (type: {types})")

    return "\n".join(lines)

@mcp.tool()
def describe_resource_uri(uri: str) -> str:
    """Beschrijf een resource: alle predicaten en waarden van een URI in de RCE-graph."""
    try:
        facts = describe_resource(uri)
    except RuntimeError as e:
        return f"Fout bij opvragen van resource: {e}"

    if not facts:
        return f"Geen gegevens gevonden voor resource: {uri}"

    lines = [f"{len(facts)} eigenschap(pen) gevonden voor {uri}:"]
    lines.extend(f"- {fact['predicate']} -> {fact['object']}" for fact in facts)

    return "\n".join(lines)

@mcp.tool()
def validate_query(sparql_query: str) -> str:
    """Valideer een SPARQL-query zonder deze uit te voeren."""
    return format_validation_report(sparql_query)

@mcp.tool()
def validate_query_structured(sparql_query: str) -> dict:
    """Valideer een SPARQL-query en geef errors/warnings gestructureerd terug."""
    return validate_sparql(sparql_query)

@mcp.tool()
def query_sparql(sparql_query: str, max_rows: int = 100) -> str:
    """Voer een SPARQL SELECT of ASK query uit op het RCE CHO endpoint.

    Let op: skos:prefLabel-waarden zijn taalgetagd (bv. "Zwolle"@nl). Een
    FILTER die een labelvariabele vergelijkt met een kale string (FILTER(?label
    = "Zwolle") of FILTER(?label IN (...))) geeft stil 0 resultaten, zonder
    fout. Gebruik resolve_concept_label() om eerst de concept-URI op te
    halen, of wrap de vergelijking in STR(). Gebruik validate_query_structured()
    om dit patroon vooraf te laten controleren.
    """
    try:
        data = execute_sparql(sparql_query)
        return format_results(data, max_rows=max_rows)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        code, advies = classify_error(body, e.code)
        return (
            f"[{code}] HTTP {e.code} van {e.url}\n\n"
            f"Advies: {advies}\n\n"
            f"Ruwe foutmelding:\n{body[:500]}"
        )

    except Exception as e:
        return f"Onverwachte fout: {type(e).__name__}: {e}"

@mcp.tool()
def query_sparql_json(sparql_query: str) -> dict:
    """Voer een SPARQL SELECT of ASK query uit en geef het ruwe JSON-resultaat terug."""
    try:
        return execute_sparql(sparql_query)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        code, advies = classify_error(body, e.code)
        return {
            "error": code,
            "status": e.code,
            "advies": advies,
            "endpoint": e.url,
            "body": body[:500],
        }

    except Exception as e:
        return {
            "error": "unexpected_error",
            "type": type(e).__name__,
            "message": str(e),
        }

@mcp.tool()
def query_sparql_geojson(
    sparql_query: str,
    wkt_var: str = "wkt",
    convert_rd: bool = False,
) -> dict:
    """Voer een SPARQL SELECT query uit en geef het resultaat terug als GeoJSON FeatureCollection.

    wkt_var: naam van de resultaatvariabele die de WKT-geometrie bevat (standaard: 'wkt').
    convert_rd: zet op True wanneer de query RD-coördinaten (EPSG:28992) oplevert,
                bijvoorbeeld bij de graph 'linies' (ceo:asWKT-RD). De coördinaten
                worden dan automatisch omgezet naar WGS84.
    Ondersteunt POINT, POLYGON en MULTIPOLYGON.
    Alle overige variabelen worden als feature properties meegenomen.
    Rijen zonder geldige geometrie worden overgeslagen (zie '_skipped' in het resultaat).

    Gebruik geo:asWKT in de query om geometrieën op te halen. Voeg toe aan de query:
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    """
    try:
        data = execute_sparql(sparql_query)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        code, advies = classify_error(body, e.code)
        return {
            "error": code,
            "status": e.code,
            "advies": advies,
            "endpoint": e.url,
            "body": body[:500],
        }
    except Exception as e:
        return {
            "error": "unexpected_error",
            "type": type(e).__name__,
            "message": str(e),
        }

    return to_geojson(data, wkt_var=wkt_var, convert_rd=convert_rd)


@mcp.tool()
def convert_rd_to_wgs84(x: float, y: float) -> dict:
    """Converteer een enkel RD New (EPSG:28992) coördinatenpaar naar WGS84.

    x: RD X-coördinaat (easting, ca. 0–300.000)
    y: RD Y-coördinaat (northing, ca. 300.000–625.000)

    Geeft {'lon': ..., 'lat': ...} terug in decimale graden.
    """
    lon, lat = rd_to_wgs84(x, y)
    return {"lon": lon, "lat": lat}


def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()
