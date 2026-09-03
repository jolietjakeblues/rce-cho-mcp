"""Spatial join tussen RCE-monumentgeometrie en Kadaster KKG-percelen.

## Het probleem met RCE's eigen BRK-relatie

RCE houdt per rijksmonument een ceo:BasisregistratieRelatie -> ceo:BRKRelatie
bij (gemeentenaam/sectie/perceelnummer). Deze koppeling is niet gegarandeerd
compleet: bij het ene monument staan alle onderliggende percelen expliciet
vermeld, bij het andere staat er maar één met de aantekening "exacte
punt-in-perceel match" -- kennelijk een ankerpunt, geen uitputtende lijst.
Je weet vooraf niet welk van de twee je voor je hebt.

## De oplossing hier: een echte spatial join

In plaats van op de tekstuele BRK-relatie te vertrouwen, berekent deze module
het antwoord opnieuw vanuit geometrie: RCE's monumentpolygoon (ceo:heeftGeometrie
-> geo:asWKT, WGS84) tegen Kadaster-percelen (imxgeo:Perceel ->
geosparql:hasGeometry -> geosparql:asWKT, ook WGS84 -- BELANGRIJK: dus GEEN
RD-conversie nodig, in weerwil van wat je op basis van "kadastrale data" zou
verwachten) via de GeoSPARQL-relatie geof:sfIntersects.

## Live geverifieerde bevindingen (2026-09-03) die de aanpak hieronder bepalen

- RCE (api.linkeddata.cultureelerfgoed.nl) en KKG (api.labs.kadaster.nl) zijn
  twee aparte SPARQL-endpoints; een query kan ze dus niet in één FROM/GRAPH
  combineren.
- SPARQL SERVICE-federatie werkt WEL in beide richtingen voor eenvoudige
  lookups (bv. ?s ?p ?o op een bekende URI via SERVICE naar het andere
  endpoint). Maar: een query die een buiten de SERVICE-clause gebonden
  variabele (de RCE-WKT) gebruikt in een geof:sfIntersects-FILTER BINNEN de
  SERVICE-clause naar KKG leverde in test consistent 0 resultaten op -- de
  externe binding lijkt niet correct doorgegeven te worden aan de remote
  filter-evaluatie. Daarom doet deze module de join client-side met twee
  losse HTTP-calls (RCE ophalen, dan de WKT als literal in een KKG-query
  plakken) in plaats van één federated SPARQL-query.
- KKG's imxgeo:Perceel-geometrie gebruikt het Virtuoso-eigen datatype
  virtrdf:Geometry (niet het generieke geosparql:wktLiteral dat RCE
  gebruikt), vermoedelijk met een spatial index erachter. Virtuoso's eigen
  bif:st_intersects/bif:st_area/bif:st_point-functies zijn via dit gehoste
  endpoint echter niet bruikbaar (consistent HTTP 500, ook op een triviale
  zelf-intersect van twee punten, ongeacht welke bif:-prefix-declaratie is
  geprobeerd). Gebruik in plaats daarvan de standaard GeoSPARQL-functie
  geof:sfIntersects -- die werkt wel, en accepteert een gewone
  geosparql:wktLiteral-string aan de andere kant van de vergelijking (dus de
  RCE-WKT hoeft niet naar virtrdf:Geometry geconverteerd te worden).
- geof:sfIntersects over de volle ~8.4 miljoen imxgeo:Perceel-instanties
  zonder verdere restrictie time-out (zelfde faalmodus als de reeds
  gedocumenteerde geof:sfWithin-timeout op het RCE-endpoint). Een
  niet-ruimtelijke voorfilter is dus verplicht om de kandidatenset klein
  genoeg te maken: imxgeo:ligtInRegistratieveRuimte naar een specifiek
  imxgeo:Gemeentegebied (afgeleid uit RCE's eigen
  ceo:heeftBasisregistratieRelatie/heeftGemeente-link) bracht een
  praktijktest terug tot een candidate set waarop geof:sfIntersects wel
  binnen enkele seconden klaar is.
- Praktijkvoorbeeld (Rijksmonument 73336, "Deelen/Vliegveld",
  rijksmonumentnummer 529782, gemeente Arnhem): 33 percelen intersecten de
  monumentpolygoon, totale kadastrale oppervlakte 6.801.806 m², tegenover
  8.674.092 m² voor de monumentpolygoon zelf (geof:area, zie area.py) --
  een verhouding van ~78%. Dat is een plausibele uitkomst (percelen zonder
  geosparql:hasGeometry/hasMetricArea vallen buiten deze query, en een
  monument kan net over de gemeentegrens heen liggen zonder dat RCE's eigen
  heeftGemeente-link dat toont -- zie BEPERKINGEN hieronder), geen foutieve.
  Dit is precies het soort plausibiliteitscontrole die je bij elk resultaat
  van deze tool zou moeten toepassen: vergelijk aantal_percelen en
  totale_kadastrale_oppervlakte_m2 met monument_oppervlakte_m2 (indien
  beschikbaar) of anders met wat qua omvang van het monument aannemelijk is.

## Beperkingen

- Als een monument fysiek over een gemeentegrens heen ligt, maar RCE's eigen
  ceo:heeftGemeente-link maar één gemeente teruggeeft, mist deze tool de
  percelen in de niet-vermelde gemeente (de kandidatenset wordt alleen
  binnen de vermelde gemeente(n) gezocht). Een totale kadastrale oppervlakte
  die duidelijk lager uitvalt dan de monumentoppervlakte kan hierop wijzen.
- Werkt alleen als RCE minstens een POINT-geometrie heeft (de meeste
  monumenten); een POLYGON/MULTIPOLYGON geeft een volledige perceel-dekking,
  een POINT geeft alleen het ene perceel waar dat punt in valt (net als
  RCE's eigen "punt-in-perceel"-aantekening, maar nu via een echte
  spatial-operatie i.p.v. een niet-verifieerbare aantekening).
- Percelen zonder geosparql:hasGeometry of geosparql:hasMetricArea in de KKG
  worden niet meegeteld (vereiste triple patterns in de query hieronder).
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request

from rce_cho_mcp.config import KKG_SPARQL_ENDPOINT, USER_AGENT
from rce_cho_mcp.sparql import execute_sparql

_KKG_TIMEOUT = 60
_RCE_TIMEOUT = 30
_MAX_CANDIDATE_ROWS = 500  # veiligheidslimiet op de KKG-kant, niet de weergavelimiet

_KIND_RE = re.compile(r"^\s*(multipolygon|polygon|point)", re.IGNORECASE)
_GEMEENTE_SUFFIX_RE = re.compile(r"[_ ]?\(gemeente\)$", re.IGNORECASE)


def _rows(data: dict) -> list[dict]:
    return data.get("results", {}).get("bindings", [])


def _post_kkg_sparql(query: str, timeout: int = _KKG_TIMEOUT) -> dict:
    data = urllib.parse.urlencode({"query": query}).encode("utf-8")
    request = urllib.request.Request(
        KKG_SPARQL_ENDPOINT,
        data=data,
        headers={
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _escape_sparql_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _resolve_rijksmonument_uri(identifier: str) -> str | None:
    """Accepteert zowel een volledige rijksmonument-URI als een kaal
    rijksmonumentnummer (xsd:string in de brondata, zie identifiers-topic)."""
    identifier = str(identifier).strip()
    if identifier.startswith("http"):
        return identifier

    nummer = _escape_sparql_string(identifier)
    query = f"""
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
SELECT ?rm WHERE {{
  GRAPH <https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce> {{
    ?rm a ceo:Rijksmonument ; ceo:rijksmonumentnummer "{nummer}" .
  }}
}}
LIMIT 1
"""
    rows = _rows(execute_sparql(query, timeout=_RCE_TIMEOUT))
    return rows[0]["rm"]["value"] if rows else None


def _fetch_geometry_and_gemeentes(rm_uri: str) -> dict:
    query = f"""
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
SELECT DISTINCT ?wkt WHERE {{
  <{rm_uri}> ceo:heeftGeometrie/geo:asWKT ?wkt .
}}
"""
    wkt_rows = _rows(execute_sparql(query, timeout=_RCE_TIMEOUT))

    gemeente_query = f"""
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
SELECT DISTINCT ?gemeenteUri WHERE {{
  <{rm_uri}> ceo:heeftBasisregistratieRelatie ?br .
  ?br ceo:heeftGemeente ?gemeenteUri .
}}
"""
    gemeente_rows = _rows(execute_sparql(gemeente_query, timeout=_RCE_TIMEOUT))

    return {
        "wkts": [r["wkt"]["value"] for r in wkt_rows],
        "gemeente_uris": [r["gemeenteUri"]["value"] for r in gemeente_rows],
    }


def _classify_wkt(wkt: str) -> str:
    m = _KIND_RE.match(wkt)
    return m.group(1).upper() if m else "OTHER"


def _pick_best_geometry(wkts: list[str]) -> tuple[str, str] | None:
    """Kiest bij voorkeur MULTIPOLYGON/POLYGON (volledige dekking) boven
    POINT (alleen het ene perceel waar het punt in valt)."""
    by_kind: dict[str, str] = {}
    for wkt in wkts:
        kind = _classify_wkt(wkt)
        by_kind.setdefault(kind, wkt)

    for kind in ("MULTIPOLYGON", "POLYGON", "POINT"):
        if kind in by_kind:
            return by_kind[kind], kind
    return None


def _gemeente_naam_from_owms(owms_uri: str) -> str | None:
    if not owms_uri:
        return None
    segment = owms_uri.rsplit("/", 1)[-1]
    segment = urllib.parse.unquote(segment)
    segment = _GEMEENTE_SUFFIX_RE.sub("", segment)
    return segment.replace("_", " ").strip() or None


def _monument_area_m2(wkt: str, kind: str) -> float | None:
    if kind not in ("POLYGON", "MULTIPOLYGON"):
        return None
    safe_wkt = _escape_sparql_string(wkt)
    query = f"""
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX uom: <http://www.opengis.net/def/uom/OGC/1.0/>
SELECT (geof:area("{safe_wkt}"^^geo:wktLiteral, uom:metre) AS ?a) WHERE {{}}
"""
    rows = _rows(execute_sparql(query, timeout=_RCE_TIMEOUT))
    return float(rows[0]["a"]["value"]) if rows else None


def _build_kkg_query(gemeente_namen: list[str], wkt: str) -> str:
    safe_wkt = _escape_sparql_string(wkt)
    gemeente_values = " ".join(
        f'"{_escape_sparql_string(naam)}"' for naam in gemeente_namen
    )
    return f"""
PREFIX geosparql: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
PREFIX imxgeo: <http://modellen.geostandaarden.nl/def/imx-geo#>
SELECT DISTINCT ?per ?area WHERE {{
  VALUES ?gemeenteNaam {{ {gemeente_values} }}
  ?gem a imxgeo:Gemeentegebied ; imxgeo:naam ?gemeenteNaam .
  ?per imxgeo:ligtInRegistratieveRuimte ?gem ;
    geosparql:hasGeometry ?geom ;
    geosparql:hasMetricArea ?area .
  ?geom geosparql:asWKT ?perwkt .
  FILTER(geof:sfIntersects(?perwkt, "{safe_wkt}"^^geosparql:wktLiteral))
}}
LIMIT {_MAX_CANDIDATE_ROWS}
"""


def percelen_via_spatial_join(rijksmonument: str, limit: int = 20) -> dict:
    """Voert de volledige spatial join uit voor één rijksmonument.

    rijksmonument: een rijksmonumentnummer (bv. "529782") of volledige URI.
    limit: hoeveel percelen (gesorteerd op oppervlakte, aflopend) in
    "percelen_top" getoond worden. aantal_percelen/totale oppervlakte gelden
    voor de volledige set (tot _MAX_CANDIDATE_ROWS), niet alleen de top.
    """
    rm_uri = _resolve_rijksmonument_uri(rijksmonument)
    if rm_uri is None:
        return {"error": f"Kon geen rijksmonument vinden voor '{rijksmonument}'."}

    try:
        geo_info = _fetch_geometry_and_gemeentes(rm_uri)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        return {"error": f"Fout bij bevragen RCE-endpoint: {type(e).__name__}: {e}"}

    if not geo_info["wkts"]:
        return {"error": f"Geen geometrie (ceo:heeftGeometrie) gevonden voor {rm_uri}."}

    picked = _pick_best_geometry(geo_info["wkts"])
    if picked is None:
        return {"error": f"Kon geometrietype niet bepalen voor {rm_uri}."}
    wkt, kind = picked

    gemeente_namen = [
        naam
        for naam in (
            _gemeente_naam_from_owms(uri) for uri in geo_info["gemeente_uris"]
        )
        if naam
    ]
    if not gemeente_namen:
        return {
            "error": (
                f"Geen gemeente gevonden voor {rm_uri} via "
                "ceo:heeftBasisregistratieRelatie/heeftGemeente -- nodig om de "
                "KKG-perceelscan te beperken tot een haalbare kandidatenset "
                "(een ongefilterde scan over alle ~8,4 miljoen percelen time-out)."
            ),
        }

    kkg_query = _build_kkg_query(gemeente_namen, wkt)
    try:
        kkg_data = _post_kkg_sparql(kkg_query)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"KKG-endpoint HTTP {e.code}: {body[:300]}"}
    except (urllib.error.URLError, TimeoutError) as e:
        return {"error": f"KKG-endpoint niet bereikbaar: {type(e).__name__}: {e}"}

    percelen = sorted(
        (
            {"perceel": r["per"]["value"], "oppervlakte_m2": float(r["area"]["value"])}
            for r in _rows(kkg_data)
        ),
        key=lambda p: p["oppervlakte_m2"],
        reverse=True,
    )

    monument_m2 = _monument_area_m2(wkt, kind)
    totaal_m2 = sum(p["oppervlakte_m2"] for p in percelen)

    return {
        "rijksmonument_uri": rm_uri,
        "geometrie_type_gebruikt": kind,
        "gemeente(s)": gemeente_namen,
        "aantal_percelen": len(percelen),
        "totale_kadastrale_oppervlakte_m2": totaal_m2,
        "monument_oppervlakte_m2": monument_m2,
        "percelen_top": percelen[:limit],
        "kandidatenlimiet_bereikt": len(percelen) >= _MAX_CANDIDATE_ROWS,
    }


def format_percelen_via_spatial_join(result: dict) -> str:
    if "error" in result:
        return result["error"]

    lines = [
        f"Rijksmonument: {result['rijksmonument_uri']}",
        f"Geometrie gebruikt voor de join: {result['geometrie_type_gebruikt']} "
        + (
            "(volledige dekking)"
            if result["geometrie_type_gebruikt"] in ("POLYGON", "MULTIPOLYGON")
            else "(alleen het ene perceel waar dit punt in valt, geen volledige dekking)"
        ),
        f"Gemeente(n) doorzocht: {', '.join(result['gemeente(s)'])}",
        f"Aantal overlappende percelen (spatial join, geof:sfIntersects): {result['aantal_percelen']}",
        f"Totale kadastrale oppervlakte: {result['totale_kadastrale_oppervlakte_m2']:,.0f} m2",
    ]

    if result["monument_oppervlakte_m2"] is not None:
        verhouding = (
            result["totale_kadastrale_oppervlakte_m2"] / result["monument_oppervlakte_m2"]
            if result["monument_oppervlakte_m2"]
            else None
        )
        lines.append(
            f"Monumentoppervlakte (geof:area op de RCE-polygoon): "
            f"{result['monument_oppervlakte_m2']:,.0f} m2"
        )
        if verhouding is not None:
            lines.append(
                f"Verhouding kadastraal/monument: {verhouding:.0%} -- "
                "gebruik dit als plausibiliteitscontrole (ver onder 100% kan "
                "wijzen op een monument dat over een gemeentegrens heen ligt "
                "die niet in RCE's eigen heeftGemeente-link staat, of op "
                "percelen zonder hasGeometry/hasMetricArea in de KKG; ver "
                "boven 100% kan wijzen op grofmazige percelen die breed om "
                "het monument heen liggen)."
            )
    else:
        lines.append(
            "Geen monumentoppervlakte beschikbaar als referentie (alleen een "
            "puntgeometrie, geen polygoon) -- beoordeel de plausibiliteit dan "
            "op basis van wat je qua omvang/type van dit monument verwacht."
        )

    if result["kandidatenlimiet_bereikt"]:
        lines.append(
            f"LET OP: kandidatenlimiet ({_MAX_CANDIDATE_ROWS}) bereikt -- er "
            "zijn mogelijk meer overlappende percelen dan hier getoond."
        )

    lines.append("")
    lines.append(f"Top {len(result['percelen_top'])} percelen (op oppervlakte):")
    lines.append("perceel | oppervlakte (m2)")
    lines.append("-" * 60)
    for p in result["percelen_top"]:
        lines.append(f"{p['perceel']} | {p['oppervlakte_m2']:,.0f}")

    return "\n".join(lines)
