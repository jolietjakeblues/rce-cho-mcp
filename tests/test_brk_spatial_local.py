"""Tests voor brk_spatial.py die geen netwerk nodig hebben: alleen de
URI-veiligheidscheck in _resolve_rijksmonument_uri(), die vóór elke
SPARQL-aanroep gebeurt zodra de aanroeper een volledige URI meegeeft
(i.p.v. een kaal rijksmonumentnummer, dat via het aparte,
escape_sparql_string()-pad loopt en dus al veilig was).
"""

import pytest

from rce_cho_mcp.brk_spatial import _resolve_rijksmonument_uri, percelen_via_spatial_join


def test_resolve_rijksmonument_uri_rejects_sparql_injection():
    # Regressie: een identifier die met "http" begint werd ongewijzigd
    # teruggegeven en later ongefilterd in <{rm_uri}> geplakt
    # (SPARQL-injectie, zie security-audit 2026-11-06).
    with pytest.raises(ValueError, match="Ongeldige rijksmonument-URI"):
        _resolve_rijksmonument_uri("http://evil/> } UNION { ?s ?p ?o")


def test_percelen_via_spatial_join_turns_injection_into_error_dict():
    # De publieke tool-functie mag nooit raisen (zie de dict-foutafhandeling
    # door de rest van deze functie) -- de ValueError hierboven moet dus
    # hier al opgevangen zijn.
    result = percelen_via_spatial_join("http://evil/> } UNION { ?s ?p ?o")
    assert "error" in result
    assert "Ongeldige rijksmonument-URI" in result["error"]
