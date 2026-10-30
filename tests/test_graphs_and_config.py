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
