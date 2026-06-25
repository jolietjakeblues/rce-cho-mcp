# Roadmap

## rce-cho-mcp

This roadmap describes the planned development of `rce-cho-mcp`.

The project starts with the RCE CHO dataset, but the long-term vision is broader: a reusable MCP architecture for the Linked Data ecosystem of the Rijksdienst voor het Cultureel Erfgoed.

---

## v0.1.0 - Stable CHO MCP

Goal: a reliable MCP server for basic CHO questions.

Scope:

- Query rijksmonumenten
- Count rijksmonumenten
- List rijksmonumenten
- Filter by municipality
- Filter by province
- Retrieve name, number and address
- Validate common SPARQL mistakes
- Support Claude Desktop

Deliverables:

- Working MCP server
- Basic ontology context
- Query validator
- SPARQL executor
- README
- Architecture document
- Vision document

---

## v0.2.0 - Validator and query patterns

Goal: reduce SPARQL errors before execution.

Scope:

- Strict SPARQL order validation
- FROM-clause validation
- Forbidden prefix validation
- Forbidden property validation
- Count-query validation
- SELECT DISTINCT guidance
- Query pattern library

---

## v0.3.0 - Query planner

Goal: move from free-form SPARQL generation to structured query planning.

Pipeline:

User question

↓

Intent

↓

Entities

↓

Filters

↓

Ontology paths

↓

SPARQL template

↓

Validation

↓

Execution

Examples:

- Count monuments in a municipality
- List monuments in a municipality
- Find monuments by function
- Find monuments by type
- Find monuments by province

---

## v0.4.0 - Benchmark suite

Goal: make quality measurable.

Each benchmark contains:

- Natural language question
- Expected intent
- Expected SPARQL pattern
- Expected result
- Notes

Example questions:

- Hoeveel rijksmonumenten staan in Zeist?
- Geef een lijst van rijksmonumenten in Zeist.
- Welke rijksmonumenten in Utrecht hebben een adres?
- Hoeveel rijksmonumenten staan in de provincie Utrecht?
- Welke kerken staan in Utrecht?
- Welke molens staan in Friesland?

---

## v0.5.0 - More CHO coverage

Goal: support more CHO concepts.

Scope:

- Complexen
- Archeologische complexen
- Archeologische terreinen
- Werelderfgoed
- Beschermde gezichten
- Functies
- Typen
- Actoren en rollen
- Geometrie

---

## v0.6.0 - Spatial queries

Goal: support geometry-aware questions.

Scope:

- Geometry retrieval
- Within queries
- Intersects queries
- Distance-based queries where supported
- Protected faces and monuments
- Municipality and province boundaries where available

---

## v0.7.0 - Result enrichment

Goal: make answers more useful.

Scope:

- Human-readable summaries
- Tables
- Links to source URIs
- Optional SPARQL output
- Explanation of used query pattern

---

## v1.0.0 - Stable public release

Goal: stable open-source release.

Requirements:

- Stable API
- Complete documentation
- Benchmark coverage
- Claude Desktop setup guide
- Known limitations
- Contribution guide
- License
- Changelog

---

# Long-term direction

After the CHO MCP is stable, the project may expand toward other RCE Linked Data sources.

Possible future modules:

- RCE Beeldbank
- RCE Bibliotheek
- HVDL geometry
- Other RCE graphs and datasets

The long-term goal is a natural language interface for Dutch cultural heritage Linked Data.