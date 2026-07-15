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
from rce_cho_mcp.termennetwerk import lookup_terms, search_terms
from rce_cho_mcp.validator import format_validation_report, validate_sparql
from rce_cho_mcp.stats import (
    class_partitions,
    dataset_totals,
    explore_class_paths,
    explore_incoming_paths,
    format_class_partitions,
    format_class_paths,
    format_incoming_paths,
    format_property_partitions,
    format_totals,
    property_partitions,
)


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
def dataset_statistics() -> str:
    """Geef live datasettotalen: triples, entiteiten, klassen en properties.

    In tegenstelling tot ontology_statistics() (telt wat er in het gebundelde
    ontologiebestand is gedefinieerd) telt dit wat er daadwerkelijk in de
    live, dagelijks ververste data staat. Dit zijn vier opeenvolgende
    full-dataset scans (~58 miljoen triples) en kunnen samen ruim een minuut
    duren, soms tot een paar minuten.
    """
    try:
        return format_totals(dataset_totals())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        code, advies = classify_error(body, e.code)
        return f"[{code}] HTTP {e.code} van {e.url}\n\nAdvies: {advies}"
    except Exception as e:
        return f"Onverwachte fout: {type(e).__name__}: {e}"


@mcp.tool()
def class_instance_counts(only_ceo: bool = True, limit: int = 100) -> str:
    """Telt per klasse het aantal instanties in de live dataset.

    Toont ook welke ontologieklassen NIET in de data voorkomen: klassen die
    in ontology_describe_class() bestaan maar hier ontbreken hebben nul
    instanties in de praktijk. Full-dataset GROUP BY-scan, kan tot ongeveer
    een minuut duren.

    only_ceo: beperk tot klassen in de CEO-namespace (standaard True). Zet
    op False om ook infrastructuurklassen te zien (owl:Class, skos:Concept, ...).
    limit: maximum aantal getoonde klassen (1-1000).
    """
    try:
        return format_class_partitions(class_partitions(only_ceo=only_ceo, limit=limit))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        code, advies = classify_error(body, e.code)
        return f"[{code}] HTTP {e.code} van {e.url}\n\nAdvies: {advies}"
    except Exception as e:
        return f"Onverwachte fout: {type(e).__name__}: {e}"


@mcp.tool()
def property_usage_counts(only_ceo: bool = True, limit: int = 100) -> str:
    """Telt per property het aantal triples in de live dataset.

    Properties met lage aantallen zijn dun gevuld -- relevant om in te
    schatten of een querypad kansrijk is voordat je 'm schrijft. Full-dataset
    GROUP BY-scan, kan tot ongeveer een minuut duren.

    only_ceo: beperk tot properties in de CEO-namespace (standaard True). Zet
    op False om ook infrastructuurproperties te zien (rdf:type, skos:prefLabel, ...).
    limit: maximum aantal getoonde properties (1-1000).
    """
    try:
        return format_property_partitions(property_partitions(only_ceo=only_ceo, limit=limit))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        code, advies = classify_error(body, e.code)
        return f"[{code}] HTTP {e.code} van {e.url}\n\nAdvies: {advies}"
    except Exception as e:
        return f"Onverwachte fout: {type(e).__name__}: {e}"


@mcp.tool()
def explore_class(class_uri: str, sample_size: int = 1000) -> str:
    """Ontdekt welke predicaten vanaf een klasse vertrekken en waar ze
    naartoe leiden (doelklasse of datatype), op basis van een steekproef
    van instanties.

    Gebruik dit om iteratief door de graaf te navigeren bij het opbouwen van
    een querypad: start bij de klasse van de vraag, volg het relevante
    predicaat naar de doelklasse, en verken die opnieuw tot je bij de
    gewenste waarde (literal) bent. In tegenstelling tot
    ontology_describe_class() (statisch) is dit empirisch: het toont ook
    paden die niet in de ontologie gedocumenteerd staan. De getoonde
    aantallen gelden alleen binnen de steekproef, niet voor de hele dataset.

    class_uri: volledige URI van de te verkennen klasse, bijv.
    https://linkeddata.cultureelerfgoed.nl/def/ceo#Rijksmonument
    sample_size: aantal instanties in de steekproef (100-10000).
    """
    try:
        return format_class_paths(explore_class_paths(class_uri, sample_size=sample_size))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        code, advies = classify_error(body, e.code)
        return f"[{code}] HTTP {e.code} van {e.url}\n\nAdvies: {advies}"
    except Exception as e:
        return f"Onverwachte fout: {type(e).__name__}: {e}"


@mcp.tool()
def explore_incoming(class_uri: str, sample_size: int = 1000) -> str:
    """Ontdekt vanuit welke klassen en via welke predicaten er naar
    instanties van deze klasse wordt verwezen (achteruit navigeren).

    Gebruik dit voor vragen waarbij het pad omgekeerd loopt, zoals "bij
    welk complex hoort dit rijksmonument": verken inkomend op Rijksmonument
    en je vindt Complex -> heeftRijksmonument. De getoonde aantallen gelden
    alleen binnen de steekproef, niet voor de hele dataset.

    class_uri: volledige URI van de te verkennen klasse.
    sample_size: aantal instanties in de steekproef (100-10000).
    """
    try:
        return format_incoming_paths(explore_incoming_paths(class_uri, sample_size=sample_size))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        code, advies = classify_error(body, e.code)
        return f"[{code}] HTTP {e.code} van {e.url}\n\nAdvies: {advies}"
    except Exception as e:
        return f"Onverwachte fout: {type(e).__name__}: {e}"


@mcp.tool()
def ontology_search(term: str) -> str:
    """Zoek classes en properties in de CEO-ontologie op naam/trefwoord.

    Dit doorzoekt alleen de schema-definitie (class- en property-namen), geen
    SKOS-concepten of labels in de data. Zoek je een concept/label (bv. een
    functie, plaatsnaam of thesaurusterm), gebruik dan resolve_concept_label()
    of zoek_concept_termennetwerk().
    """
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
def zoek_concept_termennetwerk(
    term: str,
    sources: list[str] | None = None,
    genres: list[str] | None = None,
    max_resultaten: int = 25,
) -> str:
    """Zoek SKOS-concepten op natuurlijke taal via het NDE Termennetwerk (Network of Terms).

    Anders dan resolve_concept_label() (exacte labelmatch binnen onze eigen graphs)
    doet dit een relevantie-gerangschikte zoekopdracht die ook altLabel-synoniemen
    meeneemt, en toont broader/narrower-termen. Gebruik dit wanneer je de exacte
    schrijfwijze van een CHT- of ABR-term niet kent, of om verwante termen te
    ontdekken (bv. "kerk" vindt via narrower ook "kapel").

    sources: lijst van bron-sleutels ('cht', 'abr', 'wikidata', 'aat') of volledige
    bron-URI's. Standaard: cht en abr (de RCE-thesauri).
    genres: optionele lijst van genre-URI's om binnen een bron te filteren; alleen
    ondersteund door bronnen met de GENRE_FILTER-feature (o.a. CHT, AAT, Wikidata).

    Retourneert per bron de gevonden concepten met uri, prefLabel, altLabel,
    definition en broader/narrower termen. Gebruik de gevonden URI in een SPARQL
    VALUES-filter, of controleer met resolve_concept_label() of de URI ook
    daadwerkelijk in onze eigen dataset voorkomt.
    """
    try:
        resultaten = search_terms(term, sources=sources, genres=genres, max_results=max_resultaten)
    except RuntimeError as e:
        return f"Fout bij zoeken in Termennetwerk: {e}"

    if not resultaten:
        return f"Geen bronnen doorzocht voor '{term}'."

    lines = [f"Zoekresultaten Termennetwerk voor '{term}':"]

    for bron in resultaten:
        naam = bron.get("source", {}).get("name", "onbekende bron")
        result = bron.get("result", {})

        if result.get("__typename") == "Error":
            lines.append(f"\n{naam}: fout — {result.get('message')}")
            continue

        termen = result.get("terms", [])
        lines.append(f"\n{naam} ({len(termen)} match(es)):")

        for t in termen:
            pref = "; ".join(t.get("prefLabel") or [])
            alt = "; ".join(t.get("altLabel") or [])
            lines.append(f"- {t['uri']}")
            lines.append(f"  prefLabel: {pref}" + (f" | altLabel: {alt}" if alt else ""))

            broader = t.get("broader") or []
            narrower = t.get("narrower") or []
            if broader:
                labels = ", ".join(b["prefLabel"][0] if b.get("prefLabel") else b["uri"] for b in broader)
                lines.append(f"  broader: {labels}")
            if narrower:
                labels = ", ".join(n["prefLabel"][0] if n.get("prefLabel") else n["uri"] for n in narrower)
                lines.append(f"  narrower: {labels}")

    return "\n".join(lines)

@mcp.tool()
def lookup_termennetwerk_uri(uris: list[str]) -> str:
    """Vertaal een of meer externe concept-URI's terug naar leesbare labels, via het
    NDE Termennetwerk.

    Gebruik dit voor URI's buiten onze eigen dataset, bijvoorbeeld een
    skos:exactMatch-link naar Wikidata of AAT die je met describe_resource_uri()
    tegenkomt, of een CHT/ABR-URI waarvan je alleen de URI hebt onthouden.
    """
    try:
        resultaten = lookup_terms(uris)
    except RuntimeError as e:
        return f"Fout bij opzoeken in Termennetwerk: {e}"

    if not resultaten:
        return "Geen resultaten."

    lines = []
    for item in resultaten:
        uri = item.get("uri", "")
        bron = item.get("source") or {}
        result = item.get("result") or {}

        if "message" in bron:
            lines.append(f"{uri}: bron niet herkend ({bron['message']})")
            continue
        if "message" in result:
            lines.append(f"{uri}: niet gevonden ({result['message']})")
            continue

        pref = "; ".join(result.get("prefLabel") or [])
        bron_naam = bron.get("name", "onbekende bron")
        lines.append(f"{uri} ({bron_naam}): {pref}")

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
    """Controleert een SPARQL-query op bekende RCE CHO-valkuilen, zonder de
    query uit te voeren: verdachte/niet-bestaande prefixes, een taalgetagd
    label vergelijken met een kale string (zie query_sparql), ORDER BY samen
    met OPTIONAL (geeft consistent HTTP 504) en cartesisch-productrisico bij
    meerdere onafhankelijke multi-valued OPTIONAL-blokken.

    Valideert geen classes of properties tegen de ontologie -- gebruik
    daarvoor ontology_search()/ontology_describe_class(). Geeft platte tekst
    terug; gebruik validate_query_structured() als je errors en warnings los
    wilt verwerken.
    """
    return format_validation_report(sparql_query)

@mcp.tool()
def validate_query_structured(sparql_query: str) -> dict:
    """Zelfde controles als validate_query(), maar als
    {"valid": bool, "errors": [...], "warnings": [...]} in plaats van platte
    tekst -- gebruik dit wanneer je programmatisch op errors/warnings wilt
    reageren, bv. vóór query_sparql() om het taalgetag-labelpatroon te checken.
    """
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
    """Voer een SPARQL SELECT of ASK query uit en geef het ruwe JSON-resultaat terug.

    Let op: skos:prefLabel-waarden zijn taalgetagd (bv. "Zwolle"@nl). Een
    FILTER die een labelvariabele vergelijkt met een kale string (FILTER(?label
    = "Zwolle") of FILTER(?label IN (...))) geeft stil 0 resultaten, zonder
    fout. Gebruik resolve_concept_label() om eerst de concept-URI op te
    halen, of wrap de vergelijking in STR(). Gebruik validate_query_structured()
    om dit patroon vooraf te laten controleren.
    """
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

    Let op: skos:prefLabel-waarden zijn taalgetagd (bv. "Zwolle"@nl). Een FILTER
    die een labelvariabele vergelijkt met een kale string geeft stil 0 resultaten,
    zonder fout -- gebruik resolve_concept_label() of wrap de vergelijking in
    STR(). Zie query_sparql() voor details.

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
