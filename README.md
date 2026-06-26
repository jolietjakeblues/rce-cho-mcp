# rce-cho-mcp

MCP server for querying the Dutch RCE Cultural Heritage Objects Linked Data ecosystem.

This project helps LLM clients such as Claude Desktop, ChatGPT, LM Studio and Cursor work with the RCE Linked Data environment without guessing classes, properties, graphs or modelling patterns.

The goal is not only SPARQL execution, but reliable interaction with Dutch cultural heritage linked data.

## Status

Experimental.

Not affiliated with the Rijksdienst voor het Cultureel Erfgoed.

## Goals

* Reduce hallucinations when working with RCE linked data.
* Expose ontology knowledge to clients.
* Expose thesaurus and concept knowledge to clients.
* Expose dataset semantics to clients.
* Make graph boundaries explicit.
* Keep query generation transparent and inspectable.

## Features

* Query the public RCE CHO SPARQL endpoint.
* Search and inspect the CEO ontology.
* Resolve SKOS labels to concept URIs.
* Inspect resource URIs.
* Validate SPARQL queries before execution.
* Execute SPARQL SELECT and ASK queries.
* Provide dataset semantics for important modelling patterns.

## Linked Data philosophy

The MCP assumes the following workflow:

```text
human question
    ↓
concept discovery
    ↓
URI resolution
    ↓
ontology inspection
    ↓
dataset semantics
    ↓
query validation
    ↓
SPARQL execution
```

Not:

```text
human question
    ↓
guess a property name
    ↓
run query
```

## Linked Data model

The RCE linked data ecosystem consists of several layers.

### Ontology

Defines classes and properties.

Examples:

* `ceo:Rijksmonument`
* `ceo:heeftFunctie`
* `ceo:heeftNaam`

### Thesauri and SKOS concepts

Provide meanings and labels.

Examples:

* municipalities
* provinces
* monument functions
* legal statuses

Human language should first be translated to concept URIs.

### Dataset graphs

Contain the actual cultural heritage data.

Relevant triples may be spread across multiple named graphs.

## MCP tools

### Discovery

* `ping`
* `ontology_statistics`
* `ontology_search`

### Ontology

* `ontology_describe_class`
* `ontology_describe_property`

### Dataset semantics

* `semantics_list_topics`
* `semantics_describe_topic`

### Resolver

* `resolve_concept_label`
* `describe_resource_uri`

### Validation

* `validate_query`
* `validate_query_structured`

### Execution

* `query_sparql`

## Why dataset semantics?

The RCE linked data environment contains more than ontology definitions.

Clients also need guidance about interpretation patterns.

Examples:

* use `ceo:hoofdfunctie` when multiple functions exist
* prefer `ceo:huidigeNaam` over historical names
* use legal status concepts when counting active monuments
* use municipality concept URIs instead of string matching

Without this knowledge, LLMs often generate plausible but incorrect SPARQL.

## Example questions

* How many active rijksmonuments are located in Zeist?
* Which churches are located in Roermond?
* Which properties belong to Rijksmonument?
* Resolve the label `Utrecht` in the OWMS graph.
* Which monument functions occur in Maastricht?
* Which archaeological sites occur in Limburg?

## Claude Desktop configuration

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
```

## Design principle

The MCP exposes capabilities, not workflows.

The client decides how ontology discovery, concept resolution, semantics, validation and execution are combined.

## License

EUPL-1.2
