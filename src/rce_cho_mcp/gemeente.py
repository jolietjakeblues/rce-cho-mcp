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

4. RCE's gemeentekoppeling is bij gemeentelijke herindelingen niet volledig
   omgezet naar de nieuwe gemeente (zie het commentaarblok "Gemeentelijke
   herindelingen" verderop): een vraag naar de huidige gemeente moet daarom
   ook de opgeheven voorgangers meenemen.

monumenten_in_gemeente() combineert deze stappen in één aanroep, met
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

# ceo:heeftJuridischeStatus en ceo:heeftMonumentAard hebben in de ontologie
# rdfs:domain ceo:Rijksmonument -- geen enkele andere class (ArcheologischOnderzoeksgebied,
# ArcheologischTerrein, Complex, Gezicht, ...) heeft deze triples, bevestigd
# live (2026-11-06): 113.956 ceo:ArcheologischOnderzoeksgebied-instanties, 0
# met ceo:heeftJuridischeStatus. Filteren op status/aard bij een andere
# class_name geeft daarom altijd stil 0 resultaten, zonder foutmelding --
# dezelfde valkuil als elders in deze server (zie o.a. semantics.py). In
# plaats van te gokken (en bv. terug te vallen op het onbetrouwbare,
# Rijksmonument-only ceo:gemeentenaam-tekstveld of een BAG-woonplaatsnaam)
# geeft monumenten_in_gemeente() hieronder een expliciete foutmelding.
_STATUS_AARD_DOMAIN_CLASS = "Rijksmonument"

# ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente is RDFS-gezien op elke
# CultuurhistorischObject-subclass toepasbaar, maar is in de PRAKTIJK bij de
# meeste archeologische classes vrijwel nooit gevuld -- dus geen "geldt voor
# elke class"-garantie. Live geverifieerd (2026-11-06, graph instanties-rce,
# teller/totaal instanties van die class):
#   Rijksmonument:                  67.494 / 67.496   (~100%)
#   ArcheologischOnderzoeksgebied: 103.929 / 113.956   (~91%)
#   Vondstlocatie:                 102.226 / 112.009   (~91%)
#   ArcheologischComplex:                1 / 360.471   (~0%)
#   ArcheologischTerrein:                1 /  13.025   (~0%)
#   Grondsporen:                         1 /  93.007   (~0%)
#   Vondsten:                            1 / 447.488   (~0%)
#   Complex:                             0 /   2.834   (0%)
#   Gezicht:                             0 /     472   (0%)
# Voor de vier ~0%-archeologieclasses hierboven is er wel een bruikbaar
# (niet uitputtend) alternatief: één stap omhoog via ceo:ligtInObject naar
# de bovenliggende ArcheologischOnderzoeksgebied/Vondstlocatie/Rijksmonument,
# die meestal zelf wel heeftGemeente heeft. Ook live geverifieerd:
#   ArcheologischComplex via ligtInObject: 310.178 / 360.471   (~86%)
#   Grondsporen via ligtInObject:           86.933 /  93.007   (~93%)
#   Vondsten via ligtInObject:              414.289 / 447.488   (~93%)
#   ArcheologischTerrein via ligtInObject:    1.811 /  13.025   (~14%,
#     NIET bruikbaar -- de meeste terreinen hebben domweg geen
#     ceo:ligtInObject-parent geregistreerd, direct noch indirect)
# monumenten_in_gemeente() zet hierop geen harde blokkade (dit is geen
# ontologie-garantie zoals _STATUS_AARD_DOMAIN_CLASS hierboven, maar een
# datafeit dat kan verschuiven), maar geeft wel een waarschuwing mee.
_GEMEENTE_LINK_SPARSE_NOTES: dict[str, str] = {
    "ArcheologischComplex": (
        "ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente is voor "
        "ArcheologischComplex vrijwel altijd leeg (1 van 360.471 instanties, "
        "2026-11-06) -- dit resultaat is daardoor vrijwel zeker (bijna) leeg. "
        "Betrouwbaarder alternatief: filter op de bovenliggende "
        "ArcheologischOnderzoeksgebied/Vondstlocatie via ceo:ligtInObject "
        "(dekt ~86%, 310.178 van 360.471), of navigeer vanuit "
        "monumenten_in_gemeente(class_name='ArcheologischOnderzoeksgebied', "
        "juridische_status='alle') naar ceo:bevatObject."
    ),
    "ArcheologischTerrein": (
        "ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente is voor "
        "ArcheologischTerrein vrijwel altijd leeg (1 van 13.025 instanties, "
        "2026-11-06) -- dit resultaat is daardoor vrijwel zeker (bijna) leeg. "
        "Er is hiervoor ook GEEN bruikbaar ceo:ligtInObject-alternatief: "
        "slechts 14% (1.811 van 13.025) heeft uberhaupt een containment-"
        "parent. Overweeg een geometrische aanpak (ceo:heeftGeometrie + "
        "spatial join) in plaats van een gemeentefilter voor deze class."
    ),
    "Grondsporen": (
        "ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente is voor "
        "Grondsporen vrijwel altijd leeg (1 van 93.007 instanties, "
        "2026-11-06) -- dit resultaat is daardoor vrijwel zeker (bijna) "
        "leeg. Betrouwbaarder alternatief: filter via ceo:ligtInObject op "
        "de bovenliggende Vondstlocatie (dekt ~93%, 86.933 van 93.007)."
    ),
    "Vondsten": (
        "ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente is voor "
        "Vondsten vrijwel altijd leeg (1 van 447.488 instanties, "
        "2026-11-06) -- dit resultaat is daardoor vrijwel zeker (bijna) "
        "leeg. Betrouwbaarder alternatief: filter via ceo:ligtInObject op "
        "de bovenliggende Vondstlocatie (dekt ~93%, 414.289 van 447.488)."
    ),
    "Complex": (
        "ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente is voor Complex "
        "nooit gevuld (0 van 2.834 instanties, 2026-11-06) -- dit resultaat "
        "is daardoor altijd leeg."
    ),
    "Gezicht": (
        "ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente is voor Gezicht "
        "nooit gevuld (0 van 472 instanties, 2026-11-06) -- dit resultaat "
        "is daardoor altijd leeg."
    ),
}

# Eén bron: semantics_describe_topic('legal_status')/('monument_aard') --
# zie get_known_value_uris() in semantics.py. Ook gebruikt door area.py, zodat
# deze concept-URI's niet in meerdere modules los gedupliceerd staan.
_LEGAL_STATUS_URIS = get_known_value_uris("legal_status")
_MONUMENT_AARD_URIS = get_known_value_uris("monument_aard")

# Normaliseert invoer die de gebruiker soms al in wiki/URI-stijl aanlevert
# (zie memory rce-monumentadressen-datakwaliteit), bv. "Utrecht (gemeente)".
GEMEENTE_SUFFIX_RE = re.compile(r"[_ ]?\(gemeente\)$", re.IGNORECASE)


def _clamp_limit(limit: int) -> int:
    return max(_MIN_LIMIT, min(limit, _MAX_LIMIT))


def _normalize_gemeente_naam(naam: str) -> str:
    naam = naam.strip()
    return GEMEENTE_SUFFIX_RE.sub("", naam).strip()


# ---------------------------------------------------------------------------
# Gemeentelijke herindelingen
#
# ceo:heeftGemeente wijst ALTIJD naar een OWMS-gemeenteconcept (live
# geverifieerd 2026-11-17: 273.835 triples, 402 verschillende gemeenten,
# allemaal in de namespace http://standaarden.overheid.nl/owms/terms/ -- de
# TOOI-graph wordt nergens als doel van heeftGemeente gebruikt). Die koppeling
# is bij herindelingen NIET volledig en niet altijd naar de juiste gemeente
# omgezet: 61 van die 402 gemeenten zijn inmiddels opgeheven (owms:endDate
# gevuld), samen goed voor 5.091 BasisregistratieRelaties, verdeeld over
# 1.065 Rijksmonument-objecten (58 opgeheven gemeenten), 1.793
# ArcheologischOnderzoeksgebieden en 2.233 Vondstlocaties. Live geverifieerd
# (2026-11-17), drie verschillende situaties:
#   1. ACTIEVE rijksmonumenten (status "rijksmonument") zijn overal omgezet
#      naar de huidige gemeente, met precies EEN uitzondering: Voorne aan Zee
#      (sinds 2023-01-01) heeft zelf 0 objecten; alle 448 actieve
#      rijksmonumenten van dat grondgebied staan op voorganger "Westvoorne"
#      -- ook de ruim 350 met BAG-woonplaats Brielle en de 33 in
#      Hellevoetsluis. Dat zijn alle 448 actieve rijksmonumenten die
#      landelijk nog op een opgeheven gemeente staan.
#   2. AFGEVOERDE objecten (status "geen rijksmonument") zijn NIET omgezet:
#      617 stuks, verspreid over 58 opgeheven gemeenten (bv. Weesp 69,
#      Boxmeer 41, Cuijk 13, en rijksmonumentnummer 10832 op Brielle).
#   3. ARCHEOLOGIE (onderzoeksgebieden, vondstlocaties) is niet omgezet voor
#      de herindelingen van 2021-01-01 t/m 2023-01-01: alle 4.026 objecten
#      staan op gemeenten met einddatum 2020-12-31 t/m 2022-12-31.
# Een vraag naar "monumenten in Voorne aan Zee" gaf daardoor stil 0, en een
# vraag met juridische_status="alle"/"geen rijksmonument" of een
# archeologische class mist zonder voorgangers een deel. De OWMS-graph zelf
# bevat de benodigde relaties (owms:predecessor / owms:successor, 270 elk,
# plus owms:endDate / owms:startDate), dus dit is zonder externe bron op te
# lossen: tel de gevraagde gemeente plus haar opgeheven voorgangers samen.
#
# Beperking: een voorganger die over MEERDERE opvolgers is verdeeld (bv.
# Haaren, 2020-12-31 -> Boxtel, Oisterwijk, Tilburg en Vught) is niet
# eenduidig aan één opvolger toe te wijzen. Die wordt daarom NIET automatisch
# meegeteld, maar wel apart gemeld (zie _select_voorgangers).
#
# Actualiteit: de laatste herindeling in zowel de OWMS-graph als de
# TOOI-graph (register "gemeenten compleet", zichtdatum 2026-01-29) is die
# van 2023-01-01 (Voorne aan Zee). Latere herindelingen staan er niet in en
# worden hier dus ook niet herkend.
# ---------------------------------------------------------------------------
_OWMS_NS = "http://standaarden.overheid.nl/owms/terms/"


def _select_voorgangers(start_uri: str, edges: list[dict]) -> tuple[list[dict], list[dict]]:
    """Bepaal welke voorgangers van start_uri veilig meegeteld kunnen worden.

    edges: rijen {"kind", "voorganger", "naam", "einddatum", "aantal_opvolgers"}
    -- elke rij is één owms:predecessor-relatie ergens in de (transitieve)
    voorgangersboom van start_uri.

    Retourneert (meetellen, gesplitst). Een voorganger met precies één
    opvolger is volledig in die opvolger opgegaan en telt mee (en zijn eigen
    voorgangers ook, recursief). Een voorganger met meerdere opvolgers is
    verdeeld en komt in "gesplitst" -- daar wordt niet verder doorheen
    gelopen, want ook alles daaronder is niet eenduidig toe te wijzen.
    """
    by_kind: dict[str, list[dict]] = {}
    for edge in edges:
        by_kind.setdefault(edge["kind"], []).append(edge)

    meetellen: list[dict] = []
    gesplitst: list[dict] = []
    seen = {start_uri}
    queue = [start_uri]
    while queue:
        current = queue.pop(0)
        for edge in by_kind.get(current, []):
            uri = edge["voorganger"]
            if uri in seen:
                continue
            seen.add(uri)
            if edge["aantal_opvolgers"] == 1:
                meetellen.append(edge)
                queue.append(uri)
            else:
                gesplitst.append(edge)
    return meetellen, gesplitst


def gemeente_herindeling(gemeente_uri: str) -> dict:
    """Haal de herindelingsgeschiedenis van een OWMS-gemeente op.

    Retourneert {"einddatum" (None als de gemeente nog bestaat),
    "opvolgers": [{"uri", "naam"}] (directe opvolgers),
    "voorgangers": [...] (volledig opgegane voorgangers, transitief --
    veilig om mee te tellen), "gesplitste_voorgangers": [...] (verdeeld over
    meerdere gemeenten -- niet eenduidig toe te wijzen)}.
    """
    status_query = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owms: <{_OWMS_NS}>
SELECT DISTINCT ?eind ?opv ?opvNaam WHERE {{
  GRAPH <{_OWMS_GRAPH}> {{
    {{ <{gemeente_uri}> owms:endDate ?eind }}
    UNION
    {{ <{gemeente_uri}> owms:successor ?opv . OPTIONAL {{ ?opv skos:prefLabel ?opvNaam }} }}
  }}
}}
"""
    einddatum = None
    opvolgers: dict[str, dict] = {}
    for row in _sparql_rows(execute_sparql(status_query, timeout=_QUERY_TIMEOUT)):
        if "eind" in row:
            einddatum = row["eind"]["value"]
        if "opv" in row:
            uri = row["opv"]["value"]
            opvolgers[uri] = {"uri": uri, "naam": row.get("opvNaam", {}).get("value", uri)}

    voorganger_query = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owms: <{_OWMS_NS}>
SELECT ?kind ?voorg ?naam ?eind (COUNT(DISTINCT ?opv) AS ?nOpv) WHERE {{
  GRAPH <{_OWMS_GRAPH}> {{
    <{gemeente_uri}> owms:predecessor* ?kind .
    ?kind owms:predecessor ?voorg .
    ?voorg owms:successor ?opv .
    OPTIONAL {{ ?voorg skos:prefLabel ?naam }}
    OPTIONAL {{ ?voorg owms:endDate ?eind }}
  }}
}}
GROUP BY ?kind ?voorg ?naam ?eind
"""
    edges = [
        {
            "kind": row["kind"]["value"],
            "voorganger": row["voorg"]["value"],
            "naam": row.get("naam", {}).get("value", row["voorg"]["value"]),
            "einddatum": row.get("eind", {}).get("value"),
            "aantal_opvolgers": int(row["nOpv"]["value"]),
        }
        for row in _sparql_rows(execute_sparql(voorganger_query, timeout=_QUERY_TIMEOUT))
    ]
    meetellen, gesplitst = _select_voorgangers(gemeente_uri, edges)

    def _public(edge: dict) -> dict:
        return {
            "uri": edge["voorganger"],
            "naam": edge["naam"],
            "einddatum": edge["einddatum"],
            "aantal_opvolgers": edge["aantal_opvolgers"],
        }

    return {
        "einddatum": einddatum,
        "opvolgers": sorted(opvolgers.values(), key=lambda o: o["naam"]),
        "voorgangers": sorted((_public(e) for e in meetellen), key=lambda o: o["naam"]),
        "gesplitste_voorgangers": sorted(
            (_public(e) for e in gesplitst), key=lambda o: o["naam"]
        ),
    }


def huidige_gemeentenamen(gemeente_uri: str) -> list[str]:
    """Geef de naam/namen van de nu bestaande gemeente(n) waarin een (mogelijk
    opgeheven) OWMS-gemeente is opgegaan -- transitief via owms:successor.

    Leeg resultaat betekent: de gemeente heeft geen opvolger en bestaat dus
    nog gewoon onder zijn eigen naam. Gebruikt door brk_spatial.py: het
    Kadaster KKG-endpoint kent alleen de huidige gemeentegebieden (live
    geverifieerd 2026-11-17: imxgeo:naam "Voorne aan Zee" en "Dijk en Waard"
    bestaan, "Brielle", "Weesp" en "Heerhugowaard" niet), terwijl RCE's
    heeftGemeente nog naar de opgeheven gemeente kan wijzen.
    """
    query = f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owms: <{_OWMS_NS}>
SELECT DISTINCT ?naam WHERE {{
  GRAPH <{_OWMS_GRAPH}> {{
    <{gemeente_uri}> owms:successor+ ?opv .
    ?opv skos:prefLabel ?naam .
    FILTER NOT EXISTS {{ ?opv owms:endDate ?eind }}
  }}
  FILTER(LANG(?naam) = "nl")
}}
"""
    return sorted(
        row["naam"]["value"]
        for row in _sparql_rows(execute_sparql(query, timeout=_QUERY_TIMEOUT))
    )


def format_herindeling(naam: str, herindeling: dict) -> list[str]:
    """Leesbare regels over de herindelingsstatus van een gemeente (leeg als
    er niets te melden is). Gebruikt door de resolve_gemeente-tool."""
    lines: list[str] = []
    if herindeling["einddatum"]:
        opvolgers = ", ".join(o["naam"] for o in herindeling["opvolgers"]) or "onbekend"
        lines.append(
            f"LET OP: gemeente {naam} is opgeheven per {herindeling['einddatum']} "
            f"(opgegaan in: {opvolgers}). De RCE-data is bij herindelingen niet "
            "volledig omgezet: er kunnen nog objecten aan deze oude gemeente "
            "gekoppeld zijn (vooral afgevoerde objecten en archeologie), maar "
            "actieve rijksmonumenten staan doorgaans op de opvolger of op een "
            "andere voorganger daarvan. Vraag voor het hele huidige "
            f"grondgebied {opvolgers} op met monumenten_in_gemeente()."
        )
    if herindeling["voorgangers"]:
        namen = ", ".join(
            f"{v['naam']} (tot {v['einddatum'] or '?'}): {v['uri']}"
            for v in herindeling["voorgangers"]
        )
        lines.append(
            f"Voorgangers, volledig opgegaan in {naam} -- neem deze URI's mee in "
            f"een handgeschreven gemeentefilter (VALUES): {namen}"
        )
    if herindeling["gesplitste_voorgangers"]:
        namen = ", ".join(
            f"{v['naam']} (tot {v['einddatum'] or '?'}, verdeeld over "
            f"{v['aantal_opvolgers']} gemeenten): {v['uri']}"
            for v in herindeling["gesplitste_voorgangers"]
        )
        lines.append(
            f"Gesplitste voorgangers, NIET eenduidig aan {naam} toe te wijzen: {namen}"
        )
    return lines


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
    inclusief_voorgangers: bool = True,
) -> dict:
    """Tel en toon objecten in een gemeente, met automatische
    gemeente-resolutie, de juiste graph en (voor class_name="Rijksmonument")
    een juridische-statusfilter. De gemeentekoppeling via
    ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente is RDFS-gezien op
    elke class toepasbaar, maar is in de PRAKTIJK alleen betrouwbaar gevuld
    bij Rijksmonument (~100%), ArcheologischOnderzoeksgebied (~91%) en
    Vondstlocatie (~91%) -- geverifieerd 2026-11-06. Bij ArcheologischComplex,
    ArcheologischTerrein, Grondsporen, Vondsten, Complex en Gezicht is hij
    vrijwel altijd leeg (zie _GEMEENTE_LINK_SPARSE_NOTES); voor die classes
    geeft dit aanroep "aantal": 0 (of bijna 0) en een "waarschuwing"-sleutel
    met een alternatief (meestal: filter op de bovenliggende class via
    ceo:ligtInObject).

    juridische_status: "rijksmonument" (standaard), "voorbeschermd",
    "geen rijksmonument", of "alle" om niet op status te filteren. Dit
    filter (en monument_aard) bestaat in de ontologie alleen op
    ceo:Rijksmonument -- bij elke andere class_name geef je hier "alle" (of
    None) mee, anders komt er een foutmelding (in plaats van stil 0
    resultaten, de valkuil die dit filter voor niet-Rijksmonument classes
    voorheen had).

    inclusief_voorgangers: tel (standaard) ook objecten mee die nog aan een
    door herindeling opgeheven voorganger van deze gemeente gekoppeld zijn
    -- RCE's heeftGemeente is bij herindelingen niet volledig omgezet (zie het
    commentaarblok "Gemeentelijke herindelingen" in deze module).
    Voorgangers die over meerdere gemeenten verdeeld zijn tellen nooit
    automatisch mee, maar worden wel gemeld in "herindeling".

    Retourneert bij succes {"gemeente", "gemeente_uri", "class_name",
    "class_uri", "juridische_status", "monument_aard", "aantal", "rows",
    "herindeling"}
    ("aantal" geldt voor de volledige set, "rows" is de steekproef tot
    limit), plus optioneel "waarschuwing" bij een class met een vrijwel lege
    gemeentekoppeling, of {"error": ...} bij een onbekende
    gemeente/class/status/aard, of bij een status-/aardfilter op een class
    die dat niet ondersteunt.
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

    if class_name != _STATUS_AARD_DOMAIN_CLASS:
        if juridische_status is not None and juridische_status != "alle":
            return {
                "error": (
                    f"ceo:heeftJuridischeStatus bestaat alleen op ceo:{_STATUS_AARD_DOMAIN_CLASS} "
                    f"(rdfs:domain in de ontologie) -- class_name={class_name!r} heeft "
                    "deze property nooit, dus dit filter geeft altijd stil 0 "
                    "resultaten, zonder foutmelding. Geef juridische_status=\"alle\" "
                    "mee voor een class buiten Rijksmonument (bv. "
                    "ArcheologischOnderzoeksgebied, ArcheologischTerrein, Complex, "
                    "Gezicht)."
                )
            }
        if monument_aard is not None:
            return {
                "error": (
                    f"ceo:heeftMonumentAard bestaat alleen op ceo:{_STATUS_AARD_DOMAIN_CLASS} "
                    f"(rdfs:domain in de ontologie) -- class_name={class_name!r} heeft "
                    "deze property nooit, dus dit filter geeft altijd stil 0 "
                    "resultaten, zonder foutmelding. Laat monument_aard weg voor een "
                    "class buiten Rijksmonument."
                )
            }

    status_filter = ""
    if juridische_status is not None and juridische_status != "alle":
        status_uri = _LEGAL_STATUS_URIS.get(juridische_status)
        if status_uri is None:
            return {
                "error": f"Onbekende juridische_status: {juridische_status!r}",
                "beschikbare_juridische_status_waarden": sorted(_LEGAL_STATUS_URIS.keys())
                + ["alle"],
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

    herindeling = gemeente_herindeling(gem["uri"])
    meegeteld = [{"uri": gem["uri"], "naam": gem["naam"], "einddatum": herindeling["einddatum"]}]
    if inclusief_voorgangers:
        meegeteld += [
            {"uri": v["uri"], "naam": v["naam"], "einddatum": v["einddatum"]}
            for v in herindeling["voorgangers"]
        ]
    gesplitst = [
        {"uri": v["uri"], "naam": v["naam"], "einddatum": v["einddatum"]}
        for v in herindeling["gesplitste_voorgangers"]
    ]

    gemeente_values = " ".join(f"<{g['uri']}>" for g in meegeteld)
    object_pattern = f"""VALUES ?gem {{ {gemeente_values} }}
        ?obj a <{class_uri}> ;
          ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente ?gem .
        {status_filter}
        {aard_filter}"""

    count_query = f"""
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
SELECT (COUNT(DISTINCT ?obj) AS ?aantal) WHERE {{
  GRAPH <{_INSTANTIES_GRAPH}> {{
        {object_pattern}
  }}
}}
"""
    count_rows = _sparql_rows(execute_sparql(count_query, timeout=_QUERY_TIMEOUT))
    aantal = int(count_rows[0]["aantal"]["value"]) if count_rows else 0

    # Uitsplitsing per gemeente, alleen nodig als er meer dan één gemeente in
    # het spel is. De gesplitste voorgangers gaan hier wel in mee (zodat de
    # aanroeper ziet hoeveel objecten daar nog op staan), maar tellen niet
    # mee in "aantal" hierboven.
    if len(meegeteld) + len(gesplitst) > 1:
        alle_values = " ".join(f"<{g['uri']}>" for g in meegeteld + gesplitst)
        per_gemeente_query = f"""
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
SELECT ?gem (COUNT(DISTINCT ?obj) AS ?aantal) WHERE {{
  GRAPH <{_INSTANTIES_GRAPH}> {{
        VALUES ?gem {{ {alle_values} }}
        ?obj a <{class_uri}> ;
          ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente ?gem .
        {status_filter}
        {aard_filter}
  }}
}}
GROUP BY ?gem
"""
        per_gemeente = {
            row["gem"]["value"]: int(row["aantal"]["value"])
            for row in _sparql_rows(execute_sparql(per_gemeente_query, timeout=_QUERY_TIMEOUT))
        }
    else:
        per_gemeente = {gem["uri"]: aantal}
    for g in meegeteld + gesplitst:
        g["aantal"] = per_gemeente.get(g["uri"], 0)

    # build_name_lookup_query() wrapt dit met de standaard naam/nummer-
    # OPTIONALs op de al-beperkte set (zie queries.py) -- zelfde tweetraps-
    # mechanisme als largest_by_area() in area.py, nu gedeeld in plaats van
    # met de hand herschreven.
    inner_select = f"""{{
    SELECT DISTINCT ?obj WHERE {{
      GRAPH <{_INSTANTIES_GRAPH}> {{
        {object_pattern}
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

    result = {
        "gemeente": gem["naam"],
        "gemeente_uri": gem["uri"],
        "class_name": class_name,
        "class_uri": class_uri,
        "juridische_status": juridische_status,
        "monument_aard": monument_aard,
        "aantal": aantal,
        "rows": rows,
        "herindeling": {
            "einddatum": herindeling["einddatum"],
            "opvolgers": herindeling["opvolgers"],
            "gemeenten_meegeteld": meegeteld,
            "gesplitste_voorgangers": gesplitst,
            "voorgangers_niet_meegeteld": (
                [] if inclusief_voorgangers else herindeling["voorgangers"]
            ),
        },
    }
    sparse_note = _GEMEENTE_LINK_SPARSE_NOTES.get(class_name)
    if sparse_note is not None:
        result["waarschuwing"] = sparse_note
    return result


def _format_herindeling_result(result: dict) -> list[str]:
    """Regels over herindelingen voor format_monumenten_in_gemeente()."""
    her = result.get("herindeling")
    if not her:
        return []
    naam = result["gemeente"]
    lines: list[str] = []

    if her["einddatum"]:
        opvolgers = ", ".join(o["naam"] for o in her["opvolgers"]) or "onbekend"
        lines.append(
            f"LET OP (herindeling): gemeente {naam} is opgeheven per "
            f"{her['einddatum']} en opgegaan in {opvolgers}. Dit resultaat telt "
            f"alleen wat RCE nog aan de oude gemeente {naam} koppelt -- dat is "
            "meestal een restant, en kan 0 zijn terwijl er wel monumenten in "
            f"het voormalige {naam} liggen. Vraag voor het hele huidige "
            f"grondgebied {opvolgers} op."
        )

    meegeteld = her["gemeenten_meegeteld"]
    if len(meegeteld) > 1:
        delen = ", ".join(
            g["naam"]
            + (f" (opgeheven {g['einddatum']})" if g["einddatum"] else "")
            + f": {g['aantal']}"
            for g in meegeteld
        )
        lines.append(
            "Herindeling: de gemeentekoppeling in de RCE-data is bij "
            "herindelingen niet volledig (en niet altijd naar de juiste "
            "gemeente) omgezet, daarom zijn de opgeheven voorgangers "
            f"meegeteld. Onder welke gemeente de objecten nu geregistreerd staan -- {delen}. "
            "Deze uitsplitsing zegt waar RCE het object aan koppelt, niet in "
            "welke voormalige gemeente het feitelijk ligt."
        )

    if her["voorgangers_niet_meegeteld"]:
        namen = ", ".join(v["naam"] for v in her["voorgangers_niet_meegeteld"])
        lines.append(
            f"LET OP (herindeling): {naam} heeft opgeheven voorgangers ({namen}) "
            "die NIET zijn meegeteld (inclusief_voorgangers=False). Objecten "
            "die RCE nog aan die oude gemeenten koppelt ontbreken hier."
        )

    if her["gesplitste_voorgangers"]:
        delen = ", ".join(
            f"{g['naam']} (opgeheven {g['einddatum'] or '?'}): {g['aantal']}"
            for g in her["gesplitste_voorgangers"]
        )
        lines.append(
            "LET OP (herindeling): de volgende voorgangers zijn over meerdere "
            f"gemeenten verdeeld en daarom NIET meegeteld -- {delen}. Een deel "
            f"van die objecten ligt nu in {naam}; bepaal dat zo nodig per object "
            "via de geometrie (ceo:heeftGeometrie)."
        )
    return lines


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
    ]
    lines += _format_herindeling_result(result)
    if "waarschuwing" in result:
        lines.append(f"WAARSCHUWING: {result['waarschuwing']}")
    lines += [
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
