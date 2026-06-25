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
    "list_classes",
    "list_properties",
    "search_ontology",
    "statistics",
]

def statistics() -> dict[str, int]:
    """Return basic ontology statistics."""
    return {
        "classes": len(get_classes()),
        "properties": len(get_properties()),
    }

def list_classes() -> list[str]:
    """Return all ontology class names."""
    return sorted(get_classes().keys())

def list_properties() -> list[str]:
    """Return all ontology property names."""
    return sorted(get_properties().keys())

