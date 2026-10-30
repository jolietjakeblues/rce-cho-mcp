"""Tests voor de pure, netwerkloze hulpfuncties in gemeente.py en area.py."""

from rce_cho_mcp.area import _MONUMENT_AARD_URIS as area_aard_uris
from rce_cho_mcp.area import _clamp_limit as area_clamp_limit
from rce_cho_mcp.gemeente import _MONUMENT_AARD_URIS as gemeente_aard_uris
from rce_cho_mcp.gemeente import GEMEENTE_SUFFIX_RE, _normalize_gemeente_naam
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


def test_gemeente_suffix_regex_is_shared_with_brk_spatial():
    from rce_cho_mcp.brk_spatial import _GEMEENTE_SUFFIX_RE

    assert _GEMEENTE_SUFFIX_RE is GEMEENTE_SUFFIX_RE
