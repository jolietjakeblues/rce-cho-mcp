"""Gedeelde pytest-fixtures.

Deze testsuite doet opzettelijk GEEN live netwerkaanroepen naar de RCE/
Kadaster/Termennetwerk-endpoints: dat zou de suite traag en flaky maken, en
is niet nodig om de puur lokale logica (querybouw, parsing, validatie,
tool-registratie) te verifiëren. Live gedrag wordt handmatig getest (zie de
tests/benchmark_*.md-scenario's) en tijdens development met losse scripts.
"""

import pytest


@pytest.fixture
def sparql_json():
    """Een minimale, representatieve SPARQL-JSON-resultaatset."""
    return {
        "head": {"vars": ["rm", "naam"]},
        "results": {
            "bindings": [
                {
                    "rm": {"type": "uri", "value": "https://example.org/rm/1"},
                    "naam": {"type": "literal", "value": "Testmonument"},
                },
                {
                    "rm": {"type": "uri", "value": "https://example.org/rm/2"},
                },
            ]
        },
    }


@pytest.fixture
def empty_sparql_json():
    return {"head": {"vars": ["rm"]}, "results": {"bindings": []}}
