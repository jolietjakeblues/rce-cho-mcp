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
* Detect known Virtuoso-specific query pitfalls before execution.

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
* `graphs_list`
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

### Validation checks include:

* unsafe label filters (silent zero-result risk)
* missing `DISTINCT` or `COUNT` alias
* `SELECT/FROM/WHERE` ordering
* GeoSPARQL relations that cause structural timeouts on Virtuoso (`geof:sfWithin` etc.)
* `GROUP BY` on long text fields that trigger Virtuoso overflow errors

### Execution

* `query_sparql`
* `query_sparql_json`
* `query_sparql_geojson`
* `convert_rd_to_wgs84`

`query_sparql` returns readable text with classified error codes on failure.  
`query_sparql_json` returns raw SPARQL JSON for agents, tables, benchmarks and follow-up processing.  
`query_sparql_geojson` converts SELECT results with a WKT geometry variable into a GeoJSON FeatureCollection.  
`convert_rd_to_wgs84` converts a single RD New (EPSG:28992) coordinate pair to WGS84.

#### Endpoints

By default, queries go to the "Speedy" endpoint (standards-compliant SPARQL 1.1). If that endpoint is unreachable or returns a gateway-level error (502/503/504), `execute_sparql()` automatically retries once against the "Virtuoso" endpoint, which supports GeoSPARQL but has the query quirks listed above. Override with the `SPARQL_ENDPOINT` and `SPARQL_FALLBACK_ENDPOINT` environment variables.

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
