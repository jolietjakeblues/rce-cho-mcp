"""Tests voor validator.py: elke _find_*-detector apart, plus validate_sparql()."""

from rce_cho_mcp.validator import has_blocking_errors, validate_sparql


def test_valid_simple_query_has_no_errors():
    q = (
        "SELECT DISTINCT ?x WHERE { "
        "GRAPH <https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce> "
        "{ ?x a <https://example.org/C> } }"
    )
    result = validate_sparql(q)
    assert result["valid"] is True


def test_missing_select_is_error():
    result = validate_sparql("WHERE { ?s ?p ?o }")
    assert result["valid"] is False
    assert any("SELECT" in e for e in result["errors"])


def test_missing_where_is_error():
    result = validate_sparql("SELECT ?s")
    assert result["valid"] is False
    assert any("WHERE" in e for e in result["errors"])


def test_from_before_select_is_error():
    q = "FROM <https://x> SELECT ?s WHERE { ?s ?p ?o }"
    result = validate_sparql(q)
    assert result["valid"] is False


def test_count_without_alias_is_error():
    q = "SELECT COUNT(?s) WHERE { ?s ?p ?o }"
    result = validate_sparql(q)
    assert result["valid"] is False
    assert any("alias" in e.lower() for e in result["errors"])


def test_language_tagged_label_filter_warning():
    q = 'SELECT ?naam WHERE { ?rm skos:prefLabel ?naam . FILTER(?naam = "Zwolle") }'
    result = validate_sparql(q)
    assert any("skos:prefLabel" in w and "STR()" in w for w in result["warnings"])


def test_language_tagged_label_filter_with_str_is_safe():
    q = 'SELECT ?naam WHERE { ?rm skos:prefLabel ?naam . FILTER(STR(?naam) = "Zwolle") }'
    result = validate_sparql(q)
    assert not any("zonder STR()" in w for w in result["warnings"])


def test_order_by_optional_warning():
    q = "SELECT ?rm WHERE { ?rm a ?c . OPTIONAL { ?rm ?p ?o } } ORDER BY ?rm"
    result = validate_sparql(q)
    assert any("tweetraps-subquery" in w for w in result["warnings"])


def test_order_by_without_optional_is_safe():
    q = "SELECT ?rm WHERE { ?rm a ?c } ORDER BY ?rm"
    result = validate_sparql(q)
    assert not any("tweetraps-subquery" in w for w in result["warnings"])


def test_cartesian_product_warning_on_two_optionals():
    q = "SELECT ?rm WHERE { ?rm a ?c . OPTIONAL { ?rm ?p1 ?o1 } OPTIONAL { ?rm ?p2 ?o2 } }"
    result = validate_sparql(q)
    assert any("cartesisch product" in w for w in result["warnings"])


def test_single_optional_is_safe():
    q = "SELECT ?rm WHERE { ?rm a ?c . OPTIONAL { ?rm ?p1 ?o1 } }"
    result = validate_sparql(q)
    assert not any("cartesisch product" in w for w in result["warnings"])


def test_untyped_numeric_literal_warning():
    q = "SELECT ?rm WHERE { ?rm ceo:huisnummer 19 }"
    result = validate_sparql(q)
    assert any("huisnummer" in w and "aanhalingstekens" in w for w in result["warnings"])


def test_quoted_numeric_literal_is_safe():
    q = 'SELECT ?rm WHERE { ?rm ceo:huisnummer "19" }'
    result = validate_sparql(q)
    assert not any("huisnummer" in w for w in result["warnings"])


def test_geosparql_timeout_warning():
    q = "SELECT ?rm WHERE { ?rm geof:sfWithin ?gebied }"
    result = validate_sparql(q)
    assert any("Shapely" in w for w in result["warnings"])


def test_large_wkt_without_limit_warning():
    q = "SELECT ?rm ?wkt WHERE { ?rm geo:asWKT ?wkt }"
    result = validate_sparql(q)
    assert any("geo:asWKT" in w for w in result["warnings"])


def test_large_wkt_with_safe_limit_is_safe():
    q = "SELECT ?rm ?wkt WHERE { ?rm geo:asWKT ?wkt } LIMIT 20"
    result = validate_sparql(q)
    assert not any("geo:asWKT" in w for w in result["warnings"])


def test_groupby_overflow_warning():
    q = "SELECT ?rm ?oms WHERE { ?rm ceo:omschrijving ?oms } GROUP BY ?oms"
    result = validate_sparql(q)
    assert any("GROUP BY" in w for w in result["warnings"])


def test_monument_uri_concat_risk_detected():
    q = (
        "SELECT ?rm WHERE { "
        'BIND(URI(CONCAT("https://linkeddata.cultureelerfgoed.nl/cho-kennis/id/rijksmonument/", '
        "?rijksmonumentnummer)) AS ?rm) }"
    )
    result = validate_sparql(q)
    assert any("cultuurhistorischObjectnummer" in w for w in result["warnings"])


def test_monument_uri_concat_to_public_register_is_safe():
    q = (
        "SELECT ?link WHERE { "
        'BIND(URI(CONCAT("https://monumentenregister.cultureelerfgoed.nl/monumenten/", '
        "?rijksmonumentnummer)) AS ?link) }"
    )
    result = validate_sparql(q)
    assert not any("CONCAT bouwt een URI-pad" in w for w in result["warnings"])


def test_forbidden_prefix_warning():
    result = validate_sparql("SELECT ?x WHERE { ?x ceosp:iets ?y }")
    assert any("ceosp:" in w for w in result["warnings"])


def test_has_blocking_errors_true_for_invalid():
    assert has_blocking_errors("WHERE { ?s ?p ?o }") is True


def test_has_blocking_errors_false_for_valid():
    assert has_blocking_errors("SELECT ?s WHERE { ?s ?p ?o }") is False
