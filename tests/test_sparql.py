"""Tests voor sparql.py: pure functies, geen netwerk.

format_results() had een echte regressie (UnboundLocalError op elke
niet-lege resultatenset, door een lokale variabele die de module-functie
rows() binnen dezelfde functie overschaduwde) die hier bewust als eerste
test staat -- precies het soort fout die een offline test direct vangt.
"""

from rce_cho_mcp.sparql import (
    classify_error,
    escape_sparql_string,
    format_results,
    rd_to_wgs84,
    rows,
    to_geojson,
    wkt_to_geometry,
)


def test_format_results_non_empty_does_not_crash(sparql_json):
    out = format_results(sparql_json, max_rows=10)
    assert "Testmonument" in out
    assert "Gevonden: 2" in out


def test_format_results_respects_max_rows(sparql_json):
    out = format_results(sparql_json, max_rows=1)
    assert "max 1 getoond" in out
    assert out.count("https://example.org/rm/") == 1


def test_format_results_empty(empty_sparql_json):
    assert format_results(empty_sparql_json) == "Geen resultaten gevonden."


def test_format_results_boolean():
    assert format_results({"boolean": True}) == "Resultaat: True"


def test_rows_helper(sparql_json, empty_sparql_json):
    assert len(rows(sparql_json)) == 2
    assert rows(empty_sparql_json) == []
    assert rows({}) == []


def test_escape_sparql_string():
    assert escape_sparql_string('a"b\\c') == 'a\\"b\\\\c'


def test_rd_to_wgs84_amersfoort_origin():
    # RD-oorsprong (Amersfoort) moet dicht bij de bekende referentie liggen.
    lon, lat = rd_to_wgs84(155_000.0, 463_000.0)
    assert abs(lon - 5.387638889) < 0.01
    assert abs(lat - 52.156160556) < 0.01


def test_wkt_to_geometry_point():
    geom = wkt_to_geometry("POINT(4.9041 52.3676)")
    assert geom == {"type": "Point", "coordinates": [4.9041, 52.3676]}


def test_wkt_to_geometry_rd_point_rejected_without_convert_rd():
    # RD-coördinaten (binnen NL-bounds) zonder convert_rd=True -> None.
    assert wkt_to_geometry("POINT(155000 463000)") is None


def test_wkt_to_geometry_rd_point_converted():
    geom = wkt_to_geometry("POINT(155000 463000)", convert_rd=True)
    assert geom is not None
    assert geom["type"] == "Point"
    lon, lat = geom["coordinates"]
    assert abs(lon - 5.387638889) < 0.01
    assert abs(lat - 52.156160556) < 0.01


def test_wkt_to_geometry_polygon_with_hole():
    wkt = "POLYGON((0 0, 0 10, 10 10, 10 0, 0 0), (2 2, 2 4, 4 4, 4 2, 2 2))"
    geom = wkt_to_geometry(wkt)
    assert geom["type"] == "Polygon"
    assert len(geom["coordinates"]) == 2  # buitenring + 1 gat


def test_wkt_to_geometry_multipolygon():
    wkt = "MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)), ((2 2, 2 3, 3 3, 3 2, 2 2)))"
    geom = wkt_to_geometry(wkt)
    assert geom["type"] == "MultiPolygon"
    assert len(geom["coordinates"]) == 2


def test_wkt_to_geometry_unknown_returns_none():
    assert wkt_to_geometry("LINESTRING(0 0, 1 1)") is None


def test_to_geojson_skips_invalid_geometry():
    data = {
        "head": {"vars": ["wkt", "naam"]},
        "results": {
            "bindings": [
                {"wkt": {"value": "POINT(4.9 52.3)"}, "naam": {"value": "A"}},
                {"wkt": {"value": "LINESTRING(0 0, 1 1)"}, "naam": {"value": "B"}},
            ]
        },
    }
    out = to_geojson(data)
    assert len(out["features"]) == 1
    assert out["features"][0]["properties"]["naam"] == "A"
    assert out["_skipped"] == 1


def test_classify_error_groupby_overflow():
    code, advies = classify_error("Value of any type column too long", 500)
    assert code == "GROUPBY_OVERFLOW"
    assert "GROUP BY" in advies


def test_classify_error_timeout_mentions_two_stage_remedy():
    code, advies = classify_error("", 504)
    assert code == "TIMEOUT"
    assert "tweetraps-subquery" in advies


def test_classify_error_unknown():
    code, _ = classify_error("iets geks", 418)
    assert code == "HTTP_ERROR"
