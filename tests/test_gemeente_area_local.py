"""Tests voor de pure, netwerkloze hulpfuncties in gemeente.py en area.py."""

from rce_cho_mcp.area import _MONUMENT_AARD_URIS as area_aard_uris
from rce_cho_mcp.area import _clamp_limit as area_clamp_limit
from rce_cho_mcp.gemeente import _MONUMENT_AARD_URIS as gemeente_aard_uris
from rce_cho_mcp.gemeente import _normalize_gemeente_naam
from rce_cho_mcp.gemeente import _clamp_limit as gemeente_clamp_limit
from rce_cho_mcp.limits import LIST_MAX_LIMIT


def test_area_and_gemeente_share_the_same_limit():
    assert area_clamp_limit(10_000) == LIST_MAX_LIMIT
    assert gemeente_clamp_limit(10_000) == LIST_MAX_LIMIT


def test_clamp_limit_lower_bound():
    assert area_clamp_limit(0) == 1
    assert gemeente_clamp_limit(-5) == 1


def test_area_and_gemeente_share_the_same_monument_aard_uris():
    assert area_aard_uris == gemeente_aard_uris
    assert set(area_aard_uris) == {"archeologisch", "onroerend gebouwd"}


def test_normalize_gemeente_naam_strips_wiki_suffix():
    assert _normalize_gemeente_naam("Utrecht (gemeente)") == "Utrecht"
    assert _normalize_gemeente_naam("Utrecht_(gemeente)") == "Utrecht"
    assert _normalize_gemeente_naam("  Zwolle  ") == "Zwolle"


def test_owms_graph_is_shared_with_brk_spatial():
    """brk_spatial.py haalt de gemeentenaam op via een skos:prefLabel-lookup
    in dezelfde OWMS-graph als resolve_gemeente() hier (niet langer door de
    naam uit de OWMS-URI te mangelen -- dat brak stil bij diakrieten, bv.
    "Súdwest-Fryslân", zie brk_spatial._fetch_geometry_and_gemeentes)."""
    from rce_cho_mcp.brk_spatial import _OWMS_GRAPH as brk_owms_graph
    from rce_cho_mcp.gemeente import _OWMS_GRAPH as gemeente_owms_graph

    assert brk_owms_graph is gemeente_owms_graph
