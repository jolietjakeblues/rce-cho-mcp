"""Tests voor queries.py: de gedeelde tweetraps-subquery-bouwer."""

from rce_cho_mcp.queries import build_name_lookup_query


def test_build_name_lookup_query_structure():
    inner = "{ SELECT ?rm WHERE { ?rm a <https://example.org/C> } LIMIT 5 }"
    q = build_name_lookup_query(
        outer_vars="?rm ?naam ?rijksmonumentnummer",
        inner_select=inner,
        subject_var="rm",
    )
    assert "PREFIX ceo:" in q
    assert "SELECT DISTINCT ?rm ?naam ?rijksmonumentnummer WHERE" in q
    assert inner in q
    assert "OPTIONAL { ?rm ceo:rijksmonumentnummer ?rijksmonumentnummer . }" in q
    assert "OPTIONAL { ?rm ceo:heeftNaam ?nObj . ?nObj ceo:naam ?naam . }" in q


def test_build_name_lookup_query_extra_prefixes_and_order_by():
    q = build_name_lookup_query(
        outer_vars="?rm ?opp",
        inner_select="{ SELECT ?rm WHERE {} }",
        subject_var="rm",
        extra_prefixes="PREFIX geo: <http://www.opengis.net/ont/geosparql#>",
        outer_order_by="ORDER BY DESC(?opp)",
    )
    assert "PREFIX geo:" in q
    assert q.strip().endswith("ORDER BY DESC(?opp)")


def test_build_name_lookup_query_different_subject_var():
    q = build_name_lookup_query(
        outer_vars="?obj ?naam",
        inner_select="{ SELECT ?obj WHERE {} }",
        subject_var="obj",
    )
    assert "?obj ceo:rijksmonumentnummer" in q
    assert "?obj ceo:heeftNaam" in q
