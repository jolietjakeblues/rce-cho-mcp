"""Tests voor graphs.py en config.py: één bron voor query-bare/niet-query-bare graphs."""

from rce_cho_mcp.config import DEFAULT_DATASET_GRAPH, KNOWN_GRAPHS, MASS_SPARQL_ENDPOINT
from rce_cho_mcp.graphs import NON_QUERYABLE_GRAPH_KEYS, format_graphs, list_graphs


def test_non_queryable_graphs_excluded_from_known_graphs():
    for key in NON_QUERYABLE_GRAPH_KEYS:
        assert key not in KNOWN_GRAPHS


def test_non_queryable_graphs_still_listed_for_discovery():
    keys = {row["key"] for row in list_graphs()}
    for key in NON_QUERYABLE_GRAPH_KEYS:
        assert key in keys


def test_format_graphs_flags_non_queryable_rows():
    out = format_graphs()
    assert "ceo-ontology" in out
    assert "LET OP: alleen informatief" in out


def test_default_dataset_graph_is_instanties_rce():
    assert DEFAULT_DATASET_GRAPH.endswith("/graph/instanties-rce")


def test_mass_endpoint_configured():
    assert MASS_SPARQL_ENDPOINT.startswith("https://")
    assert "mass" in MASS_SPARQL_ENDPOINT


def test_afbeeldingen_and_bibliotheek_endpoints_configured():
    from rce_cho_mcp.config import AFBEELDINGEN_SPARQL_ENDPOINT, BIBLIOTHEEK_SPARQL_ENDPOINT

    assert AFBEELDINGEN_SPARQL_ENDPOINT.endswith("/datasets/rce/afbeeldingen/sparql")
    assert BIBLIOTHEEK_SPARQL_ENDPOINT.endswith("/datasets/rce/bibliotheek/sparql")


def test_other_dataset_graphs_are_listed_but_not_cho_graph_names():
    """De graphs van Afbeeldingen/Bibliotheek bestaan niet op het CHO-endpoint:
    wel tonen in graphs_list(), niet toelaten als graph_name voor
    resolve_concept_label()."""
    from rce_cho_mcp.graphs import OTHER_DATASET_GRAPH_ROWS

    out = format_graphs()
    for row in OTHER_DATASET_GRAPH_ROWS:
        assert row["uri"] in out
        assert row["tool"] in out
        assert row["key"] not in KNOWN_GRAPHS
        assert row["uri"] not in KNOWN_GRAPHS.values()
