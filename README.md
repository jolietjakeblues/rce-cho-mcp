# rce-cho-mcp

MCP server for querying the Dutch RCE Cultural Heritage Objects linked data endpoint.

This project helps LLM clients such as Claude Desktop query the public RCE CHO SPARQL endpoint with built-in ontology guidance, query validation and safe SPARQL patterns.

## Status

Experimental. Not affiliated with the Rijksdienst voor het Cultureel Erfgoed.

## Features

- Query the public RCE CHO SPARQL endpoint
- Get ontology context for classes, properties and common paths
- Validate SPARQL before execution
- Prevent common mistakes such as wrong `FROM` placement
- Support questions about rijksmonumenten by municipality and province

## MCP tools

- `get_ontology_context`
- `validate_query`
- `query_sparql`
- `describe_resource`
- `get_provincie_uri`

## Claude Desktop config

```json
{
  "mcpServers": {
    "rce-cho": {
      "command": "C:\\Python314\\python.exe",
      "args": [
        "C:\\AI\\rce-cho-mcp\\src\\rce_cho_mcp\\server.py"
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

## License

EUPL-1.2