# Architecture

## RCE CHO MCP

Version: 0.1 (Draft)

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

Claude Desktop

↓

MCP Server

↓

Ontology

↓

Query Planner

↓

Validator

↓

SPARQL Executor

↓

RCE CHO Endpoint

↓

Formatter

↓

Natural language response
```

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

        validator.py

        prompts.py

        ontology/

            loader.py

            registry.py

            api.py

            CEO_RCE.ttl
```

Note: this reflects the actual module layout. Earlier drafts of this
document described a planned `tools.py` / `planner.py` / `ontology.py` /
`formatter.py` / `examples.py` split that was never built this way; the
responsibilities described below map onto the modules listed above.

---

# Responsibilities

## server.py

Registers the MCP server.

Registers all tools.

Contains no business logic.

---

## tools.py

Contains the MCP tools exposed to Claude.

Examples:

* get_ontology_context()
* validate_query()
* query_sparql()
* describe_resource()

---

## ontology.py

Contains all ontology knowledge.

Examples:

* prefixes

* classes

* properties

* semantic mappings

* query rules

* province URIs

---

## planner.py

Transforms a natural language question into a query plan.

Example:

Question

↓

Entity detection

↓

Intent detection

↓

Required ontology paths

↓

SPARQL template

---

## validator.py

Checks generated SPARQL before execution.

Examples:

* syntax order

* missing FROM

* forbidden properties

* invalid prefixes

* ontology consistency

---

## sparql.py

Responsible only for communication with the SPARQL endpoint.

No ontology logic.

No prompt logic.

---

## formatter.py

Transforms raw SPARQL JSON results into readable Dutch.

---

## prompts.py

Contains workflow instructions for the language model.

No ontology data.

---

## examples.py

Contains curated example queries.

Used only as guidance.

---

# Processing Pipeline

Every question follows the same pipeline.

```
Question

↓

Ontology context

↓

Query planning

↓

SPARQL generation

↓

Validation

↓

Execution

↓

Formatting

↓

Answer
```

---

# Development Strategy

The project evolves in small stable releases.

## Version 0.1

Stable MCP server

Basic ontology

Basic validator

Basic query execution

---

## Version 0.2

Query planner

Semantic mappings

Improved validation

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
