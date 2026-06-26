import urllib.error

from mcp.server.fastmcp import FastMCP

from rce_cho_mcp.ontology.api import (
    describe_class,
    describe_property,
    search_ontology,
    statistics,
)
from rce_cho_mcp.prompts import WORKFLOW_INSTRUCTIONS
from rce_cho_mcp.resolver import describe_resource, resolve_label
from rce_cho_mcp.semantics import format_topic, format_topics
from rce_cho_mcp.sparql import SPARQL_ENDPOINT, execute_sparql, format_results
from rce_cho_mcp.validator import format_validation_report, validate_sparql


mcp = FastMCP("RCE CHO SPARQL", instructions=WORKFLOW_INSTRUCTIONS)


@mcp.tool()
def ping() -> str:
    """Test of de MCP-server bereikbaar is."""
    return "RCE CHO MCP werkt."


@mcp.tool()
def ontology_statistics() -> str:
    """Geef statistieken over de ingelezen CEO-ontologie."""
    stats = statistics()
    return (
        "CEO-ontologie geladen.\n"
        f"Classes: {stats['classes']}\n"
        f"Properties: {stats['properties']}"
    )


@mcp.tool()
def ontology_search(term: str) -> str:
    """Zoek classes en properties in de CEO-ontologie."""
    return search_ontology(term)


@mcp.tool()
def ontology_describe_class(class_name: str) -> str:
    """Beschrijf een CEO-class op basis van de ingelezen ontologie."""
    return describe_class(class_name)


@mcp.tool()
def ontology_describe_property(property_name: str) -> str:
    """Beschrijf een CEO-property op basis van de ingelezen ontologie."""
    return describe_property(property_name)


@mcp.tool()
def semantics_list_topics() -> str:
    """Toon beschikbare dataset-semantiek onderwerpen."""
    return format_topics()


@mcp.tool()
def semantics_describe_topic(topic: str) -> str:
    """Geef interpretatieregels voor een dataset-semantiek onderwerp."""
    return format_topic(topic)


@mcp.tool()
def resolve_concept_label(label: str, graph_name: str = "owms", lang: str = "nl") -> str:
    """Resolveer een SKOS prefLabel naar concept-URI's in een named graph.

    Geeft alle matches terug met URI en rdf:type. De client kiest welke
    relevant is. De resolver kiest niet zelf.
    """
    matches = resolve_label(label, graph_name=graph_name, lang=lang)

    if not matches:
        return f"Geen concept gevonden voor label '{label}' in graph:{graph_name}."

    lines = [f"{len(matches)} match(es) gevonden voor '{label}' in graph:{graph_name}:"]

    for match in matches:
        types = ", ".join(match["types"]) if match["types"] else "onbekend"
        lines.append(f"- {match['uri']} (type: {types})")

    return "\n".join(lines)


@mcp.tool()
def describe_resource_uri(uri: str) -> str:
    """Beschrijf een resource: alle predicaten en waarden van een URI in de RCE-graph."""
    facts = describe_resource(uri)

    if not facts:
        return f"Geen gegevens gevonden voor resource: {uri}"

    lines = [f"{len(facts)} eigenschap(pen) gevonden voor {uri}:"]
    lines.extend(f"- {fact['predicate']} -> {fact['object']}" for fact in facts)

    return "\n".join(lines)


@mcp.tool()
def validate_query(sparql_query: str) -> str:
    """Valideer een SPARQL-query zonder deze uit te voeren."""
    return format_validation_report(sparql_query)


@mcp.tool()
def validate_query_structured(sparql_query: str) -> dict:
    """Valideer een SPARQL-query en geef errors/warnings gestructureerd terug."""
    return validate_sparql(sparql_query)


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