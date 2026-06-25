from functools import lru_cache
from pathlib import Path
from rdflib import Graph

ONTOLOGY_FILE = Path(__file__).parent / "CEO_RCE.ttl"


@lru_cache(maxsize=1)
def load_ontology() -> Graph:
    """Load the CEO ontology once and cache it."""
    graph = Graph()
    graph.parse(ONTOLOGY_FILE, format="turtle")
    return graph


def count_triples() -> int:
    return len(load_ontology())