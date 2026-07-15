# Architecture

## RCE CHO MCP

Version: 0.2.0-beta

---

# Vision

The RCE CHO MCP project provides a natural language interface to the Dutch Cultural Heritage Objects (CHO) Linked Data endpoint.

The goal is not simply to generate SPARQL queries. The goal is to enable researchers, heritage professionals, information specialists and software developers to explore Dutch cultural heritage data without requiring detailed knowledge of SPARQL or the CEO ontology.

The MCP server acts as an intelligent bridge between a Large Language Model and the RCE CHO SPARQL endpoint.

---

# Design Principles

The project follows several principles.

## Domain first

The ontology is the source of truth.

The language model must never invent classes, properties or query paths.

---

## Small responsibilities

Every module has exactly one responsibility.

Examples:

* endpoint communication
* validation
* ontology knowledge
* query planning
* result formatting

---

## Explainable behaviour

Every SPARQL query should be understandable.

The system should always be able to explain:

* why a class was chosen
* why a property was chosen
* why a UNION was used
* why DISTINCT was required

Nothing should be "magic".

---

## Safe by default

The MCP should prevent common mistakes before they reach the endpoint.

Examples include:

* missing FROM clause
* invalid query order
* forbidden prefixes
* invalid properties
* unsupported ontology paths

---

## Reusable

The project should not depend on one specific LLM.

Claude may currently provide the best results, but the architecture should also support future MCP clients such as ChatGPT, Gemini or others.

---

# System Architecture

```
User

↓

MCP client (e.g. Claude Desktop, Claude Code)

↓

MCP Server (ontology, live stats/exploration, dataset semantics,
concept resolution, validation and execution -- exposed as
independent tool capabilities, not a fixed pipeline)

↓

RCE CHO SPARQL endpoint

↓

Natural language response
```

There is no query planner and no enforced ordering: the MCP exposes
capabilities, and the client (the LLM) decides which tools to call and in
what order, guided by `WORKFLOW_INSTRUCTIONS` in `prompts.py`. See "Design
principle" in the README.

---

# Project Structure

```
rce-cho-mcp/

docs/

tests/

src/

    rce_cho_mcp/

        server.py

        config.py

        graphs.py

        resolver.py

        semantics.py

        sparql.py

        stats.py

        termennetwerk.py

        validator.py

        prompts.py

        ontology/

            loader.py

            registry.py

            api.py

            CEO_RCE.ttl
```

Note: `http_server.py` (not shown above, alongside `server.py`) runs the
server over Streamable HTTP for deployments like Render, instead of stdio.

---

# Responsibilities

## server.py

Registers the MCP server and every tool (`@mcp.tool()`). Contains no
business logic itself -- each tool delegates to the module responsible
for that capability.

---

## http_server.py

Runs the server over Streamable HTTP (used in production, e.g. on
Render) instead of stdio.

---

## config.py

Environment-driven configuration: endpoint URLs, default/fallback
dataset graph, Network of Terms endpoint.

---

## ontology/ (loader.py, registry.py, api.py)

Loads and queries the bundled CEO ontology (`CEO_RCE.ttl`): classes,
properties, domains/ranges, labels and comments. Static -- describes
what the ontology *defines*, not what the live data contains.

---

## stats.py

Live dataset statistics and empirical path exploration: dataset-wide
totals, per-class/per-property instance counts, and forward/backward
predicate discovery sampled from live instances. Complements `ontology/`
with what is *actually present* in the data.

---

## resolver.py

Resolves SKOS `prefLabel`s to concept URIs within known named graphs,
and describes an arbitrary resource URI (all its predicates and values).

---

## semantics.py

Interpretation rules for dataset semantics: function, legal status,
monument type, name, description, address -- the CEO paths and pitfalls
a client needs to query these correctly.

---

## graphs.py

Registry of known CHO named graphs.

---

## termennetwerk.py

Client for the public NDE Network of Terms GraphQL API: fuzzy,
synonym-aware concept search (CHT, ABR, Wikidata, AAT) and reverse
URI-to-label lookup.

---

## validator.py

Checks a SPARQL query against known RCE CHO pitfalls before execution:
unsafe label filters, forbidden prefixes, untyped numeric literals,
`ORDER BY`+`OPTIONAL` timeouts, cartesian-product risk, `GROUP BY`
overflow, GeoSPARQL timeout patterns, and query-clause ordering. Does
not validate classes or properties against the ontology.

---

## sparql.py

Executes SPARQL against the RCE CHO endpoint (POST, with a Speedy ->
Virtuoso fallback and HTTP-error classification), formats results as
text, and converts SELECT results with a WKT variable into GeoJSON.

---

## prompts.py

Contains `WORKFLOW_INSTRUCTIONS`, the server-level guidance (passed to
FastMCP's `instructions=`) covering tool ordering, dataset-semantics
patterns and SPARQL design rules.

---

# Processing Pipeline

There is no fixed pipeline the client must follow -- see "System
Architecture" above. In practice, most questions touch these capabilities,
loosely in this order, as guided by `WORKFLOW_INSTRUCTIONS`:

```
Question

↓

Ontology / live-stats context (what classes, properties and paths exist)

↓

Concept resolution (natural-language terms -> concept URIs)

↓

SPARQL construction (by the client/LLM, not a planner module)

↓

Validation

↓

Execution

↓

Answer
```

# Development Strategy

The project evolves in small stable releases.

## Version 0.1

Stable MCP server

Basic ontology

Basic validator

Basic query execution

---

## Version 0.2

Semantic mappings

Improved validation

Live dataset statistics and empirical path exploration

Network of Terms concept search

Note: the originally planned dedicated query-planner module was dropped
in favour of the capabilities model described under "System Architecture"
-- the client/LLM builds the SPARQL query itself from the exposed tools,
guided by `WORKFLOW_INSTRUCTIONS`.

---

## Version 0.3

Pattern library

More ontology coverage

Automatic query templates

---

## Version 0.4

Benchmark suite

Regression tests

Performance improvements

---

## Version 1.0

Stable public release.

---

# Testing

Every feature must be backed by benchmark questions.

Each benchmark contains:

* natural language question
* expected SPARQL
* expected result
* notes

Regression tests ensure future improvements never reduce quality.

---

# Open Source

The project is developed as an open-source reference implementation.

Goals:

* readable code

* clear documentation

* reproducible examples

* transparent development

The project is not affiliated with the Rijksdienst voor het Cultureel Erfgoed.

It uses the publicly available RCE CHO Linked Data endpoint.

---

# Long-term Vision

The long-term goal is not simply an MCP server.

The goal is to create a reusable architecture for interacting with Linked Open Data through natural language.

Although the first implementation targets the Dutch Cultural Heritage Objects dataset, the same architecture should eventually support additional cultural heritage datasets by replacing only the ontology module while keeping the planner, validator and execution pipeline unchanged.
