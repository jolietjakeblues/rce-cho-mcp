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
- Detecteren van bekende Virtuoso-specifieke query-valkuilen voorafgaand aan uitvoering.
- Rapporteren van live datasetstatistieken (triples, entiteiten, aantallen per class en per property).
- Verkennen van daadwerkelijke querypaden van/naar een class via steekproeven, onafhankelijk van wat de ontologie declareert.

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

**Conceptzoeken (NDE Termennetwerk):** `zoek_concept_termennetwerk`, `lookup_termennetwerk_uri`

`zoek_concept_termennetwerk` doet een relevantie-gerangschikte, synoniemgevoelige zoekopdracht over gepubliceerde terminologiebronnen (standaard CHT, ABR; Wikidata en AAT beschikbaar) via de publieke, niet-geauthenticeerde GraphQL API van het Termennetwerk, in tegenstelling tot `resolve_concept_label`, dat alleen een exacte `skos:prefLabel`-match doet binnen onze eigen named graphs. `lookup_termennetwerk_uri` herleidt externe concept-URI's (bijvoorbeeld een `skos:exactMatch`-doel gevonden via `describe_resource_uri`) terug naar labels.

**Validatie:** `validate_query`, `validate_query_structured`

Validatiechecks omvatten onder meer:

- onveilige labelfilters (stil risico op nul resultaten)
- ongetypeerde numerieke literals op string-properties (bijvoorbeeld `ceo:huisnummer 19` in plaats van `ceo:huisnummer "19"`, ook een stil risico op nul resultaten)
- ontbrekende `DISTINCT` of `COUNT`-alias
- volgorde van `SELECT/FROM/WHERE`
- verdachte of niet-bestaande prefixen (`ceosp:`, `ceox:`) en handmatige taalfilters (`LANG()`/`LANGMATCHES()`)
- GeoSPARQL-relaties die structurele timeouts veroorzaken op Virtuoso (`geof:sfWithin` e.d.)
- `GROUP BY` op lange tekstvelden die Virtuoso-overflowfouten veroorzaken
- `ORDER BY` gecombineerd met `OPTIONAL`-joins, wat consistent een HTTP 504 veroorzaakt op dit endpoint
- meerdere onafhankelijke `OPTIONAL`-blokken in één query, wat een cartesisch product oplevert in plaats van losse feiten

**Uitvoering:** `query_sparql`, `query_sparql_json`, `query_sparql_geojson`, `convert_rd_to_wgs84`

`query_sparql` geeft leesbare tekst terug met geclassificeerde foutcodes bij falen. `query_sparql_json` geeft ruwe SPARQL JSON terug voor agents, tabellen, benchmarks en vervolgverwerking. `query_sparql_geojson` converteert SELECT-resultaten met een WKT-geometrievariabele naar een GeoJSON FeatureCollection. `convert_rd_to_wgs84` converteert een enkel RD New-coördinatenpaar (EPSG:28992) naar WGS84.

**Endpoints.** Standaard gaan queries naar het "Speedy"-endpoint (standaardconform SPARQL 1.1). Als dat endpoint onbereikbaar is of een gateway-foutmelding geeft (502/503/504), probeert `execute_sparql()` automatisch één keer opnieuw tegen het "Virtuoso"-endpoint, dat GeoSPARQL ondersteunt maar de hierboven genoemde query-eigenaardigheden heeft. Override met de omgevingsvariabelen `SPARQL_ENDPOINT` en `SPARQL_FALLBACK_ENDPOINT`.

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
- Detect known Virtuoso-specific query pitfalls before execution.
- Report live dataset statistics (triples, entities, per-class and per-property counts).
- Explore actual query paths from/to a class via sampling, independent of what the ontology declares.

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

**Concept search (NDE Network of Terms):** `zoek_concept_termennetwerk`, `lookup_termennetwerk_uri`

`zoek_concept_termennetwerk` does a relevance-ranked, synonym-aware search across published terminology sources (CHT, ABR by default; Wikidata and AAT available) via the public, unauthenticated Network of Terms GraphQL API, unlike `resolve_concept_label`, which only does an exact `skos:prefLabel` match within our own named graphs. `lookup_termennetwerk_uri` resolves external concept URIs (e.g. a `skos:exactMatch` target found via `describe_resource_uri`) back to labels.

**Validation:** `validate_query`, `validate_query_structured`

Validation checks include:

- unsafe label filters (silent zero-result risk)
- untyped numeric literals on string properties (e.g. `ceo:huisnummer 19` instead of `ceo:huisnummer "19"`, also a silent zero-result risk)
- missing `DISTINCT` or `COUNT` alias
- `SELECT/FROM/WHERE` ordering
- suspicious/non-existent prefixes (`ceosp:`, `ceox:`) and manual language filters (`LANG()`/`LANGMATCHES()`)
- GeoSPARQL relations that cause structural timeouts on Virtuoso (`geof:sfWithin` etc.)
- `GROUP BY` on long text fields that trigger Virtuoso overflow errors
- `ORDER BY` combined with `OPTIONAL` joins, which causes a consistent HTTP 504 on this endpoint
- multiple independent `OPTIONAL` blocks in one query, which produces a cartesian product instead of separate facts

**Execution:** `query_sparql`, `query_sparql_json`, `query_sparql_geojson`, `convert_rd_to_wgs84`

`query_sparql` returns readable text with classified error codes on failure. `query_sparql_json` returns raw SPARQL JSON for agents, tables, benchmarks and follow-up processing. `query_sparql_geojson` converts SELECT results with a WKT geometry variable into a GeoJSON FeatureCollection. `convert_rd_to_wgs84` converts a single RD New (EPSG:28992) coordinate pair to WGS84.

**Endpoints.** By default, queries go to the "Speedy" endpoint (standards-compliant SPARQL 1.1). If that endpoint is unreachable or returns a gateway-level error (502/503/504), `execute_sparql()` automatically retries once against the "Virtuoso" endpoint, which supports GeoSPARQL but has the query quirks listed above. Override with the `SPARQL_ENDPOINT` and `SPARQL_FALLBACK_ENDPOINT` environment variables.

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
