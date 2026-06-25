import urllib.error

from mcp.server.fastmcp import FastMCP

from rce_cho_mcp.prompts import WORKFLOW_INSTRUCTIONS
from rce_cho_mcp.sparql import SPARQL_ENDPOINT, execute_sparql, format_results
from rce_cho_mcp.ontology.registry import (
    get_classes,
    get_properties,
    describe_class,
    describe_property,
    search_ontology,
)

mcp = FastMCP("RCE CHO SPARQL", instructions=WORKFLOW_INSTRUCTIONS)


@mcp.tool()
def ping() -> str:
    """Test of de MCP-server bereikbaar is."""
    return "RCE CHO MCP werkt."

@mcp.tool()
def ontology_summary() -> str:
    """Geef een korte samenvatting van de ingelezen CEO-ontologie."""
    classes = get_classes()
    properties = get_properties()

    return (
        f"CEO-ontologie geladen.\n"
        f"Classes: {len(classes)}\n"
        f"Properties: {len(properties)}\n\n"
        f"Eerste classes:\n"
        + "\n".join(f"- {name}" for name in list(classes)[:10])
    )

@mcp.tool()
def ontology_describe_class(class_name: str) -> str:
    """Beschrijf een CEO-class op basis van de ingelezen ontologie."""
    return describe_class(class_name)

@mcp.tool()
def ontology_search(term: str) -> str:
    """Zoek classes en properties in de CEO-ontologie."""
    return search_ontology(term)

@mcp.tool()
def ontology_describe_property(property_name: str) -> str:
    """Beschrijf een CEO-property op basis van de ingelezen ontologie."""
    return describe_property(property_name)

@mcp.tool()
def query_sparql(sparql_query: str, max_rows: int = 100) -> str:
    """Voer een SPARQL SELECT of ASK query uit op het RCE CHO endpoint."""
    try:
        data = execute_sparql(sparql_query)
        return format_results(data, max_rows=max_rows)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return (
            f"HTTP fout {e.code} van endpoint {SPARQL_ENDPOINT}: {e.reason}\n\n"
            f"Endpoint antwoord:\n{body[:1000]}"
        )
    except Exception as e:
        return f"Onverwachte fout: {type(e).__name__}: {e}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()