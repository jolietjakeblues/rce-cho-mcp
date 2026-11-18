"""Automatische endpoint-routering voor query_sparql().

## Waarom deze module bestaat

De RCE-data staat op meerdere SPARQL-endpoints (CHO, Afbeeldingen,
Bibliotheek, MASS), elk met eigen named graphs. Een GRAPH-clause met een
graph van een ander endpoint geeft op het CHO-endpoint GEEN fout maar stil 0
resultaten (ASK: false) -- live bevestigd 2026-11-18.

Daarvoor bestaan aparte tools (query_sparql_afbeeldingen e.d.), maar die
zijn niet in elke chat beschikbaar: een MCP-client legt de toollijst van een
connector vast en ziet later toegevoegde tools soms niet (gezien op
2026-11-18: de server bood 31 tools aan, de client kende er 28). Het model
viel dan terug op query_sparql(), kreeg stil niets terug, en probeerde
vergeefs SERVICE-federatie.

Oplossing: query_sparql() kijkt zelf naar de graph-IRI's in de query. Hoort
een graph aantoonbaar bij een ander endpoint, dan gaat de query daarheen.
Een query op de juiste graph werkt daardoor altijd, via welke tool hij ook
binnenkomt.
"""

from __future__ import annotations

import re

from rce_cho_mcp.config import (
    AFBEELDINGEN_SPARQL_ENDPOINT,
    BIBLIOTHEEK_SPARQL_ENDPOINT,
    MASS_SPARQL_ENDPOINT,
)
from rce_cho_mcp.sparql import execute_sparql, post_sparql

_LD = "https://linkeddata.cultureelerfgoed.nl"
_CHT = "https://data.cultureelerfgoed.nl/term/id/cht/thesaurus"
_ABR = "https://data.cultureelerfgoed.nl/term/id/abr/thesaurus"

# Per dataset buiten CHO, live geverifieerd 2026-11-18 (SELECT ?g ... GROUP BY
# ?g op elk endpoint):
#   prefixes: een graph-IRI die hiermee begint bestaat ALLEEN op dit endpoint
#   exact:    idem, maar als volledige IRI (geen prefixmatch, om botsingen
#             met gelijkend genaamde CHO-graphs te vermijden)
#   shared:   graphs die op dit endpoint EN op het CHO-endpoint bestaan; zij
#             bepalen de route niet, maar mogen wel in dezelfde query staan
OTHER_DATASETS: dict[str, dict] = {
    "afbeeldingen": {
        "label": "RCE Afbeeldingen",
        "endpoint": AFBEELDINGEN_SPARQL_ENDPOINT,
        "tool": "query_sparql_afbeeldingen",
        "prefixes": (f"{_LD}/rce/afbeeldingen/",),
        "exact": (),
        "shared": (f"{_LD}/graph/image", f"{_LD}/graph/print"),
    },
    "bibliotheek": {
        "label": "RCE Bibliotheek",
        "endpoint": BIBLIOTHEEK_SPARQL_ENDPOINT,
        "tool": "query_sparql_bibliotheek",
        "prefixes": (f"{_LD}/rce/bibliotheek/", f"{_LD}/graph/bib-"),
        "exact": (f"{_LD}/graph/bib",),
        "shared": (_CHT, _ABR),
    },
    "mass": {
        "label": "RCE MASS",
        "endpoint": MASS_SPARQL_ENDPOINT,
        "tool": "query_sparql_mass",
        "prefixes": (
            f"{_LD}/joop-van-der-heiden/mass/",
            f"{_LD}/rce/mass/",
            "https://mass.cultureelerfgoed.nl/graph/",
        ),
        "exact": (),
        "shared": (),
    },
}

# GRAPH <iri>, FROM <iri> en FROM NAMED <iri>. Een variabele (GRAPH ?g) of
# een geprefixte naam matcht bewust niet: daar valt niets uit af te leiden.
_GRAPH_IRI_RE = re.compile(r"\b(?:GRAPH|FROM(?:\s+NAMED)?)\s*<([^<>\s]+)>", re.IGNORECASE)


# SERVICE <...> naar een RCE-linked-data-host (api.linkeddata... of de
# frontend-host). SERVICE naar een externe bron (bv. Wikidata) blijft toegestaan.
_SERVICE_RCE_RE = re.compile(
    r"\bSERVICE\s+(?:SILENT\s+)?<https?://(?:api\.)?linkeddata\.cultureelerfgoed\.nl/",
    re.IGNORECASE,
)


class MixedEndpointsError(ValueError):
    """De query combineert graphs die op verschillende endpoints staan."""


def graph_iris(query: str) -> list[str]:
    """Alle graph-IRI's uit GRAPH/FROM/FROM NAMED, in volgorde, ontdubbeld."""
    seen: list[str] = []
    for iri in _GRAPH_IRI_RE.findall(query):
        if iri not in seen:
            seen.append(iri)
    return seen


def _owner(iri: str) -> str | None:
    for key, dataset in OTHER_DATASETS.items():
        if iri in dataset["exact"] or any(iri.startswith(p) for p in dataset["prefixes"]):
            return key
    return None


def resolve_dataset(query: str) -> str:
    """Bepaal op welk endpoint een query thuishoort: "cho" (standaard) of een
    sleutel uit OTHER_DATASETS.

    Raises MixedEndpointsError als de query graphs van verschillende
    endpoints combineert -- dat kan in één query niet werken.
    """
    if _SERVICE_RCE_RE.search(query):
        raise MixedEndpointsError(
            "Deze query gebruikt SERVICE-federatie naar een ander RCE-endpoint. "
            "Dat werkt niet tussen deze endpoints (live getest: HTTP 500 of stil "
            "0 resultaten). Splits de query in twee stappen: haal eerst op het "
            "CHO-endpoint de URI's of nummers op, en gebruik die daarna in een "
            "VALUES-lijst in een aparte query met de GRAPH-clause van de andere "
            "dataset (photos, books of article) -- query_sparql() voert die "
            "automatisch op het juiste endpoint uit."
        )
    iris = graph_iris(query)
    owners = {iri: _owner(iri) for iri in iris}
    datasets = sorted({owner for owner in owners.values() if owner})

    if not datasets:
        return "cho"

    if len(datasets) > 1:
        labels = ", ".join(OTHER_DATASETS[d]["label"] for d in datasets)
        raise MixedEndpointsError(
            f"Deze query combineert graphs van verschillende endpoints ({labels}). "
            "Eén SPARQL-query kan maar op één endpoint draaien. Splits de query: "
            "één query per dataset, en combineer de resultaten daarna zelf "
            "(bv. via een VALUES-lijst met de gevonden URI's of nummers)."
        )

    key = datasets[0]
    dataset = OTHER_DATASETS[key]
    alleen_cho = [
        iri for iri, owner in owners.items() if owner is None and iri not in dataset["shared"]
    ]
    if alleen_cho:
        raise MixedEndpointsError(
            f"Deze query combineert een graph van {dataset['label']} met graph(s) "
            f"die daar niet bestaan: {', '.join(alleen_cho)}. Eén SPARQL-query kan "
            "maar op één endpoint draaien, en SERVICE-federatie tussen deze "
            "endpoints werkt niet. Splits de query in twee stappen: haal eerst "
            "op het CHO-endpoint de URI's of nummers op, en gebruik die daarna "
            f"in een VALUES-lijst in een aparte query op {dataset['label']}."
        )
    return key


def routing_note(dataset_key: str) -> str:
    """Eén regel die in het resultaat meldt dat de query is omgeleid."""
    dataset = OTHER_DATASETS[dataset_key]
    return (
        f"Let op: uitgevoerd op het {dataset['label']}-endpoint, niet op het "
        "CHO-endpoint, omdat de graph in de query bij die dataset hoort "
        f"(zelfde als {dataset['tool']}())."
    )


def execute_routed(query: str, timeout: int = 30) -> tuple[dict, str]:
    """Voer een query uit op het endpoint waar zijn graphs thuishoren.

    Retourneert (SPARQL-JSON, dataset-sleutel). Voor "cho" is dit exact
    execute_sparql(), inclusief de Speedy/Virtuoso-fallback.
    """
    key = resolve_dataset(query)
    if key == "cho":
        return execute_sparql(query, timeout=timeout), key
    return post_sparql(OTHER_DATASETS[key]["endpoint"], query, timeout=timeout), key
