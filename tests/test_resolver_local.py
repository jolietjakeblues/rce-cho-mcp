"""Tests voor resolver.py die geen netwerk nodig hebben: de
graph-naamvalidatie en de URI-veiligheidscheck, die beide vóór elke
SPARQL-aanroep gebeuren.
"""

import pytest

from rce_cho_mcp.resolver import _validate_graph_name, describe_resource


def test_known_graph_name_passes():
    _validate_graph_name("owms")  # mag niet raisen


def test_non_queryable_graph_name_gives_specific_message():
    with pytest.raises(ValueError, match="niet query-baar"):
        _validate_graph_name("ceo-ontology")


def test_unknown_graph_name_gives_generic_message():
    with pytest.raises(ValueError, match="Unknown graph_name"):
        _validate_graph_name("bestaat-niet")


def test_describe_resource_rejects_sparql_injection_in_uri():
    # Regressie: uri werd ongefilterd in <{uri}> geplakt (SPARQL-injectie,
    # zie security-audit 2026-11-06) -- dit moet nu vóór elke netwerkaanroep
    # een ValueError geven, niet een (mogelijk gemanipuleerde) query uitvoeren.
    with pytest.raises(ValueError, match="Ongeldige URI"):
        describe_resource("http://evil/> } UNION { ?s ?p ?o")
