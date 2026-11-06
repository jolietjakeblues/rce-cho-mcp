"""Tests voor stats.py die geen netwerk nodig hebben: alleen de
class_uri-veiligheidscheck, die vóór elke SPARQL-aanroep gebeurt.
"""

import pytest

from rce_cho_mcp.stats import explore_class_paths, explore_incoming_paths


def test_explore_class_paths_rejects_sparql_injection_in_class_uri():
    # Regressie: class_uri werd ongefilterd in <{class_uri}> geplakt
    # (SPARQL-injectie, zie security-audit 2026-11-06), anders dan
    # area.py/gemeente.py die een class_name via get_classes() opzoeken.
    with pytest.raises(ValueError, match="Ongeldige class_uri"):
        explore_class_paths("http://evil/> } UNION { ?s ?p ?o")


def test_explore_incoming_paths_rejects_sparql_injection_in_class_uri():
    with pytest.raises(ValueError, match="Ongeldige class_uri"):
        explore_incoming_paths("http://evil/> } UNION { ?s ?p ?o")
