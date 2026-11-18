"""Tests voor routing.py: automatische endpoint-keuze op basis van graph-IRI's."""

import pytest

import rce_cho_mcp.routing as routing
import rce_cho_mcp.server as server
from rce_cho_mcp.config import AFBEELDINGEN_SPARQL_ENDPOINT, BIBLIOTHEEK_SPARQL_ENDPOINT
from rce_cho_mcp.graphs import OTHER_DATASET_GRAPH_ROWS
from rce_cho_mcp.routing import MixedEndpointsError, graph_iris, resolve_dataset

PHOTOS = "https://linkeddata.cultureelerfgoed.nl/rce/afbeeldingen/graphs/photos"
BOOKS = "https://linkeddata.cultureelerfgoed.nl/rce/bibliotheek/graphs/books"
ARTICLE = "https://linkeddata.cultureelerfgoed.nl/rce/bibliotheek/graphs/article"
INSTANTIES = "https://linkeddata.cultureelerfgoed.nl/graph/instanties-rce"
CHT = "https://data.cultureelerfgoed.nl/term/id/cht/thesaurus"

EMPTY = {"head": {"vars": ["s"]}, "results": {"bindings": []}}


def _q(*graphs):
    return "SELECT ?s WHERE { " + " ".join(f"GRAPH <{g}> {{ ?s ?p ?o }}" for g in graphs) + " }"


def test_graph_iris_finds_graph_from_and_from_named():
    q = (
        f"SELECT ?s FROM <{BOOKS}> FROM NAMED <{ARTICLE}> "
        f"WHERE {{ graph <{PHOTOS}> {{ ?s ?p ?o }} }}"
    )
    assert graph_iris(q) == [BOOKS, ARTICLE, PHOTOS]


def test_query_without_graph_or_with_cho_graph_stays_on_cho():
    assert resolve_dataset("SELECT ?s WHERE { ?s ?p ?o }") == "cho"
    assert resolve_dataset(_q(INSTANTIES)) == "cho"
    assert resolve_dataset("SELECT ?s WHERE { GRAPH ?g { ?s ?p ?o } }") == "cho"


@pytest.mark.parametrize(
    ("graph", "expected"),
    [
        (PHOTOS, "afbeeldingen"),
        (BOOKS, "bibliotheek"),
        (ARTICLE, "bibliotheek"),
        ("https://linkeddata.cultureelerfgoed.nl/graph/bib", "bibliotheek"),
        ("https://linkeddata.cultureelerfgoed.nl/graph/bib-aut", "bibliotheek"),
        ("https://mass.cultureelerfgoed.nl/graph/3061", "mass"),
    ],
)
def test_foreign_graph_routes_to_its_own_dataset(graph, expected):
    assert resolve_dataset(_q(graph)) == expected


def test_cho_graphs_with_a_similar_name_are_not_mistaken_for_bibliotheek():
    # ".../graph/bib" is een exacte match, geen prefix: CHO-graphs als
    # bebouwdeomgeving of buitenplaatsen mogen er niet door geraakt worden.
    for name in ("bebouwdeomgeving", "buitenplaatsen", "image"):
        graph = f"https://linkeddata.cultureelerfgoed.nl/graph/{name}"
        assert resolve_dataset(_q(graph)) == "cho"


def test_every_listed_other_dataset_graph_is_routed():
    """Elke graph die graphs_list() onder 'andere datasets' toont moet ook
    echt routeerbaar zijn -- anders belooft de tekst iets wat de code niet doet."""
    for row in OTHER_DATASET_GRAPH_ROWS:
        assert resolve_dataset(_q(row["uri"])) == row["dataset"]


def test_shared_thesaurus_graph_may_accompany_bibliotheek():
    assert resolve_dataset(_q(BOOKS, CHT)) == "bibliotheek"


def test_mixing_cho_only_graph_with_other_dataset_is_an_error():
    with pytest.raises(MixedEndpointsError) as exc:
        resolve_dataset(_q(PHOTOS, INSTANTIES))
    assert "twee stappen" in str(exc.value)
    assert INSTANTIES in str(exc.value)


def test_service_federation_to_another_rce_endpoint_is_an_error():
    q = (
        "SELECT ?s WHERE { ?s ?p ?o SERVICE "
        "<https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/bibliotheek/sparql> "
        "{ ?b ?q ?s } }"
    )
    with pytest.raises(MixedEndpointsError) as exc:
        resolve_dataset(q)
    assert "VALUES" in str(exc.value)


def test_service_to_an_external_source_is_left_alone():
    q = "SELECT ?s WHERE { SERVICE <https://query.wikidata.org/sparql> { ?s ?p ?o } }"
    assert resolve_dataset(q) == "cho"


def test_mixing_two_other_datasets_is_an_error():
    with pytest.raises(MixedEndpointsError):
        resolve_dataset(_q(PHOTOS, BOOKS))


def test_query_sparql_sends_photos_query_to_afbeeldingen_endpoint(monkeypatch):
    calls = []
    monkeypatch.setattr(
        routing, "post_sparql", lambda endpoint, query, timeout=30: calls.append(endpoint) or EMPTY
    )
    monkeypatch.setattr(
        routing, "execute_sparql", lambda query, timeout=30: pytest.fail("CHO-endpoint gebruikt")
    )
    out = server.query_sparql(_q(PHOTOS))
    assert calls == [AFBEELDINGEN_SPARQL_ENDPOINT]
    assert "RCE Afbeeldingen-endpoint" in out


def test_query_sparql_json_sends_books_query_to_bibliotheek_endpoint(monkeypatch):
    calls = []
    monkeypatch.setattr(
        routing, "post_sparql", lambda endpoint, query, timeout=30: calls.append(endpoint) or EMPTY
    )
    out = server.query_sparql_json(_q(BOOKS))
    assert calls == [BIBLIOTHEEK_SPARQL_ENDPOINT]
    assert "RCE Bibliotheek" in out["_endpoint_note"]
    assert out["results"] == EMPTY["results"]


def test_query_sparql_keeps_plain_cho_query_on_cho_without_note(monkeypatch):
    monkeypatch.setattr(routing, "execute_sparql", lambda query, timeout=30: EMPTY)
    monkeypatch.setattr(
        routing, "post_sparql", lambda *a, **k: pytest.fail("ander endpoint gebruikt")
    )
    out = server.query_sparql(_q(INSTANTIES))
    assert "Let op: uitgevoerd op" not in out
    assert "_endpoint_note" not in server.query_sparql_json(_q(INSTANTIES))


def test_query_sparql_reports_mixed_endpoints_instead_of_silent_zero(monkeypatch):
    monkeypatch.setattr(routing, "execute_sparql", lambda *a, **k: pytest.fail("uitgevoerd"))
    monkeypatch.setattr(routing, "post_sparql", lambda *a, **k: pytest.fail("uitgevoerd"))
    assert server.query_sparql(_q(BOOKS, INSTANTIES)).startswith("[MIXED_ENDPOINTS]")
    assert server.query_sparql_json(_q(BOOKS, INSTANTIES))["error"] == "MIXED_ENDPOINTS"
