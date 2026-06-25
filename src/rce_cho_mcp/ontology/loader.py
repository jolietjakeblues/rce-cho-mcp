from pathlib import Path

from rdflib import Graph


ONTOLOGY_FILE = Path(__file__).parent / "CEO_RCE.ttl"


def load_ontology() -> Graph:
    """Load the CEO ontology from Turtle."""
    graph = Graph()
    graph.parse(ONTOLOGY_FILE, format="turtle")
    return graph


def count_triples() -> int:
    """Return the number of triples in the CEO ontology."""
    graph = load_ontology()
    return len(graph)