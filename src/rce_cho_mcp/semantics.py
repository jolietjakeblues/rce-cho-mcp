SEMANTIC_TOPICS = {
    "functions": {
        "title": "Functies",
        "description": (
            "Gebruik functiepaden wanneer een vraag gaat over wat een monument is "
            "of oorspronkelijk was. Filter niet op naam of omschrijving."
        ),
        "patterns": [
            {
                "name": "Oorspronkelijke functie",
                "path": [
                    "ceo:heeftOorspronkelijkeFunctie",
                    "ceo:heeftFunctieNaam",
                    "skos:prefLabel",
                ],
                "guidance": (
                    "Gebruik dit pad vaak als eerste bij vragen als boerderijen, "
                    "kerken, begraafplaatsen, kerkhoven, molens, scholen of fabrieken. "
                    "Gebruik hiervoor niet OWMS. Functies lopen via functiepaden naar "
                    "ceo:heeftFunctieNaam en daarna skos:prefLabel."
                ),
            },
            {
                "name": "Huidige functie",
                "path": [
                    "ceo:heeftHuidigeFunctie",
                    "ceo:heeftFunctieNaam",
                    "skos:prefLabel",
                ],
                "guidance": (
                    "Gebruik dit pad wanneer de vraag expliciet gaat over huidig "
                    "gebruik of actuele functie. Gebruik hiervoor niet OWMS; OWMS is "
                    "voor overheidstermen zoals gemeenten en provincies."
                ),
            },
        ],
    },
    "legal_status": {
        "title": "Juridische status",
        "description": (
            "Gebruik juridische status om te bepalen of een object rijksmonument, "
            "voorbeschermd of geen rijksmonument is."
        ),
        "patterns": [
            {
                "name": "Juridische status",
                "path": [
                    "ceo:heeftJuridischeStatus",
                    "skos:prefLabel",
                ],
                "known_values": [
                    "rijksmonument",
                    "voorbeschermd",
                    "geen rijksmonument",
                ],
                "guidance": (
                    "Gebruik dit pad voor vragen over actieve rijksmonumenten of "
                    "juridische status. 'Rijksmonument' is hier een juridische "
                    "statuswaarde, geen OWMS-concept. Gebruik dus niet "
                    "resolve_concept_label('rijksmonument', graph_name='owms'). "
                    "Gebruik hiervoor ook niet ceo:registergegeven."
                ),
            },
        ],
    },
    "monument_aard": {
        "title": "Monumentaard",
        "description": (
            "Gebruik monumentaard om onderscheid te maken tussen archeologische "
            "en gebouwde monumenten."
        ),
        "patterns": [
            {
                "name": "Monumentaard",
                "path": [
                    "ceo:heeftMonumentAard",
                    "skos:prefLabel",
                ],
                "known_values": [
                    "archeologisch",
                    "onroerend gebouwd",
                ],
                "guidance": (
                    "Gebruik dit pad bij vragen over gebouwde of archeologische "
                    "rijksmonumenten. 'Archeologisch' is monumentaard, geen functie "
                    "en geen OWMS-concept."
                ),
            },
        ],
    },
    "names": {
        "title": "Namen",
        "description": (
            "Gebruik namen voor presentatie. Gebruik namen meestal niet als eerste "
            "selectiecriterium."
        ),
        "patterns": [
            {
                "name": "Naam",
                "path": [
                    "ceo:heeftNaam",
                    "ceo:naam",
                ],
                "guidance": (
                    "Gebruik dit pad om een naam te tonen nadat objecten zijn "
                    "geselecteerd via type, functie, locatie of status."
                ),
            },
        ],
    },
    "descriptions": {
        "title": "Omschrijvingen",
        "description": (
            "Gebruik omschrijvingen om uit te leggen waarom of hoe een object "
            "in het register beschreven staat."
        ),
        "patterns": [
            {
                "name": "Omschrijving",
                "path": [
                    "ceo:heeftOmschrijving",
                    "ceo:omschrijving",
                ],
                "guidance": (
                    "Gebruik dit pad voor beschrijvende tekst. Filter hier alleen "
                    "op als er geen beter conceptueel pad bestaat."
                ),
            },
        ],
    },
    "geometry": {
        "title": "Geometrie",
        "description": (
            "Gebruik geometrie om locaties van monumenten op te halen als "
            "coördinaten of WKT-geometrieën. Geometrieën zijn direct bruikbaar "
            "voor kaartvisualisatie; geen coördinaatconversie nodig."
        ),
        "patterns": [
            {
                "name": "Puntgeometrie (WKT)",
                "path": [
                    "geo:hasGeometry",
                    "geo:asWKT",
                ],
                "guidance": (
                    "Gebruik dit pad om de locatie van een monument als WKT op te halen. "
                    "Het resultaat is een POINT-waarde in WGS84 (lon lat), bijvoorbeeld "
                    "POINT(4.9041 52.3676). Geen conversie nodig voor Leaflet of GeoJSON. "
                    "Geometrieën staan in de graph 'punten' of 'instanties-rce'. "
                    "Voeg PREFIX geo: <http://www.opengis.net/ont/geosparql#> toe aan de query. "
                    "Gebruik geen geof:sfWithin of andere GeoSPARQL-relaties voor ruimtelijke "
                    "joins — deze veroorzaken structurele timeouts op het Virtuoso-endpoint. "
                    "Haal in plaats daarvan de WKT-geometrieën op via query_sparql() en voer "
                    "de ruimtelijke join daarna lokaal uit met Shapely in Python. "
                    "Let op: de graph 'linies' gebruikt ceo:asWKT-RD met Rijksdriehoekscoördinaten "
                    "(EPSG:28992), niet WGS84. query_sparql_geojson() slaat die rijen automatisch "
                    "over (zichtbaar als '_skipped' in het resultaat). Gebruik voor linies een "
                    "aparte conversie van RD naar WGS84 vóór visualisatie."
                ),
            },
            {
                "name": "Polygoongeometrie (beschermd stadsgezicht)",
                "path": [
                    "geo:hasGeometry",
                    "geo:asWKT",
                ],
                "guidance": (
                    "Polygonen van beschermde stads- en dorpsgezichten staan in de graph "
                    "'gezicht-hvdl' (URI: https://linkeddata.cultureelerfgoed.nl/graph/gezicht_hvdl). "
                    "Gebruik GRAPH <https://linkeddata.cultureelerfgoed.nl/graph/gezicht_hvdl> "
                    "om polygonen op te halen. Het WKT-formaat is een POLYGON in WGS84. "
                    "Ruimtelijke joins (welke monumenten liggen binnen een stadsgezicht-polygoon) "
                    "moeten lokaal worden uitgevoerd met Shapely; gebruik geof:sfWithin niet."
                ),
            },
        ],
    },
}


def list_topics() -> list[dict]:
    """Return available dataset semantics topics."""
    return [
        {
            "topic": key,
            "title": value["title"],
            "description": value["description"],
        }
        for key, value in sorted(SEMANTIC_TOPICS.items())
    ]


def describe_topic(topic: str) -> dict:
    """Return guidance for a dataset semantics topic."""
    key = topic.lower().strip()

    if key not in SEMANTIC_TOPICS:
        return {
            "found": False,
            "topic": topic,
            "available_topics": sorted(SEMANTIC_TOPICS.keys()),
        }

    return {
        "found": True,
        "topic": key,
        **SEMANTIC_TOPICS[key],
    }


def format_topics() -> str:
    """Return available dataset semantics topics as readable text."""
    lines = ["Beschikbare dataset semantics topics:"]

    for item in list_topics():
        lines.append(
            f"- {item['topic']}: {item['title']} - {item['description']}"
        )

    return "\n".join(lines)


def format_topic(topic: str) -> str:
    """Return dataset semantics guidance as readable text."""
    data = describe_topic(topic)

    if not data["found"]:
        available = ", ".join(data["available_topics"])
        return f"Onbekend semantics topic: {topic}\n\nBeschikbaar: {available}"

    lines = [
        f"Topic: {data['title']}",
        "",
        data["description"],
        "",
        "Patronen:",
    ]

    for pattern in data["patterns"]:
        lines.append(f"- {pattern['name']}")
        lines.append(f"  Pad: {' -> '.join(pattern['path'])}")

        if "known_values" in pattern:
            values = ", ".join(pattern["known_values"])
            lines.append(f"  Bekende waarden: {values}")

        lines.append(f"  Gebruik: {pattern['guidance']}")

    return "\n".join(lines)