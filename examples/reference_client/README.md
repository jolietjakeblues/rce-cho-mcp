# Reference client

This is a worked example of one way to consume the RCE CHO MCP — a Dutch-language
question parser, query builder, and pipeline. It is **not part of the MCP server**
and is not exposed as a tool.

The server's job is to expose generic Linked Data capabilities (ontology
introspection, label resolution, validation, raw SPARQL execution). Turning a
Dutch sentence into a query is a client-side concern — any LLM client can do
this reasoning using the server's tools. This folder shows one way to do it
without an LLM, for testing/benchmarking purposes (see `tests/benchmark_*.md`).

To run it, add the repo root to `PYTHONPATH` so `reference_client` and the
installed `rce_cho_mcp` package both resolve.
