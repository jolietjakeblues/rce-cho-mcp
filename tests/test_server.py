"""Tests voor server.py: tool-registratie, annotations en schema-constraints.

Geen netwerkaanroepen -- dit test alleen de registratielaag (schema's,
annotations, resources, prompts), niet het daadwerkelijk uitvoeren van een
tool die een live SPARQL-call doet.
"""

import pytest

import rce_cho_mcp.server as server

EXPECTED_TOOL_COUNT = 28


def _tools():
    return server.mcp._tool_manager._tools


def test_tool_count():
    assert len(_tools()) == EXPECTED_TOOL_COUNT


def test_every_tool_has_readonly_hint():
    missing = [
        name
        for name, t in _tools().items()
        if not (t.annotations and t.annotations.readOnlyHint)
    ]
    assert missing == []


def test_every_tool_has_a_description():
    empty = [name for name, t in _tools().items() if not (t.description or "").strip()]
    assert empty == []


@pytest.mark.parametrize(
    ("tool_name", "param", "minimum", "maximum"),
    [
        ("class_instance_counts", "limit", 1, 1000),
        ("property_usage_counts", "limit", 1, 1000),
        ("explore_class", "sample_size", 100, 10_000),
        ("explore_incoming", "sample_size", 100, 10_000),
        ("monumenten_in_gemeente", "limit", 1, 200),
        ("grootste_monumenten_oppervlakte", "limit", 1, 200),
        ("percelen_via_spatial_join", "limit", 1, 500),
        ("query_sparql", "max_rows", 1, 10_000),
        ("query_sparql_mass", "max_rows", 1, 10_000),
        ("zoek_concept_termennetwerk", "max_resultaten", 1, 100),
    ],
)
def test_limit_param_schema_bounds(tool_name, param, minimum, maximum):
    schema = _tools()[tool_name].parameters["properties"][param]
    assert schema["minimum"] == minimum
    assert schema["maximum"] == maximum


async def test_out_of_range_limit_is_rejected_before_the_function_runs():
    with pytest.raises(Exception) as exc_info:
        await server.mcp.call_tool("class_instance_counts", {"limit": 99_999})
    assert "less_than_equal" in str(exc_info.value) or "1000" in str(exc_info.value)


def test_mass_tool_is_registered():
    assert "query_sparql_mass" in _tools()
