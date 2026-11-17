"""Tests voor de pure, netwerkloze hulpfuncties in gemeente.py en area.py."""

from rce_cho_mcp.area import _MONUMENT_AARD_URIS as area_aard_uris
from rce_cho_mcp.area import _clamp_limit as area_clamp_limit
from rce_cho_mcp.gemeente import _MONUMENT_AARD_URIS as gemeente_aard_uris
from rce_cho_mcp.gemeente import _clamp_limit as gemeente_clamp_limit
from rce_cho_mcp.gemeente import _normalize_gemeente_naam
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


def _edge(kind, voorganger, aantal_opvolgers=1):
    return {
        "kind": kind,
        "voorganger": voorganger,
        "naam": voorganger,
        "einddatum": "2021-12-31",
        "aantal_opvolgers": aantal_opvolgers,
    }


def test_select_voorgangers_includes_fully_merged_predecessors_transitively():
    from rce_cho_mcp.gemeente import _select_voorgangers

    edges = [_edge("nieuw", "oud1"), _edge("nieuw", "oud2"), _edge("oud1", "ouder")]
    meetellen, gesplitst = _select_voorgangers("nieuw", edges)
    assert {e["voorganger"] for e in meetellen} == {"oud1", "oud2", "ouder"}
    assert gesplitst == []


def test_select_voorgangers_excludes_split_predecessor_and_everything_below_it():
    """Een gemeente die over meerdere opvolgers is verdeeld (bv. Haaren ->
    Boxtel/Oisterwijk/Tilburg/Vught) is niet eenduidig toe te wijzen: niet
    meetellen, en ook niet verder door zijn eigen voorgangers lopen."""
    from rce_cho_mcp.gemeente import _select_voorgangers

    edges = [
        _edge("tilburg", "haaren", aantal_opvolgers=4),
        _edge("haaren", "nog_ouder"),
        _edge("tilburg", "berkel"),
    ]
    meetellen, gesplitst = _select_voorgangers("tilburg", edges)
    assert [e["voorganger"] for e in meetellen] == ["berkel"]
    assert [e["voorganger"] for e in gesplitst] == ["haaren"]


def test_format_herindeling_result_reports_breakdown_and_split():
    from rce_cho_mcp.gemeente import _format_herindeling_result

    lines = _format_herindeling_result(
        {
            "gemeente": "Voorne aan Zee",
            "herindeling": {
                "einddatum": None,
                "opvolgers": [],
                "gemeenten_meegeteld": [
                    {"uri": "u1", "naam": "Voorne aan Zee", "einddatum": None, "aantal": 0},
                    {"uri": "u2", "naam": "Brielle", "einddatum": "2022-12-31", "aantal": 341},
                ],
                "gesplitste_voorgangers": [
                    {"uri": "u3", "naam": "Haaren", "einddatum": "2020-12-31", "aantal": 7}
                ],
                "voorgangers_niet_meegeteld": [],
            },
        }
    )
    text = " ".join(lines)
    assert "Brielle (opgeheven 2022-12-31): 341" in text
    assert "NIET meegeteld" in text
    assert "Haaren" in text


def test_format_herindeling_result_flags_abolished_municipality():
    from rce_cho_mcp.gemeente import _format_herindeling_result

    lines = _format_herindeling_result(
        {
            "gemeente": "Brielle",
            "herindeling": {
                "einddatum": "2022-12-31",
                "opvolgers": [{"uri": "u1", "naam": "Voorne aan Zee"}],
                "gemeenten_meegeteld": [
                    {"uri": "u2", "naam": "Brielle", "einddatum": "2022-12-31", "aantal": 341}
                ],
                "gesplitste_voorgangers": [],
                "voorgangers_niet_meegeteld": [],
            },
        }
    )
    assert len(lines) == 1
    assert "opgeheven per 2022-12-31" in lines[0]
    assert "Voorne aan Zee" in lines[0]
