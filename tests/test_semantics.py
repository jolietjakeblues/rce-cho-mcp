"""Tests voor semantics.py."""

from rce_cho_mcp.semantics import (
    FUNCTION_PATH_NOTE,
    MONUMENT_AARD_WARNING,
    SEMANTIC_TOPICS,
    describe_topic,
    get_known_value_uris,
    list_topics,
)


def test_list_topics_is_sorted_and_non_empty():
    topics = list_topics()
    assert len(topics) == len(SEMANTIC_TOPICS)
    keys = [t["topic"] for t in topics]
    assert keys == sorted(keys)


def test_describe_topic_known():
    data = describe_topic("legal_status")
    assert data["found"] is True
    assert data["patterns"]


def test_describe_topic_unknown():
    data = describe_topic("bestaat-niet")
    assert data["found"] is False
    assert "legal_status" in data["available_topics"]


def test_get_known_value_uris_legal_status():
    uris = get_known_value_uris("legal_status")
    assert set(uris.keys()) == {"rijksmonument", "voorbeschermd", "geen rijksmonument"}
    assert all(u.startswith("https://") for u in uris.values())


def test_get_known_value_uris_monument_aard():
    uris = get_known_value_uris("monument_aard")
    assert set(uris.keys()) == {"archeologisch", "onroerend gebouwd"}


def test_maritime_topic_exists_and_points_to_mass_tool():
    data = describe_topic("maritime")
    assert data["found"] is True
    assert "query_sparql_mass" in data["description"]


def test_monument_aard_warning_and_function_path_note_are_shared():
    # Deze module-constanten worden ook in ontology/registry.py hergebruikt
    # (zie test_ontology.py); hier alleen checken dat ze bestaan en niet leeg zijn.
    assert "GEEN fijnmazige" in MONUMENT_AARD_WARNING
    assert "heeftOorspronkelijkeFunctie" in FUNCTION_PATH_NOTE
