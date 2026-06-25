from rdflib import OWL, RDF, RDFS, URIRef

from rce_cho_mcp.ontology.loader import load_ontology


def _local_name(uri: URIRef) -> str:
    text = str(uri)
    if "#" in text:
        return text.rsplit("#", 1)[1]
    return text.rstrip("/").rsplit("/", 1)[-1]


def get_classes() -> dict[str, str]:
    graph = load_ontology()
    classes = {}

    for subject in graph.subjects(RDF.type, OWL.Class):
        if isinstance(subject, URIRef):
            classes[_local_name(subject)] = str(subject)

    return dict(sorted(classes.items()))


def get_properties() -> dict[str, str]:
    graph = load_ontology()
    properties = {}

    property_types = [
        RDF.Property,
        OWL.ObjectProperty,
        OWL.DatatypeProperty,
        OWL.AnnotationProperty,
    ]

    for property_type in property_types:
        for subject in graph.subjects(RDF.type, property_type):
            if isinstance(subject, URIRef):
                properties[_local_name(subject)] = str(subject)

    return dict(sorted(properties.items()))


def get_label(uri: str) -> str | None:
    graph = load_ontology()
    for label in graph.objects(URIRef(uri), RDFS.label):
        return str(label)
    return None

def get_comment(uri: str) -> str | None:
    graph = load_ontology()
    for comment in graph.objects(URIRef(uri), RDFS.comment):
        return str(comment)
    return None

def describe_class(class_name: str) -> str:
    classes = get_classes()

    if class_name not in classes:
        available = ", ".join(classes.keys())
        return f"Onbekende class: {class_name}\n\nBeschikbare classes:\n{available}"

    uri = classes[class_name]
    label = get_label(uri) or class_name
    comment = get_comment(uri) or "Geen commentaar gevonden."

    return (
        f"Class: {class_name}\n"
        f"URI: {uri}\n"
        f"Label: {label}\n"
        f"Comment: {comment}"
    )