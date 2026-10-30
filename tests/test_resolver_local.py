"""Tests voor resolver.py die geen netwerk nodig hebben: alleen de
graph-naamvalidatie, die vóór elke SPARQL-aanroep gebeurt.
"""

import pytest

from rce_cho_mcp.resolver import _validate_graph_name


def test_known_graph_name_passes():
    _validate_graph_name("owms")  # mag niet raisen


def test_non_queryable_graph_name_gives_specific_message():
    with pytest.raises(ValueError, match="niet query-baar"):
        _validate_graph_name("ceo-ontology")


def test_unknown_graph_name_gives_generic_message():
    with pytest.raises(ValueError, match="Unknown graph_name"):
        _validate_graph_name("bestaat-niet")
