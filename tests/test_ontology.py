"""Tests voor de ontology-module. Leest alleen het lokaal gebundelde
CEO_RCE.ttl-bestand, geen netwerk nodig."""

from rce_cho_mcp.ontology.api import list_classes, list_properties, statistics
from rce_cho_mcp.ontology.registry import (
    CLASS_NOTES,
    PROPERTY_NOTES,
    describe_class,
    describe_property,
    get_classes,
    get_properties_for_class,
    search_ontology,
)
from rce_cho_mcp.semantics import FUNCTION_PATH_NOTE, MONUMENT_AARD_WARNING


def test_ontology_loads_and_has_classes():
    classes = get_classes()
    assert "Rijksmonument" in classes
    assert classes["Rijksmonument"].startswith("https://linkeddata.cultureelerfgoed.nl/def/ceo#")


def test_statistics_counts_match_list_functions():
    stats = statistics()
    assert stats["classes"] == len(list_classes())
    assert stats["properties"] == len(list_properties())
    assert stats["classes"] > 0
    assert stats["properties"] > 0


def test_describe_class_known():
    out = describe_class("Rijksmonument")
    assert "Class: Rijksmonument" in out
    assert "Let op:" in out  # CLASS_NOTES is aangehaakt


def test_describe_class_unknown():
    out = describe_class("BestaatNiet")
    assert "Onbekende class" in out


def test_describe_property_known():
    out = describe_property("heeftMonumentAard")
    assert "Property: heeftMonumentAard" in out
    assert "Let op:" in out


def test_search_ontology_finds_rijksmonument():
    out = search_ontology("rijksmonument")
    assert "Rijksmonument" in out


def test_get_properties_for_class_returns_dict():
    props = get_properties_for_class("Rijksmonument")
    assert isinstance(props, dict)


def test_class_and_property_notes_reuse_shared_semantics_constants():
    assert MONUMENT_AARD_WARNING in CLASS_NOTES["Rijksmonument"]
    assert FUNCTION_PATH_NOTE in CLASS_NOTES["Rijksmonument"]
    assert MONUMENT_AARD_WARNING in PROPERTY_NOTES["heeftMonumentAard"]
