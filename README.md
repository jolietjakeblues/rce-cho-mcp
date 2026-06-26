# rce-cho-mcp

MCP server for querying the Dutch RCE Cultural Heritage Objects linked data endpoint.

This project helps LLM clients query the public RCE CHO SPARQL endpoint with ontology guidance, concept resolution, query validation and SPARQL execution.

## Status

Experimental. Not affiliated with the Rijksdienst voor het Cultureel Erfgoed.

## What this MCP does

This MCP provides small, reusable tools for working with RCE CHO linked data.

It does not try to understand full user questions itself. The client combines the tools.

## Features

- Query the public RCE CHO SPARQL endpoint
- Search and inspect the CEO ontology
- Resolve SKOS labels to concept URIs
- Inspect resource URIs
- Validate SPARQL queries before execution
- Execute SPARQL SELECT and ASK queries

## MCP tools

### Discovery

- `ping`
- `ontology_statistics`
- `ontology_search`

### Ontology

- `ontology_describe_class`
- `ontology_describe_property`

### Resolver

- `resolve_concept_label`
- `describe_resource_uri`

### Validation

- `validate_query`
- `validate_query_structured`

### Execution

- `query_sparql`

## Claude Desktop config

```json
{
  "mcpServers": {
    "rce-cho": {
      "command": "C:\\Python314\\python.exe",
      "args": [
        "-m",
        "rce_cho_mcp.server"
      ],
      "cwd": "C:\\AI\\rce-cho-mcp"
    }
  }
}

## Example questions
Hoeveel rijksmonumenten staan in Zeist?
Geef een lijst van rijksmonumenten in Zeist.
Welke rijksmonumenten in Utrecht hebben een adres?
Hoeveel rijksmonumenten staan in de provincie Utrecht?
Welke properties horen bij Rijksmonument?
Resolveer het label Utrecht in de OWMS graph.
Design principle

### The MCP exposes capabilities, not fixed workflows.

Clients such as Claude Desktop, ChatGPT, Cursor or LM Studio should combine tools such as ontology search, label resolution, validation and query execution.

## License

EUPL-1.2