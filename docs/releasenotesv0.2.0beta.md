## rce-cho-mcp — 2026-11-06 fixes (post v0.2.0-beta, no version bump yet)

Prompted by a user report that `monumenten_in_gemeente()` silently fell back
to an unreliable path for archaeological objects. A full audit of the
codebase followed; this lists what was fixed, not just the triggering bug.

- `monumenten_in_gemeente()`/`largest_by_area()`: `juridische_status`/
  `monument_aard` now raise an explicit error when combined with a
  `class_name` other than `Rijksmonument` (these properties only exist
  there, rdfs:domain-wise) -- previously a silent empty result
- `monumenten_in_gemeente()` now works reliably for archaeological classes
  (`ArcheologischOnderzoeksgebied`, `Vondstlocatie`): the shared name lookup
  in `queries.py` also tries `ceo:heeftLocatieAanduiding`/`ceo:locatienaam`
  (Rijksmonument-only `ceo:heeftNaam` isn't the only naming path), and
  classes with a near-empty municipality link (`ArcheologischComplex`,
  `ArcheologischTerrein`, `Grondsporen`, `Vondsten`, `Complex`, `Gezicht`)
  now get a `waarschuwing` field with the best alternative instead of a
  silent empty result
- `percelen_via_spatial_join()`: fixed 0-parcel results for municipalities
  with diacritics (e.g. Súdwest-Fryslân) -- the municipality name is now
  resolved via a `skos:prefLabel` SPARQL lookup instead of parsed out of
  the OWMS URI slug; also added the missing `@sparql_text_errors()`
  decorator so an endpoint error no longer crashes the tool
- `validate_query()`/`validate_query_structured()`: fixed a false-positive
  `ORDER BY` + `OPTIONAL` 504 warning on the tool's own documented safe
  two-stage subquery pattern, a domain-whitelist bypass in the CONCAT-risk
  check (subdomain/path tricks), and a whitespace-fragile unaliased-COUNT
  check
- `query_sparql_geojson()`/`wkt_to_geometry()`: added `LINESTRING`/
  `MULTILINESTRING` support -- the `linies` graph's own documented example
  previously always returned an empty FeatureCollection
- Corrected several stale or incorrect numeric claims surfaced by
  `semantics_describe_topic()` (geometry triple counts, the CHOI/
  rijksmonumentnummer ratio, archaeology containment counts, a
  GRAPH-restriction contradiction between the `functions` and
  `legal_status`/`monument_aard` topics) against freshly re-verified live
  data, each now dated so future drift is easier to spot
- README, CAPABILITIES.md and architecture.md updated to reflect the above

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
