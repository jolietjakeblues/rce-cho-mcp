"""Tests voor references.py: verwijzingen naar de LDV en de CEO-ontologie."""

from rce_cho_mcp import config
from rce_cho_mcp.references import (
    CEO_TTL_URL,
    LDV_DATASETS,
    LDV_FRONTEND,
    bundled_ontology_version,
    format_references,
)


def test_references_cover_frontend_endpoints_and_ceo_ttl():
    out = format_references()
    assert LDV_FRONTEND in out
    assert CEO_TTL_URL in out
    assert "https://linkeddata.cultureelerfgoed.nl/def/ceo#" in out
    for dataset in LDV_DATASETS:
        assert dataset["frontend"] in out
        assert dataset["endpoint"] in out
        assert dataset["tool"] in out


def test_reference_endpoints_come_from_config():
    """De getoonde endpoints zijn dezelfde als die de tools echt bevragen."""
    endpoints = {dataset["endpoint"] for dataset in LDV_DATASETS}
    assert endpoints == {
        config.CHO_DATASET_ENDPOINT,
        config.MASS_SPARQL_ENDPOINT,
        config.AFBEELDINGEN_SPARQL_ENDPOINT,
        config.BIBLIOTHEEK_SPARQL_ENDPOINT,
    }
    assert config.CHO_SERVICE_ENDPOINT in format_references()


def test_bundled_ontology_version_is_read_from_the_ttl_header():
    version = bundled_ontology_version()
    assert version["version"][0].isdigit()
    assert len(version["modified"]) == 10
    assert version["version"] in format_references()
