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
independent tool/resource/prompt capabilities, not a fixed pipeline)

↓

RCE CHO SPARQL endpoint ("Speedy" / "Virtuoso")
RCE MASS SPARQL endpoint (maritime heritage, separate dataset)
Kadaster KKG SPARQL endpoint (cadastral spatial join)

↓

Natural language response
```

There is no query planner and no enforced ordering: the MCP exposes
capabilities, and the client (the LLM) decides which tools to call and in
what order, guided by `WORKFLOW_INSTRUCTIONS` in `prompts.py`. See "Design
principle" in the README. Besides tools, the server also exposes a handful
of MCP Resources (static reference data, browsable without a tool call) and
two MCP Prompts (pre-built workflow starters) -- see `docs/CAPABILITIES.md`.

---

# Project Structure

```
rce-cho-mcp/

docs/

tests/

    test_*.py (pytest, no network -- see "Testing" below)

src/

    rce_cho_mcp/

        server.py

        http_server.py

        config.py

        graphs.py

        resolver.py

        semantics.py

        sparql.py

        stats.py

        area.py

        gemeente.py

        brk_spatial.py

        queries.py

        pitfalls.py

        limits.py

        termennetwerk.py

        validator.py

        prompts.py

        ontology/

            loader.py

            registry.py

            api.py

            CEO_RCE.ttl
```

Note: `http_server.py` runs the server over Streamable HTTP for deployments
like Render, instead of stdio.

---

# Responsibilities

## server.py

Registers the MCP server, every tool (`@mcp.tool()`, all marked
`readOnlyHint`), a handful of MCP Resources (`@mcp.resource()`, static
reference data at `rce-cho://...` URIs) and two MCP Prompts
(`@mcp.prompt()`, pre-built workflow starters). Contains no business
logic itself -- each tool delegates to the module responsible for that
capability. Limit-style parameters use `Annotated[int, Field(ge=..., le=...)]`
so the MCP client's own schema validation rejects an out-of-range value
before the tool function runs, rather than relying only on each
module's internal clamping.

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

## gemeente.py

Resolves a municipality name to its OWMS concept URI (disambiguated
against same-named provinces/cadastral municipalities), and combines
that with the right graph and a default legal-status filter to list
monuments in a municipality in one call.

---

## area.py

Computes monument surface area on the fly from polygon geometry
(`geof:area()`), for the subset of monuments without a materialized
area field, using a two-stage subquery (via `queries.py`) to avoid the
`ORDER BY` + `OPTIONAL` timeout.

---

## brk_spatial.py

Spatial join between RCE monument geometry and Kadaster KKG parcels,
as a geometrically verified alternative to RCE's own (not guaranteed
complete) BRK relation.

---

## queries.py

Shared SPARQL query-building helper for the two-stage subquery pattern
(inner `SELECT DISTINCT` without `OPTIONAL`, outer query adding name/
rijksmonumentnummer via `OPTIONAL` on the already-limited candidate
set) used by both `area.py` and `gemeente.py`.

---

## pitfalls.py

Canonical Dutch warning snippets for recurring query pitfalls (language-
tagged labels, the `ORDER BY`+`OPTIONAL` two-stage-subquery remedy, the
cartesian-product warning), shared by `validator.py`, `sparql.py`,
`resolver.py` and `prompts.py` instead of each repeating its own copy.

---

## limits.py

Shared result-limit tiers (e.g. `LIST_MAX_LIMIT`) for tools that return
a bounded sample/list, so similarly-weighted tools don't end up with
arbitrarily different limits.

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
`post_sparql()` is the shared, endpoint-agnostic POST primitive also
used directly for the MASS endpoint (`query_sparql_mass` in
`server.py`) and the Kadaster KKG endpoint (`brk_spatial.py`). Logs
every outbound request (endpoint, duration, fallback triggers) via the
standard `logging` module, to stderr. `sparql_text_errors`/
`sparql_dict_errors` are decorators shared by most tools in `server.py`
for consistent error formatting and logging, supporting both sync and
async tool functions.

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

Added since the initial 0.2 feature set, still within the beta: gemeente/
area/BRK-spatial-join tools, a second dataset (RCE MASS, maritime
heritage), an offline pytest regression suite, structured logging,
schema-level parameter constraints, tool annotations, and MCP Resources
and Prompts alongside the existing tools.

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

Two complementary layers:

* **`tests/test_*.py`** (pytest, run via `pytest`): fast, fully offline
  unit/registration tests -- query building, parsing, validator checks,
  and that every tool/resource/prompt is registered with the schema and
  annotations it should have. No live SPARQL calls; network behaviour
  is mocked or fixture-based. This is the regression net for the pure
  logic (it would have caught the `format_results()` variable-shadowing
  bug described in the release history as soon as it was introduced).
* **Benchmark questions** (`tests/benchmark_*.md`): manually-run,
  live-endpoint scenarios. Every feature must be backed by one. Each
  benchmark contains a natural language question, expected SPARQL,
  expected result and notes.

Together these ensure future improvements never reduce quality, at two
different speeds: pytest on every change, benchmarks for live-endpoint
behaviour that can't be mocked away.

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
