"""Verwijzingen naar de bronnen achter deze server.

Eén bron voor de `verwijzingen`-tool, de MCP-resource `rce-cho://verwijzingen`
en de README: de Linked Data Voorziening (LDV) van de RCE -- zowel de
frontend (voor mensen) als de SPARQL-endpoints (voor machines) -- en de
CEO-ontologie (CEO_RCE.ttl).

De endpoint-URL's komen uit config.py, zodat een via een omgevingsvariabele
overschreven endpoint hier ook klopt. Alle URL's hieronder zijn op
2026-11-18 op bereikbaarheid gecontroleerd.
"""

from __future__ import annotations

import re

from rce_cho_mcp.config import (
    AFBEELDINGEN_SPARQL_ENDPOINT,
    BIBLIOTHEEK_SPARQL_ENDPOINT,
    CHO_DATASET_ENDPOINT,
    CHO_SERVICE_ENDPOINT,
    MASS_SPARQL_ENDPOINT,
)
from rce_cho_mcp.ontology.loader import ONTOLOGY_FILE

LDV_FRONTEND = "https://linkeddata.cultureelerfgoed.nl/"
LDV_RCE_ACCOUNT = "https://linkeddata.cultureelerfgoed.nl/rce"

CEO_ONTOLOGY_URI = "https://linkeddata.cultureelerfgoed.nl/def/ceo"
CEO_NAMESPACE = "https://linkeddata.cultureelerfgoed.nl/def/ceo#"
CEO_GITHUB_REPO = "https://github.com/cultureelerfgoed/CEO"
CEO_TTL_URL = "https://raw.githubusercontent.com/cultureelerfgoed/CEO/master/CEO_RCE.ttl"

# Per dataset: de pagina in de LDV-frontend, het SPARQL-endpoint en de tool
# van deze server waarmee je het endpoint bevraagt.
LDV_DATASETS = [
    {
        "naam": "CHO (cultuurhistorische objecten en kennis)",
        "frontend": f"{LDV_RCE_ACCOUNT}/cho",
        "sparql_editor": f"{LDV_RCE_ACCOUNT}/cho/sparql",
        "endpoint": CHO_DATASET_ENDPOINT,
        "tool": "query_sparql",
    },
    {
        "naam": "MASS (maritiem erfgoed, scheepswrakken)",
        "frontend": f"{LDV_RCE_ACCOUNT}/mass",
        "sparql_editor": f"{LDV_RCE_ACCOUNT}/mass/sparql",
        "endpoint": MASS_SPARQL_ENDPOINT,
        "tool": "query_sparql_mass",
    },
    {
        "naam": "Afbeeldingen (Beeldbank)",
        "frontend": f"{LDV_RCE_ACCOUNT}/afbeeldingen",
        "sparql_editor": f"{LDV_RCE_ACCOUNT}/afbeeldingen/sparql",
        "endpoint": AFBEELDINGEN_SPARQL_ENDPOINT,
        "tool": "query_sparql_afbeeldingen",
    },
    {
        "naam": "Bibliotheek (catalogus)",
        "frontend": f"{LDV_RCE_ACCOUNT}/bibliotheek",
        "sparql_editor": f"{LDV_RCE_ACCOUNT}/bibliotheek/sparql",
        "endpoint": BIBLIOTHEEK_SPARQL_ENDPOINT,
        "tool": "query_sparql_bibliotheek",
    },
]

_HEADER_FIELD_RE = re.compile(r"^#\s*(Version|Modified):\s*(\S+)", re.MULTILINE)


def bundled_ontology_version() -> dict[str, str]:
    """Lees versie en wijzigingsdatum uit de kopregels van het gebundelde
    CEO_RCE.ttl, zodat de verwijzing niet los daarvan kan verouderen."""
    with ONTOLOGY_FILE.open(encoding="utf-8") as handle:
        header = handle.read(2000)
    return {key.lower(): value for key, value in _HEADER_FIELD_RE.findall(header)}


def format_references() -> str:
    """Geef alle verwijzingen als leesbare tekst."""
    version = bundled_ontology_version()
    lines = [
        "Verwijzingen: bronnen achter de RCE CHO MCP-server",
        "",
        "Linked Data Voorziening (LDV) van de RCE -- frontend (voor mensen):",
        f"- Startpagina: {LDV_FRONTEND}",
        f"- Alle RCE-datasets, opgeslagen query's en data stories: {LDV_RCE_ACCOUNT}",
        "",
        "Datasets -- pagina in de LDV, SPARQL-editor in de browser en het",
        "SPARQL-endpoint dat deze server bevraagt:",
    ]
    for dataset in LDV_DATASETS:
        lines += [
            f"- {dataset['naam']}",
            f"  Frontend: {dataset['frontend']}",
            f"  SPARQL-editor: {dataset['sparql_editor']}",
            f"  Endpoint: {dataset['endpoint']}",
            f"  Tool: {dataset['tool']}()",
        ]
    lines += [
        f"- CHO, fallback-endpoint (service 'cho'): {CHO_SERVICE_ENDPOINT}",
        "  Wordt automatisch gebruikt als het CHO-endpoint hierboven niet",
        "  bereikbaar is of een 502/503/504 geeft.",
        "",
        "CEO-ontologie (Cultureel Erfgoed Ontologie):",
        f"- Ontologie-URI (opent in de LDV): {CEO_ONTOLOGY_URI}",
        f"- Namespace (PREFIX ceo:): {CEO_NAMESPACE}",
        f"- Bronbestand CEO_RCE.ttl: {CEO_TTL_URL}",
        f"- Repository: {CEO_GITHUB_REPO}",
        "- Deze server gebruikt een gebundelde kopie van CEO_RCE.ttl"
        f" (versie {version.get('version', 'onbekend')}, gewijzigd"
        f" {version.get('modified', 'onbekend')}). ontology_search(),"
        " ontology_describe_class() en ontology_describe_property() lezen die"
        " kopie; vergelijk bij twijfel met het bronbestand hierboven.",
        "",
        "Geef in een antwoord waar dat helpt de LDV-link mee, zodat de",
        "gebruiker de data zelf kan bekijken of de query kan herhalen in de",
        "SPARQL-editor.",
    ]
    return "\n".join(lines)
