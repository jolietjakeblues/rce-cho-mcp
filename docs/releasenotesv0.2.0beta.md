## rce-cho-mcp v0.2.0-beta

Beta release. Highlights since `v0.1.0-alpha` (37 commits):

- POST-based SPARQL execution (fixes HTTP 431 on large `VALUES` clauses)
- "Speedy" (standards-compliant SPARQL 1.1) is now the default endpoint, with automatic fallback to "Virtuoso" on connection failure or a 502/503/504
- New dataset-semantics topics: `addresses` (BAG address path) and registration-number identifiers (`rijksmonumentnummer`, `complexnummer`, `gezichtsnummer`, `werelderfgoednummer`)
- Unified the graph registry so every graph from `graphs_list()` is usable in `resolve_concept_label()`
- GeoJSON export (`query_sparql_geojson`) and RD New <-> WGS84 coordinate conversion (`convert_rd_to_wgs84`)
- Validator checks for `ORDER BY` + `OPTIONAL` timeouts, multi-valued `OPTIONAL` cartesian products, unquoted string-literal filters, and unsafe language-tagged label filters
- Documentation (README, CAPABILITIES.md, architecture.md) brought back in sync with the actual tool set and module layout

Not affiliated with the Rijksdienst voor het Cultureel Erfgoed.
