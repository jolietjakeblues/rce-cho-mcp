"""Oppervlakteberekening op basis van polygoongeometrie (geof:area).

ceo:oppervlakteInVierkanteMeters bestaat alleen op de ~1.400 Geometrie-objecten
die via ceo:heeftAanlegGeometrie aan een historische buitenplaats/tuin hangen.
Voor de overige ~61.500 rijksmonumenten (gebouwen, archeologische terreinen,
forten, vliegvelden, ...) is er geen vergelijkbaar gematerialiseerd veld.

Deze module berekent de oppervlakte in plaats daarvan on-the-fly met de
GeoSPARQL-functie geof:area() op de hoofdgeometrie (ceo:heeftGeometrie ->
geo:asWKT), voor de subset monumenten die daar een POLYGON/MULTIPOLYGON
(i.p.v. een POINT) hebben staan.

Geverifieerd tegen het live endpoint (2026-09-03):
- geof:area(?wkt, uom:metre) is beschikbaar op dit Virtuoso-endpoint en
  verwacht *twee* argumenten (de wkt-literal en een eenheid-URI) -- met één
  argument geeft het endpoint HTTP 400 "Expected 2 argument, but got 1".
  Met uom:metre levert het een geodetische oppervlakte in vierkante meters,
  direct uit WGS84-coordinaten (getest op een 1x1 graad vierkant nabij de
  evenaar: ~1.236e10 m2, wat overeenkomt met een ellipsoidische berekening).
- Van de ~128.896 ceo:heeftGeometrie-triples op ceo:Rijksmonument is de
  overgrote meerderheid (104.236) een POINT, zonder oppervlakte. Slechts
  14.291 zijn POLYGON en 10.369 MULTIPOLYGON (~19% van het totaal) -- alleen
  die subset kan hiermee een oppervlakte krijgen.
- BELANGRIJK, los ontdekt pitfall: de WKT-literals in deze dataset gebruiken
  gemengde hoofdletters MET spatie voor het type-keyword, bv. "Polygon (...)"
  en "Point (...)", niet de striktere vorm "POLYGON(...)" die je in externe
  WKT-voorbeelden vaak ziet. Een FILTER(STRSTARTS(STR(?wkt), "POLYGON")) of
  CONTAINS-check zonder case-insensitive REGEX geeft hierdoor stil 0
  resultaten. Gebruik daarom altijd REGEX(STR(?wkt), "^\\s*(multi)?polygon",
  "i") (zoals in dit module) in plaats van STRSTARTS/CONTAINS op de kale
  string.
- ORDER BY gecombineerd met OPTIONAL-joins geeft op dit endpoint consistent
  een HTTP 504 (zie validator.py). Deze module vermijdt dat met de
  tweetraps-subquery-truc: eerst sorteren/limiteren op de berekende
  oppervlakte in een binnenste SELECT DISTINCT (geen OPTIONAL), pas daarna
  naam en rijksmonumentnummer via OPTIONAL toevoegen in de buitenste query
  op de al-beperkte set.
- SELECT DISTINCT is nodig op zowel het binnenste als het buitenste niveau:
  ceo:heeftGeometrie (en dus ook de erop volgende naam/nummer-OPTIONALs)
  komt vaak dubbel voor per object (zelfde bekende dubbeltellingsissue als
  heeftJuridischeStatus/heeftMonumentAard), zonder DISTINCT verschijnt elke
  rij tweemaal.
- Voorbeeldresultaat (live, LIMIT 5, class=Rijksmonument): grootste is
  "Deelen/Vliegveld" (rijksmonumentnummer 529782) met ~8,67 km2.
"""

from rce_cho_mcp.ontology.registry import get_classes
from rce_cho_mcp.sparql import execute_sparql

_DEFAULT_CLASS = "Rijksmonument"
_INSTANTIES_GRAPH = "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce"
_QUERY_TIMEOUT = 60

_MIN_LIMIT = 1
_MAX_LIMIT = 100

# Zie semantics_describe_topic('monument_aard'): ceo:heeftMonumentAard kent
# precies deze twee waarden. Hier herbruikt zodat "grootste archeologische
# monumenten qua oppervlakte" in 1 tool call kan, zonder ooit ruwe WKT naar de
# aanroeper te sturen (zie query_sparql's docstring voor waarom dat bij
# grotere aantallen de tool-resultaatlimiet raakt).
_MONUMENT_AARD_URIS = {
    "archeologisch": "https://data.cultureelerfgoed.nl/term/id/rn/2/b673c8c1-5d93-496d-8f9e-89133d579d77",
    "onroerend gebouwd": "https://data.cultureelerfgoed.nl/term/id/rn/2/fc966a68-8863-4970-a83e-110f96006c21",
}


def _clamp_limit(limit: int) -> int:
    return max(_MIN_LIMIT, min(limit, _MAX_LIMIT))


def _resolve_class_uri(class_name: str) -> str | None:
    """Resolveer een class-naam (bv. 'Rijksmonument') naar de volledige URI
    via de ingelezen CEO-ontologie. Geeft None terug als de naam onbekend is.
    """
    return get_classes().get(class_name)


def largest_by_area(
    limit: int = 10, class_name: str = _DEFAULT_CLASS, monument_aard: str | None = None
) -> dict:
    """Zoek de monumenten met de grootste polygoon-oppervlakte in de live dataset.

    monument_aard: optioneel, "archeologisch" of "onroerend gebouwd" (zie
    semantics_describe_topic('monument_aard')) om te filteren op
    ceo:heeftMonumentAard. Alleen zinvol in combinatie met class_name
    "Rijksmonument" (het enige domain van deze property).

    Retourneert {"class_name", "class_uri", "limit", "monument_aard", "rows": [...]}
    of {"error": ...} bij een onbekende class_name/monument_aard. Elke rij in
    "rows" heeft "rm" (URI), "oppervlakte_m2" (float), "naam" (str|None) en
    "rijksmonumentnummer" (str|None).
    """
    limit = _clamp_limit(limit)
    class_uri = _resolve_class_uri(class_name)

    if class_uri is None:
        return {
            "error": f"Onbekende class: {class_name}",
            "beschikbare_classes_voorbeeld": sorted(get_classes().keys())[:50],
        }

    monument_aard_filter = ""
    if monument_aard is not None:
        aard_uri = _MONUMENT_AARD_URIS.get(monument_aard)
        if aard_uri is None:
            return {
                "error": f"Onbekende monument_aard: {monument_aard!r}",
                "beschikbare_monument_aard_waarden": sorted(_MONUMENT_AARD_URIS.keys()),
            }
        monument_aard_filter = f"?rm ceo:heeftMonumentAard <{aard_uri}> ."

    query = f"""
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX uom: <http://www.opengis.net/def/uom/OGC/1.0/>
SELECT DISTINCT ?rm ?opp ?naam ?rijksmonumentnummer WHERE {{
  {{
    SELECT DISTINCT ?rm (geof:area(?wkt, uom:metre) AS ?opp)
    WHERE {{
      GRAPH <{_INSTANTIES_GRAPH}> {{
        ?rm a <{class_uri}> ; ceo:heeftGeometrie ?geomObj .
        {monument_aard_filter}
      }}
      ?geomObj geo:asWKT ?wkt .
      FILTER(REGEX(STR(?wkt), "^\\\\s*(multi)?polygon", "i"))
    }}
    ORDER BY DESC(?opp)
    LIMIT {limit}
  }}
  OPTIONAL {{ ?rm ceo:heeftNaam ?nObj . ?nObj ceo:naam ?naam . }}
  OPTIONAL {{ ?rm ceo:rijksmonumentnummer ?rijksmonumentnummer . }}
}}
ORDER BY DESC(?opp)
"""
    data = execute_sparql(query, timeout=_QUERY_TIMEOUT)
    bindings = data.get("results", {}).get("bindings", [])

    rows = [
        {
            "rm": row["rm"]["value"],
            "oppervlakte_m2": float(row["opp"]["value"]),
            "naam": row.get("naam", {}).get("value"),
            "rijksmonumentnummer": row.get("rijksmonumentnummer", {}).get("value"),
        }
        for row in bindings
    ]

    return {
        "class_name": class_name,
        "class_uri": class_uri,
        "limit": limit,
        "monument_aard": monument_aard,
        "rows": rows,
    }


def format_largest_by_area(result: dict) -> str:
    if "error" in result:
        available = ", ".join(
            result.get("beschikbare_classes_voorbeeld")
            or result.get("beschikbare_monument_aard_waarden")
            or []
        )
        return f"{result['error']}\n\nBeschikbaar:\n{available}"

    rows = result["rows"]
    aard_suffix = f" (monumentaard: {result['monument_aard']})" if result["monument_aard"] else ""
    if not rows:
        return (
            f"Geen monumenten met polygoon-/multipolygoon-geometrie gevonden "
            f"voor class {result['class_name']}{aard_suffix} ({result['class_uri']})."
        )

    lines = [
        f"Top {len(rows)} grootste {result['class_name']}(s){aard_suffix} qua "
        "oppervlakte (alleen monumenten met polygoon-/multipolygoon-geometrie op "
        "ceo:heeftGeometrie -- monumenten met alleen een puntgeometrie hebben "
        "geen berekenbare oppervlakte en zitten hier niet in):\n",
        "rijksmonumentnummer | naam | oppervlakte (m2) | uri",
        "-" * 60,
    ]
    for row in rows:
        naam = row["naam"] or "-"
        nummer = row["rijksmonumentnummer"] or "-"
        lines.append(f"{nummer} | {naam} | {row['oppervlakte_m2']:,.0f} | {row['rm']}")

    return "\n".join(lines)
