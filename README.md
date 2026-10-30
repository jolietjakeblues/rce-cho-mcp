# rce-cho-mcp

**Nederlands** | [English](#english)

---

## Nederlands

MCP-server voor het bevragen van de RCE Linked Data-omgeving voor Cultuurhistorische Objecten (CHO).

Dit project helpt LLM-clients zoals Claude Desktop, ChatGPT, LM Studio en Cursor om met de RCE Linked Data-omgeving te werken zonder te hoeven gokken naar classes, properties, graphs of modelleerpatronen.

Het doel is niet alleen het uitvoeren van SPARQL, maar betrouwbare interactie met Nederlandse cultureel-erfgoed linked data.

### Status

Beta (v0.2.0-beta).

Niet geaffilieerd met de Rijksdienst voor het Cultureel Erfgoed.

### Doelen

- Hallucinaties verminderen bij het werken met RCE linked data.
- Ontologiekennis beschikbaar maken voor clients.
- Thesaurus- en conceptkennis beschikbaar maken voor clients.
- Datasetsemantiek beschikbaar maken voor clients.
- Graafgrenzen expliciet maken.
- Querygeneratie transparant en inspecteerbaar houden.

### Functies

- Bevragen van het publieke RCE CHO SPARQL-endpoint.
- Doorzoeken en inspecteren van de CEO-ontologie.
- SKOS-labels herleiden naar concept-URI's.
- Fuzzy-zoeken naar concepten (met synoniemen) via het NDE Termennetwerk, inclusief externe thesauri (Wikidata, AAT).
- Inspecteren van resource-URI's.
- Valideren van SPARQL-queries voorafgaand aan uitvoering.
- Uitvoeren van SPARQL SELECT- en ASK-queries.
- Leveren van datasetsemantiek voor belangrijke modelleerpatronen.
- Detecteren van bekende endpoint-specifieke query-valkuilen voorafgaand aan uitvoering.
- Rapporteren van live datasetstatistieken (triples, entiteiten, aantallen per class en per property), met voortgangsrapportage voor de volledige-datasetscan.
- Verkennen van daadwerkelijke querypaden van/naar een class via steekproeven, onafhankelijk van wat de ontologie declareert.
- Automatische gemeente-resolutie en monumentenlijsten per gemeente, inclusief kadastrale oppervlakteberekening en een echte spatial join met het Kadaster.
- Bevragen van de aparte RCE MASS-dataset voor maritiem erfgoed (scheepswrakken wereldwijd).

### Linked Data-filosofie

De MCP gaat uit van de volgende workflow:

```
menselijke vraag
    ↓
conceptontdekking
    ↓
URI-resolutie
    ↓
ontologie-inspectie
    ↓
datasetsemantiek
    ↓
queryvalidatie
    ↓
SPARQL-uitvoering
```

Niet:

```
menselijke vraag
    ↓
gok een propertynaam
    ↓
voer query uit
```

### Linked Data-model

Het RCE linked data-ecosysteem bestaat uit meerdere lagen.

**Ontologie.** Definieert classes en properties. Voorbeelden: `ceo:Rijksmonument`, `ceo:heeftFunctie`, `ceo:heeftNaam`.

**Thesauri en SKOS-concepten.** Leveren betekenissen en labels. Voorbeelden: gemeenten, provincies, monumentfuncties, juridische statussen. Menselijke taal moet eerst vertaald worden naar concept-URI's.

**Dataset-graphs.** Bevatten de daadwerkelijke cultureel-erfgoeddata. Relevante triples kunnen verspreid zijn over meerdere named graphs.

### MCP-tools

**Ontdekking:** `ping`, `graphs_list`, `ontology_statistics`, `ontology_search`

**Ontologie:** `ontology_describe_class`, `ontology_describe_property`

**Live datasetstatistieken:** `dataset_statistics`, `class_instance_counts`, `property_usage_counts`, `explore_class`, `explore_incoming`

In tegenstelling tot de ontologietools hierboven (die beschrijven wat er *gedefinieerd* is in de meegeleverde CEO-ontologie), bevragen deze tools het live endpoint op wat er *daadwerkelijk aanwezig* is in de data: instance-aantallen per class/property (inclusief ontologieclasses met nul instances), en empirische verkenning van paden vooruit en achteruit op basis van een steekproef van echte instances.

`dataset_statistics`, `class_instance_counts` en `property_usage_counts` rapporteren live aantallen uit de huidige dataset (~58M triples), dagelijks ververst. Dit zijn volledige datasetscans; `dataset_statistics` kan een paar minuten duren.

`explore_class` vindt welke predicaten vanaf een class vertrekken en waar ze naartoe leiden; `explore_incoming` vindt welke classes en predicaten ernaartoe wijzen (de omgekeerde richting). Beide zijn steekproefgebaseerd en snel (enkele seconden), nuttig voor paden die nog niet gedekt zijn door de datasetsemantiek. Aantallen gelden alleen binnen de steekproef, niet datasetbreed.

**Datasetsemantiek:** `semantics_list_topics`, `semantics_describe_topic`

**Resolver:** `resolve_concept_label`, `describe_resource_uri`

**Gemeente & monumentenlijsten:** `resolve_gemeente`, `monumenten_in_gemeente`

`resolve_gemeente` disambigueert een gemeentenaam tegen gelijknamige provincies/kadastrale gemeenten. `monumenten_in_gemeente` combineert gemeente-resolutie, de juiste graph en een standaard juridische-statusfilter in één aanroep.

**Oppervlakte & kadaster:** `grootste_monumenten_oppervlakte`, `percelen_via_spatial_join`

`grootste_monumenten_oppervlakte` berekent server-side oppervlaktes uit polygoongeometrie (geen ruwe WKT naar de client). `percelen_via_spatial_join` berekent via een echte ruimtelijke join met het Kadaster KKG-endpoint welke percelen een rijksmonument daadwerkelijk overlapt, onafhankelijk van RCE's eigen (niet gegarandeerd complete) BRK-koppeling.

**Conceptzoeken (NDE Termennetwerk):** `zoek_concept_termennetwerk`, `lookup_termennetwerk_uri`

`zoek_concept_termennetwerk` doet een relevantie-gerangschikte, synoniemgevoelige zoekopdracht over gepubliceerde terminologiebronnen (standaard CHT, ABR; Wikidata en AAT beschikbaar) via de publieke, niet-geauthenticeerde GraphQL API van het Termennetwerk, in tegenstelling tot `resolve_concept_label`, dat alleen een exacte `skos:prefLabel`-match doet binnen onze eigen named graphs. `lookup_termennetwerk_uri` herleidt externe concept-URI's (bijvoorbeeld een `skos:exactMatch`-doel gevonden via `describe_resource_uri`) terug naar labels.

**Validatie:** `validate_query`, `validate_query_structured`

Validatiechecks omvatten onder meer:

- onveilige labelfilters (stil risico op nul resultaten)
- ongetypeerde numerieke literals op string-properties (bijvoorbeeld `ceo:huisnummer 19` in plaats van `ceo:huisnummer "19"`, ook een stil risico op nul resultaten)
- ontbrekende `DISTINCT` of `COUNT`-alias
- volgorde van `SELECT/FROM/WHERE`
- verdachte of niet-bestaande prefixen (`ceosp:`, `ceox:`) en handmatige taalfilters (`LANG()`/`LANGMATCHES()`)
- GeoSPARQL-relaties die structurele timeouts veroorzaken op dit endpoint (`geof:sfWithin` e.d.)
- `GROUP BY` op lange tekstvelden die een overflowfout veroorzaken
- `ORDER BY` gecombineerd met `OPTIONAL`-joins, wat consistent een HTTP 504 veroorzaakt op dit endpoint
- meerdere onafhankelijke `OPTIONAL`-blokken in één query, wat een cartesisch product oplevert in plaats van losse feiten
- een rijksmonument-/complex-/gezicht-/werelderfgoednummer dat via `CONCAT()` direct in een CHO-URI-pad wordt geplakt (dat padsegment is het interne `cultuurhistorischObjectnummer`, niet dat nummer)

**Uitvoering:** `query_sparql`, `query_sparql_json`, `query_sparql_geojson`, `query_sparql_mass`, `convert_rd_to_wgs84`

`query_sparql` geeft leesbare tekst terug met geclassificeerde foutcodes bij falen. `query_sparql_json` geeft ruwe SPARQL JSON terug voor agents, tabellen, benchmarks en vervolgverwerking. `query_sparql_geojson` converteert SELECT-resultaten met een WKT-geometrievariabele naar een GeoJSON FeatureCollection. `query_sparql_mass` bevraagt de aparte RCE MASS-dataset (maritiem erfgoed, eigen schema.org-achtige vocabulaire) in plaats van het CHO-endpoint — zie `semantics_describe_topic('maritime')`. `convert_rd_to_wgs84` converteert een enkel RD New-coördinatenpaar (EPSG:28992) naar WGS84.

**Endpoints.** Standaard gaan queries naar het "Speedy"-endpoint (standaardconform SPARQL 1.1, en het endpoint dat GeoSPARQL-functies zoals `geof:area()` daadwerkelijk ondersteunt). Als dat endpoint onbereikbaar is of een gateway-foutmelding geeft (502/503/504), probeert `execute_sparql()` automatisch één keer opnieuw tegen het "Virtuoso"-endpoint. Welk van de twee endpoints de hierboven genoemde query-eigenaardigheden (GROUP BY-overflow, ORDER BY+OPTIONAL-504, geof:sfWithin-timeout) exact geeft, is niet per-endpoint herverifieerd; de validator waarschuwt er hoe dan ook voor. Override met de omgevingsvariabelen `SPARQL_ENDPOINT` en `SPARQL_FALLBACK_ENDPOINT`.

**Resources en Prompts.** Naast tools biedt de server ook MCP Resources (`rce-cho://graphs`, `rce-cho://ontology/statistics`, `rce-cho://semantics/topics`, en de template `rce-cho://semantics/{topic}`) voor clients die statische referentiedata willen browsen/aanhechten zonder een tool aan te roepen, en twee MCP Prompts (`zoek_monumenten_in_gemeente`, `zoek_scheepswrak`) als voorgesorteerde workflow-starters.

### Waarom datasetsemantiek?

De RCE linked data-omgeving bevat meer dan ontologiedefinities. Clients hebben ook datasetsemantiek nodig om data goed te interpreteren. Voorbeelden:

- gebruik `ceo:hoofdfunctie` wanneer er meerdere functies bestaan
- geef de voorkeur aan `ceo:huidigeNaam` boven historische namen
- gebruik juridische-statusconcepten bij het tellen van actieve monumenten
- gebruik gemeente-concept-URI's in plaats van stringmatching

Zonder deze kennis genereren LLM's vaak plausibele maar onjuiste SPARQL.

### Voorbeeldvragen

- Hoeveel actieve rijksmonumenten liggen er in Zeist?
- Welke kerken liggen er in Roermond?
- Welke properties horen bij Rijksmonument?
- Herleid het label `Utrecht` in de OWMS-graph.
- Welke monumentfuncties komen voor in Maastricht?
- Welke archeologische terreinen komen voor in Limburg?

### Tests

```bash
pip install -e ".[dev]"
pytest
```

De testsuite draait volledig offline (gemockte/gefixeerde data, geen live SPARQL-calls) en dekt querybouw, validatie, parsing en de MCP-tool-/resource-/prompt-registratie.

### Configuratie Claude Desktop

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

### Ontwerpprincipe

De MCP biedt capabilities, geen workflows. De client bepaalt hoe ontologie-ontdekking, conceptresolutie, semantiek, validatie en uitvoering worden gecombineerd.

### Licentie

Dit project is uitgebracht onder de EUPL-1.2 (European Union Public Licence, versie 1.2).

Kort samengevat: je mag de code vrij gebruiken, aanpassen en verspreiden. Als je een afgeleid werk verspreidt of publiekelijk aanbiedt, moet dat ook onder de EUPL of een compatibele copyleft-licentie beschikbaar blijven. De volledige licentietekst staat in het bestand `LICENSE` in deze repository, en is officieel beschikbaar in alle EU-talen via de Europese Commissie.

---

## English

MCP server for querying the Dutch RCE Cultural Heritage Objects Linked Data ecosystem.

This project helps LLM clients such as Claude Desktop, ChatGPT, LM Studio and Cursor work with the RCE Linked Data environment without guessing classes, properties, graphs or modelling patterns.

The goal is not only SPARQL execution, but reliable interaction with Dutch cultural heritage linked data.

### Status

Beta (v0.2.0-beta).

Not affiliated with the Rijksdienst voor het Cultureel Erfgoed.

### Goals

- Reduce hallucinations when working with RCE linked data.
- Expose ontology knowledge to clients.
- Expose thesaurus and concept knowledge to clients.
- Expose dataset semantics to clients.
- Make graph boundaries explicit.
- Keep query generation transparent and inspectable.

### Features

- Query the public RCE CHO SPARQL endpoint.
- Search and inspect the CEO ontology.
- Resolve SKOS labels to concept URIs.
- Fuzzy-search concepts (with synonyms) across the NDE Network of Terms, including external thesauri (Wikidata, AAT).
- Inspect resource URIs.
- Validate SPARQL queries before execution.
- Execute SPARQL SELECT and ASK queries.
- Provide dataset semantics for important modelling patterns.
- Detect known endpoint-specific query pitfalls before execution.
- Report live dataset statistics (triples, entities, per-class and per-property counts), with progress reporting for the full-dataset scan.
- Explore actual query paths from/to a class via sampling, independent of what the ontology declares.
- Automatic municipality resolution and per-municipality monument lists, including cadastral area calculation and a real spatial join with the Cadastre.
- Query the separate RCE MASS dataset for maritime heritage (shipwrecks worldwide).

### Linked Data philosophy

The MCP assumes the following workflow:

```
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

```
human question
    ↓
guess a property name
    ↓
run query
```

### Linked Data model

The RCE linked data ecosystem consists of several layers.

**Ontology.** Defines classes and properties. Examples: `ceo:Rijksmonument`, `ceo:heeftFunctie`, `ceo:heeftNaam`.

**Thesauri and SKOS concepts.** Provide meanings and labels. Examples: municipalities, provinces, monument functions, legal statuses. Human language should first be translated to concept URIs.

**Dataset graphs.** Contain the actual cultural heritage data. Relevant triples may be spread across multiple named graphs.

### MCP tools

**Discovery:** `ping`, `graphs_list`, `ontology_statistics`, `ontology_search`

**Ontology:** `ontology_describe_class`, `ontology_describe_property`

**Live dataset statistics:** `dataset_statistics`, `class_instance_counts`, `property_usage_counts`, `explore_class`, `explore_incoming`

Unlike the ontology tools above (which describe what is *defined* in the bundled CEO ontology), these tools query the live endpoint for what is *actually present* in the data: instance counts per class/property (including ontology classes with zero instances), and empirical forward/backward path discovery based on a sample of real instances.

`dataset_statistics`, `class_instance_counts` and `property_usage_counts` report live counts from the current dataset (~58M triples), refreshed daily. These are full-dataset scans; `dataset_statistics` can take a couple of minutes.

`explore_class` finds which predicates lead out of a class and to what; `explore_incoming` finds which classes and predicates point into it (the reverse direction). Both are sample-based and fast (a few seconds), useful for paths not yet covered by dataset semantics. Counts only apply within the sample, not dataset-wide.

**Dataset semantics:** `semantics_list_topics`, `semantics_describe_topic`

**Resolver:** `resolve_concept_label`, `describe_resource_uri`

**Municipality & monument lists:** `resolve_gemeente`, `monumenten_in_gemeente`

`resolve_gemeente` disambiguates a municipality name against same-named provinces/cadastral municipalities. `monumenten_in_gemeente` combines municipality resolution, the right graph and a default legal-status filter in a single call.

**Area & cadastre:** `grootste_monumenten_oppervlakte`, `percelen_via_spatial_join`

`grootste_monumenten_oppervlakte` computes areas server-side from polygon geometry (no raw WKT sent to the client). `percelen_via_spatial_join` uses a real spatial join against the Cadastre's KKG endpoint to find which parcels actually overlap a rijksmonument, independent of RCE's own (not guaranteed complete) BRK link.

**Concept search (NDE Network of Terms):** `zoek_concept_termennetwerk`, `lookup_termennetwerk_uri`

`zoek_concept_termennetwerk` does a relevance-ranked, synonym-aware search across published terminology sources (CHT, ABR by default; Wikidata and AAT available) via the public, unauthenticated Network of Terms GraphQL API, unlike `resolve_concept_label`, which only does an exact `skos:prefLabel` match within our own named graphs. `lookup_termennetwerk_uri` resolves external concept URIs (e.g. a `skos:exactMatch` target found via `describe_resource_uri`) back to labels.

**Validation:** `validate_query`, `validate_query_structured`

Validation checks include:

- unsafe label filters (silent zero-result risk)
- untyped numeric literals on string properties (e.g. `ceo:huisnummer 19` instead of `ceo:huisnummer "19"`, also a silent zero-result risk)
- missing `DISTINCT` or `COUNT` alias
- `SELECT/FROM/WHERE` ordering
- suspicious/non-existent prefixes (`ceosp:`, `ceox:`) and manual language filters (`LANG()`/`LANGMATCHES()`)
- GeoSPARQL relations that cause structural timeouts on this endpoint (`geof:sfWithin` etc.)
- `GROUP BY` on long text fields that trigger an overflow error
- `ORDER BY` combined with `OPTIONAL` joins, which causes a consistent HTTP 504 on this endpoint
- multiple independent `OPTIONAL` blocks in one query, which produces a cartesian product instead of separate facts
- a rijksmonument/complex/gezicht/werelderfgoed number pasted directly into a CHO URI path via `CONCAT()` (that path segment is the internal `cultuurhistorischObjectnummer`, not that number)

**Execution:** `query_sparql`, `query_sparql_json`, `query_sparql_geojson`, `query_sparql_mass`, `convert_rd_to_wgs84`

`query_sparql` returns readable text with classified error codes on failure. `query_sparql_json` returns raw SPARQL JSON for agents, tables, benchmarks and follow-up processing. `query_sparql_geojson` converts SELECT results with a WKT geometry variable into a GeoJSON FeatureCollection. `query_sparql_mass` queries the separate RCE MASS dataset (maritime heritage, its own schema.org-like vocabulary) instead of the CHO endpoint -- see `semantics_describe_topic('maritime')`. `convert_rd_to_wgs84` converts a single RD New (EPSG:28992) coordinate pair to WGS84.

**Endpoints.** By default, queries go to the "Speedy" endpoint (standards-compliant SPARQL 1.1, and the endpoint that actually supports GeoSPARQL functions such as `geof:area()`). If that endpoint is unreachable or returns a gateway-level error (502/503/504), `execute_sparql()` automatically retries once against the "Virtuoso" endpoint. Which of the two endpoints exactly produces the query quirks listed above (GROUP BY overflow, ORDER BY+OPTIONAL 504, geof:sfWithin timeout) has not been re-verified per endpoint; the validator warns regardless. Override with the `SPARQL_ENDPOINT` and `SPARQL_FALLBACK_ENDPOINT` environment variables.

**Resources and Prompts.** Besides tools, the server also exposes MCP Resources (`rce-cho://graphs`, `rce-cho://ontology/statistics`, `rce-cho://semantics/topics`, and the template `rce-cho://semantics/{topic}`) for clients that want to browse/attach static reference data without calling a tool, and two MCP Prompts (`zoek_monumenten_in_gemeente`, `zoek_scheepswrak`) as pre-built workflow starters.

### Why dataset semantics?

The RCE linked data environment contains more than ontology definitions. Clients also need dataset semantics to interpret the data correctly. Examples:

- use `ceo:hoofdfunctie` when multiple functions exist
- prefer `ceo:huidigeNaam` over historical names
- use legal status concepts when counting active monuments
- use municipality concept URIs instead of string matching

Without this knowledge, LLMs often generate plausible but incorrect SPARQL.

### Example questions

- How many active rijksmonuments are located in Zeist?
- Which churches are located in Roermond?
- Which properties belong to Rijksmonument?
- Resolve the label `Utrecht` in the OWMS graph.
- Which monument functions occur in Maastricht?
- Which archaeological sites occur in Limburg?

### Tests

```bash
pip install -e ".[dev]"
pytest
```

The test suite runs entirely offline (mocked/fixture data, no live SPARQL calls) and covers query building, validation, parsing, and MCP tool/resource/prompt registration.

### Claude Desktop configuration

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

### Design principle

The MCP exposes capabilities, not workflows. The client decides how ontology discovery, concept resolution, semantics, validation and execution are combined.

### License

This project is released under the EUPL-1.2 (European Union Public Licence, version 1.2).

In short: you may freely use, modify and distribute the code. If you distribute or publicly offer a derivative work, it must remain available under the EUPL or a compatible copyleft licence. The full licence text is in the `LICENSE` file in this repository, and is officially available in all EU languages via the European Commission.

---

*"The future is unwritten."*  
— Joe Strummer

---