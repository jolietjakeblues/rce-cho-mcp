from rce_cho_mcp.ontology.registry import (
    describe_class,
    describe_property,
    get_classes,
    get_properties,
    search_ontology,
)

__all__ = [
    "describe_class",
    "describe_property",
    "get_classes",
    "get_properties",
    "search_ontology",
]

def statistics() -> dict[str, int]:
    """Return basic ontology statistics."""
    return {
        "classes": len(get_classes()),
        "properties": len(get_properties()),
    }