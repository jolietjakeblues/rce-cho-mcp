"""Gemeente-resolutie en een gecombineerde gemeente/juridische-status-filter.

## Waarom deze module bestaat

Drie terugkerende knelpunten in gebruik van deze server (zie memory
rce-verbetervoorstel / rce-sparql-patronen):

1. Een gemeentenaam moet eerst naar een OWMS concept-URI vertaald worden
   voordat je 'm in een SPARQL-filter kunt gebruiken -- en
   resolve_concept_label() op graph "owms" matcht zonder verder filter ook
   gelijknamige provincies en kadastrale gemeenten (bv. "Utrecht" is zowel
   gemeente als provincie, elk een eigen concept met hetzelfde
   skos:prefLabel). Live geverifieerd (2026-10-29): skos:prefLabel
   "Utrecht"@nl matcht drie concepten in de owms-graph
   (.../Utrecht_(gemeente), .../Utrecht_(provincie),
   .../Utrecht_(kadastrale_gemeente)), onderscheiden door hun rdf:type
   (resp. .../owms/terms/Gemeente, .../owms/terms/Provincie,
   .../owms/terms/KadastraleGemeente). resolve_gemeente() hieronder filtert
   daarom altijd op type Gemeente.
2. Rijksmonument-vragen moeten de graph 'instanties-rce' gebruiken (anders
   dubbeltellingen, zie prompts.py) en meestal ook filteren op
   ceo:heeftJuridischeStatus = "rijksmonument" (anders telt een naieve
   "alle objecten van class Rijksmonument"-telling ook voorbeschermde en
   afgevoerde ("geen rijksmonument") objecten mee -- dat zijn juridische
   statuswaarden, geen aparte classes).
3. De gemeentekoppeling op een monument loopt via
   ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente (zie brk_spatial.py,
   waar dit pad al gebruikt wordt om de KKG-perceelscan te beperken).

monumenten_in_gemeente() combineert deze drie stappen in één aanroep, met
dezelfde dubbeltellings-/timeoutvoorzorgen als largest_by_area() in area.py
(DISTINCT op elk niveau, filteren/limiteren vóór de OPTIONAL-naam/nummer-
joins in een binnenste subquery, zodat de bekende "ORDER BY + OPTIONAL"-
504-valkuil niet kan optreden).
"""

from __future__ import annotations

import re

from rce_cho_mcp.config import DEFAULT_DATASET_GRAPH as _INSTANTIES_GRAPH
from rce_cho_mcp.limits import LIST_MAX_LIMIT
from rce_cho_mcp.ontology.registry import get_classes
from rce_cho_mcp.queries import build_name_lookup_query
from rce_cho_mcp.semantics import get_known_value_uris
from rce_cho_mcp.sparql import escape_sparql_string, execute_sparql
from rce_cho_mcp.sparql import rows as _sparql_rows

_OWMS_GRAPH = "https://linkeddata.cultureelerfgoed.nl/graph/owms"
_GEMEENTE_TYPE_URI = "http://standaarden.overheid.nl/owms/terms/Gemeente"
_QUERY_TIMEOUT = 60

_MIN_LIMIT = 1
_MAX_LIMIT = LIST_MAX_LIMIT

# Eén bron: semantics_describe_topic('legal_status')/('monument_aard') --
# zie get_known_value_uris() in semantics.py. Ook gebruikt door area.py, zodat
# deze concept-URI's niet in meerdere modules los gedupliceerd staan.
_LEGAL_STATUS_URIS = get_known_value_uris("legal_status")
_MONUMENT_AARD_URIS = get_known_value_uris("monument_aard")

# Normaliseert invoer die de gebruiker soms al in wiki/URI-stijl aanlevert
# (zie memory rce-monumentadressen-datakwaliteit), bv. "Utrecht (gemeente)".
# Ook gebruikt door brk_spatial.py (gemeentenaam afgeleid uit een OWMS-URI).
GEMEENTE_SUFFIX_RE = re.compile(r"[_ ]?\(gemeente\)$", re.IGNORECASE)


def _clamp_limit(limit: int) -> int:
    return max(_MIN_LIMIT, min(limit, _MAX_LIMIT))


def _normalize_gemeente_naam(naam: str) -> str:
    naam = naam.strip()
    return GEMEENTE_SUFFIX_RE.sub("", naam).strip()


def resolve_gemeente(naam: str) -> dict:
    """Resolveer een gemeentenaam naar zijn OWMS concept-URI.

    Filtert, anders dan een kale resolve_concept_label(graph_name="owms"),
    altijd op rdf:type owms:Gemeente -- zodat een gelijknamige provincie of
    kadastrale gemeente (bv. "Utrecht", "Groningen", "Overijssel") niet als
    kandidaat meekomt.

    Retourneert {"uri", "naam"} bij precies één match, of {"error", ...}
    bij nul of meerdere matches (bv. bij een niet-bestaande of ambigue
    schrijfwijze) -- gokt niet.
    """
    schoon = _normalize_gemeente_naam(naam)
    if not schoon:
        return {"error": "Lege gemeentenaam."}

    safe = escape_sparql_string(schoon)
    query = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?concept WHERE {{
  GRAPH <{_OWMS_GRAPH}> {{
    ?concept skos:prefLabel "{safe}"@nl ;
      a <{_GEMEENTE_TYPE_URI}> .
  }}
}}
"""
    data = execute_sparql(query, timeout=_QUERY_TIMEOUT)
    uris = [row["concept"]["value"] for row in _sparql_rows(data)]

    if not uris:
        return {
            "error": (
                f"Geen gemeente gevonden met naam '{naam}' in de OWMS-graph "
                "(type Gemeente). Controleer de schrijfwijze, of gebruik "
                "resolve_concept_label(graph_name='owms') zonder typefilter "
                "om te zien welke OWMS-concepten er wel zijn voor dit label."
            )
        }
    if len(uris) > 1:
        return {
            "error": (
                f"Meerdere gemeenten gevonden voor '{naam}' -- kies de juiste URI."
            ),
            "kandidaten": uris,
        }

    return {"uri": uris[0], "naam": schoon}


def monumenten_in_gemeente(
    gemeente: str,
    juridische_status: str | None = "rijksmonument",
    class_name: str = "Rijksmonument",
    monument_aard: str | None = None,
    limit: int = 50,
) -> dict:
    """Tel en toon monumenten in een gemeente, met automatische
    gemeente-resolutie, de juiste graph en een juridische-statusfilter.

    juridische_status: "rijksmonument" (standaard), "voorbeschermd",
    "geen rijksmonument", of "alle" om niet op status te filteren.

    Retourneert bij succes {"gemeente", "gemeente_uri", "class_name",
    "class_uri", "juridische_status", "monument_aard", "aantal", "rows"}
    ("aantal" geldt voor de volledige set, "rows" is de steekproef tot
    limit), of {"error": ...} bij een onbekende gemeente/class/status/aard.
    """
    limit = _clamp_limit(limit)

    gem = resolve_gemeente(gemeente)
    if "error" in gem:
        return gem

    class_uri = get_classes().get(class_name)
    if class_uri is None:
        return {
            "error": f"Onbekende class: {class_name}",
            "beschikbare_classes_voorbeeld": sorted(get_classes().keys())[:50],
        }

    status_filter = ""
    if juridische_status is not None and juridische_status != "alle":
        status_uri = _LEGAL_STATUS_URIS.get(juridische_status)
        if status_uri is None:
            return {
                "error": f"Onbekende juridische_status: {juridische_status!r}",
                "beschikbare_juridische_status_waarden": sorted(_LEGAL_STATUS_URIS.keys()) + ["alle"],
            }
        status_filter = f"?obj ceo:heeftJuridischeStatus <{status_uri}> ."

    aard_filter = ""
    if monument_aard is not None:
        aard_uri = _MONUMENT_AARD_URIS.get(monument_aard)
        if aard_uri is None:
            return {
                "error": f"Onbekende monument_aard: {monument_aard!r}",
                "beschikbare_monument_aard_waarden": sorted(_MONUMENT_AARD_URIS.keys()),
            }
        aard_filter = f"?obj ceo:heeftMonumentAard <{aard_uri}> ."

    count_query = f"""
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
SELECT (COUNT(DISTINCT ?obj) AS ?aantal) WHERE {{
  GRAPH <{_INSTANTIES_GRAPH}> {{
    ?obj a <{class_uri}> ;
      ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente <{gem['uri']}> .
    {status_filter}
    {aard_filter}
  }}
}}
"""
    count_rows = _sparql_rows(execute_sparql(count_query, timeout=_QUERY_TIMEOUT))
    aantal = int(count_rows[0]["aantal"]["value"]) if count_rows else 0

    # build_name_lookup_query() wrapt dit met de standaard naam/nummer-
    # OPTIONALs op de al-beperkte set (zie queries.py) -- zelfde tweetraps-
    # mechanisme als largest_by_area() in area.py, nu gedeeld in plaats van
    # met de hand herschreven.
    inner_select = f"""{{
    SELECT DISTINCT ?obj WHERE {{
      GRAPH <{_INSTANTIES_GRAPH}> {{
        ?obj a <{class_uri}> ;
          ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente <{gem['uri']}> .
        {status_filter}
        {aard_filter}
      }}
    }}
    LIMIT {limit}
  }}"""
    sample_query = build_name_lookup_query(
        outer_vars="?obj ?rijksmonumentnummer ?naam",
        inner_select=inner_select,
        subject_var="obj",
    )
    sample_rows = _sparql_rows(execute_sparql(sample_query, timeout=_QUERY_TIMEOUT))

    rows = [
        {
            "obj": row["obj"]["value"],
            "rijksmonumentnummer": row.get("rijksmonumentnummer", {}).get("value"),
            "naam": row.get("naam", {}).get("value"),
        }
        for row in sample_rows
    ]

    return {
        "gemeente": gem["naam"],
        "gemeente_uri": gem["uri"],
        "class_name": class_name,
        "class_uri": class_uri,
        "juridische_status": juridische_status,
        "monument_aard": monument_aard,
        "aantal": aantal,
        "rows": rows,
    }


def format_monumenten_in_gemeente(result: dict) -> str:
    if "error" in result:
        extra = (
            result.get("kandidaten")
            or result.get("beschikbare_classes_voorbeeld")
            or result.get("beschikbare_juridische_status_waarden")
            or result.get("beschikbare_monument_aard_waarden")
        )
        lines = [result["error"]]
        if extra:
            lines.append("Beschikbaar: " + ", ".join(extra))
        return "\n".join(lines)

    status_suffix = (
        f", status: {result['juridische_status']}" if result["juridische_status"] else ""
    )
    aard_suffix = f", monumentaard: {result['monument_aard']}" if result["monument_aard"] else ""

    lines = [
        f"{result['class_name']} in gemeente {result['gemeente']}{status_suffix}{aard_suffix}:",
        f"Aantal: {result['aantal']}",
        f"Gemeente-URI: {result['gemeente_uri']}",
        "",
        f"Steekproef ({len(result['rows'])} van {result['aantal']}):",
        "rijksmonumentnummer | naam | uri",
        "-" * 60,
    ]
    for row in result["rows"]:
        nummer = row["rijksmonumentnummer"] or "-"
        naam = row["naam"] or "-"
        lines.append(f"{nummer} | {naam} | {row['obj']}")

    return "\n".join(lines)
