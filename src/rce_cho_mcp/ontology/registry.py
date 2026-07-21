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


def _preferred_literal(uri: str, predicate, preferred_lang: str = "nl") -> str | None:
    """Return one literal for (uri, predicate, ?), preferring preferred_lang.

    The ontology declares both @nl and @en variants for most labels/comments.
    rdflib's iteration order over multiple objects for the same predicate is
    not something to rely on for language selection, even though it happens
    to follow file order (@nl first) in practice -- this makes the preference
    explicit instead.
    """
    graph = load_ontology()
    fallback = None

    for value in graph.objects(URIRef(uri), predicate):
        if getattr(value, "language", None) == preferred_lang:
            return str(value)
        if fallback is None:
            fallback = value

    return str(fallback) if fallback is not None else None


def get_label(uri: str) -> str | None:
    return _preferred_literal(uri, RDFS.label)


def get_comment(uri: str) -> str | None:
    return _preferred_literal(uri, RDFS.comment)


def get_properties_for_class(class_name: str) -> dict[str, str]:
    classes = get_classes()

    if class_name not in classes:
        return {}

    graph = load_ontology()
    class_uri = URIRef(classes[class_name])
    properties = {}

    for prop in graph.subjects(RDFS.domain, class_uri):
        if isinstance(prop, URIRef):
            properties[_local_name(prop)] = str(prop)

    return dict(sorted(properties.items()))


def describe_class(class_name: str) -> str:
    classes = get_classes()

    if class_name not in classes:
        available = ", ".join(list(classes.keys())[:50])
        return f"Onbekende class: {class_name}\n\nEerste beschikbare classes:\n{available}"

    uri = classes[class_name]
    label = get_label(uri) or class_name
    comment = get_comment(uri) or "Geen commentaar gevonden."
    properties = get_properties_for_class(class_name)

    lines = [
        f"Class: {class_name}",
        f"URI: {uri}",
        f"Label: {label}",
        f"Comment: {comment}",
        "",
        f"Properties met rdfs:domain {class_name}: {len(properties)}",
    ]

    if properties:
        lines.extend(f"- {name}: {prop_uri}" for name, prop_uri in properties.items())

    return "\n".join(lines)


def search_ontology(term: str) -> str:
    term_lower = term.lower().strip()

    classes = get_classes()
    properties = get_properties()

    class_matches = [
        name
        for name in classes
        if term_lower in name.lower()
        or term_lower in (get_label(classes[name]) or "").lower()
        or term_lower in (get_comment(classes[name]) or "").lower()
    ]

    property_matches = [
        name
        for name in properties
        if term_lower in name.lower()
        or term_lower in (get_label(properties[name]) or "").lower()
        or term_lower in (get_comment(properties[name]) or "").lower()
    ]

    lines = [
        f"Zoekterm: {term}",
        "",
        f"Classes: {len(class_matches)}",
    ]

    lines.extend(f"- {name}: {classes[name]}" for name in class_matches[:20])

    lines.append("")
    lines.append(f"Properties: {len(property_matches)}")
    lines.extend(f"- {name}: {properties[name]}" for name in property_matches[:20])

    return "\n".join(lines)


def get_domain(uri: str) -> list[str]:
    graph = load_ontology()
    return [str(value) for value in graph.objects(URIRef(uri), RDFS.domain)]


def get_range(uri: str) -> list[str]:
    graph = load_ontology()
    return [str(value) for value in graph.objects(URIRef(uri), RDFS.range)]


def describe_property(property_name: str) -> str:
    properties = get_properties()

    if property_name not in properties:
        available = ", ".join(list(properties.keys())[:50])
        return f"Onbekende property: {property_name}\n\nEerste beschikbare properties:\n{available}"

    uri = properties[property_name]
    label = get_label(uri) or property_name
    comment = get_comment(uri) or "Geen commentaar gevonden."
    domains = get_domain(uri)
    ranges = get_range(uri)

    lines = [
        f"Property: {property_name}",
        f"URI: {uri}",
        f"Label: {label}",
        f"Comment: {comment}",
        "",
        "Domain:",
    ]

    if domains:
        lines.extend(f"- {domain}" for domain in domains)
    else:
        lines.append("- Geen domain gevonden.")

    lines.append("")
    lines.append("Range:")

    if ranges:
        lines.extend(f"- {range_uri}" for range_uri in ranges)
    else:
        lines.append("- Geen range gevonden.")

    return "\n".join(lines)