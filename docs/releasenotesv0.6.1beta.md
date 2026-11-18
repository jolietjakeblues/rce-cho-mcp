## rce-cho-mcp v0.6.1-beta

Fix release on top of `v0.6.0-beta`.

### Fixed

- **`query_sparql` could not reach the Afbeeldingen and Bibliotheek data.**
  A query with a `GRAPH` clause on
  `.../rce/afbeeldingen/graphs/photos`, `.../rce/bibliotheek/graphs/books`
  or `.../rce/bibliotheek/graphs/article` was sent to the CHO endpoint,
  where those graphs do not exist. The endpoint does not report an error
  for that, it silently returns 0 rows (`ASK`: false). In a client where the
  model did not use the dedicated tools `query_sparql_afbeeldingen` /
  `query_sparql_bibliotheek`, the data was therefore unreachable, and the
  model fell back on SERVICE federation, which fails between these
  endpoints
  - `query_sparql`, `query_sparql_json` and `query_sparql_geojson` now look
    at the graph IRIs in the query (`GRAPH`, `FROM`, `FROM NAMED`) and run
    the query on the endpoint those graphs belong to (Afbeeldingen,
    Bibliotheek or MASS). The result states that the query was rerouted. A
    query without such a graph behaves exactly as before
  - A query that combines graphs of different endpoints, or that uses
    `SERVICE` to another RCE endpoint, now returns a clear
    `MIXED_ENDPOINTS` message with the two-step alternative (first CHO, then
    a `VALUES` list on the other dataset) instead of silently returning
    nothing
  - The server instructions, `graphs_list()` and the `images` and `library`
    topics now say that `query_sparql` plus the `GRAPH` clause is a valid
    route, and that this data is never "unreachable"

### Changed

- `library` topic: place names in the catalogue often carry a suffix in
  brackets, e.g. `Amersfoort (stad)` (421 books, 239 articles) and
  `Amersfoort (gemeente)`; an exact match on `Amersfoort` returns 0. The
  topic now says to match with `STRSTARTS`/`CONTAINS`, and documents the
  two-step recipe for "literature on the monuments of municipality X"
  (verified for Amersfoort: 45 of 460 active rijksmonumenten have at least
  one title, 57 unique titles)

### Also in this release

- The `verwijzingen` tool, the `rce-cho://verwijzingen` resource and the
  README section with references to the LDV and the CEO ontology (issue
  #29) were merged after the `v0.6.0-beta` tag and are first released here

### Housekeeping

- Test suite extended from 170 to 189 tests (endpoint routing, mixed
  endpoints, SERVICE federation)

Not affiliated with the Rijksdienst voor het Cultureel Erfgoed.
