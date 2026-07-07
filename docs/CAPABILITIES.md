# RCE CHO MCP Capabilities

## Doel

Het doel van `rce-cho-mcp` is niet om Nederlandse vragen zelf te beantwoorden.

Het doel is een generieke open source MCP-server te bieden waarmee LLM-clients betrouwbaar de RCE Linked Data kunnen raadplegen.

De server biedt capabilities voor:

- CEO-ontologie
- thesauri en SKOS-concepten
- dataset-semantiek
- named graph kennis
- URI-resolutie
- SPARQL-validatie
- SPARQL-executie

Een client, zoals Claude Desktop, ChatGPT, Gemini, Cursor, VS Code of een Python-script, bepaalt zelf hoe deze capabilities worden gecombineerd.

## Linked Data-model

De server gaat uit van het Linked Data-model van de RCE-data.

Belangrijke uitgangspunten:

- objecten staan in datasetgraphs
- betekenissen staan vaak in thesauri
- labels staan meestal op SKOS-concepten, niet op erfgoedobjecten zelf
- menselijke woorden moeten eerst naar concept-URI's worden vertaald
- concept-URI's worden daarna gebruikt in SPARQL-query's
- relevante triples kunnen verspreid zijn over meerdere named graphs

Voorbeeld:

```text
menselijke term
    ↓
SKOS prefLabel / altLabel
    ↓
concept URI
    ↓
SPARQL filter
    ↓
erfgoedobjecten
```

Belangrijke ontwerpregel:

```text
Labels en namen zijn meestal presentatie.
Concepten, types en relaties zijn selectiecriteria.
```

## Capabilitygroepen

### 1. Discovery

Helpt een client ontdekken wat beschikbaar is.

Huidige tools:

- `ping`
- `graphs_list`
- `ontology_statistics`
- `ontology_search`

### 2. Ontology

Geeft kennis over het datamodel.

Huidige tools:

- `ontology_describe_class`
- `ontology_describe_property`

Voorbeelden:

- Welke properties horen bij `Rijksmonument`?
- Welke classes bevatten het woord `Adres`?
- Welke properties hebben `Gemeente` in hun label?

### 3. Dataset semantics

Geeft interpretatieregels voor belangrijke RCE-datapatronen.

Ontology zegt wat er bestaat.  
Dataset semantics zegt wat belangrijk is bij interpretatie.

Huidige tools:

- `semantics_list_topics`
- `semantics_describe_topic`

Huidige topics:

- `functions`
- `legal_status`
- `monument_aard`
- `names`
- `descriptions`
- `identifiers`
- `addresses`
- `geometry`

Belangrijke patronen:

```text
Functie:
ceo:heeftOorspronkelijkeFunctie / ceo:heeftHuidigeFunctie
    ↓
ceo:heeftFunctieNaam
    ↓
skos:prefLabel
```

```text
Juridische status:
ceo:heeftJuridischeStatus
    ↓
skos:prefLabel
```

```text
Monumentaard:
ceo:heeftMonumentAard
    ↓
skos:prefLabel
```

```text
Naam:
ceo:heeftNaam
    ↓
ceo:naam
```

```text
Omschrijving:
ceo:heeftOmschrijving
    ↓
ceo:omschrijving
```

Belangrijke regel:

```text
Gebruik ceo:registergegeven niet als juridische status.
Juridische status loopt via ceo:heeftJuridischeStatus en skos:prefLabel.
```

### 4. Graphs

Geeft kennis over named graphs in het CHO-KENNIS endpoint.

Huidige tools:

- `graphs_list`

Deze capability helpt clients bepalen wanneer een `FROM` of `GRAPH` nuttig is en wanneer een cross-graph query nodig kan zijn.

Belangrijke regel:

```text
Gebruik FROM of GRAPH alleen wanneer je zeker weet in welke named graph de relevante triples staan.
Bij relaties over meerdere graphs kan een query zonder graphrestrictie correct zijn.
```

### 5. Resolver

Lost labels op naar URI's zonder zelf domeinkeuzes te maken.

Huidige tools:

- `resolve_concept_label`
- `describe_resource_uri`

Voorbeeld:

```text
Utrecht
↓
http://standaarden.overheid.nl/owms/terms/Utrecht_(gemeente)
http://standaarden.overheid.nl/owms/terms/Utrecht_(provincie)
↓
client kiest welke URI relevant is
```

Ontwerpprincipe:

De resolver kiest nooit zelf tussen meerdere resultaten.

### 6. Validator

Controleert SPARQL-query's op bekende valkuilen.

Huidige tools:

- `validate_query`
- `validate_query_structured`

Voorbeelden van controles:
- verdachte prefixes
- onjuiste `SELECT/FROM/WHERE` volgorde
- ontbreken van `DISTINCT`
- `COUNT` zonder alias
- query zonder `FROM` of `GRAPH` als waarschuwing, niet als fout
- gebruik van `skos:prefLabel`-gebonden variabelen in FILTER zonder `STR()` (stille nul-resultaten)
- GeoSPARQL-relaties die structureel timeout veroorzaken op Virtuoso (`geof:sfWithin` e.d.)
- `GROUP BY` op lange tekstvelden (`ceo:omschrijving`, `ceo:naam`) die Virtuoso-overflowfouten geven
- `ORDER BY` gecombineerd met `OPTIONAL`-joins (veroorzaakt consistent een HTTP 504, ook met kleine `LIMIT`)
- meerdere onafhankelijke multi-valued `OPTIONAL`-blokken in dezelfde query (cartesisch product)
- `ceo:huisnummer` / `ceo:perceelnummer` met een kaal getal-literal i.p.v. een gequote string (stille nul-resultaten)

### 7. Execution

Voert SPARQL-query's uit op het RCE CHO endpoint.

Huidige tools:

- `query_sparql`
- `query_sparql_json`
- `query_sparql_geojson`
- `convert_rd_to_wgs84`

`query_sparql` geeft leesbare tekst terug.
`query_sparql_json` geeft het ruwe SPARQL JSON-resultaat terug voor agents en vervolgverwerking.
`query_sparql_geojson` zet SELECT-resultaten met een WKT-geometrievariabele om naar een GeoJSON FeatureCollection.
`convert_rd_to_wgs84` zet een los RD New (EPSG:28992) coördinatenpaar om naar WGS84.

Voorbeeld:

```text
SPARQL query
    ↓
query_sparql()
    ↓
SPARQL endpoint
    ↓
JSON resultaat
```

Bij fouten classificeert `query_sparql` de foutmelding:

- `TIMEOUT` — query afgebroken wegens tijdslimiet (ook een kale HTTP 504 zonder 'timeout' in de body)
- `GROUPBY_OVERFLOW` — Virtuoso kan lange tekstvelden niet groeperen
- `SYNTAX` — SPARQL-syntaxfout
- `ENDPOINT_UNAVAILABLE` — endpoint tijdelijk niet bereikbaar

Elke foutcode wordt vergezeld van een concreet advies voor de vervolgstap.

Requests naar het endpoint gaan via POST (query in de body), niet via GET:
een query met een grote `VALUES`-clause (>~300-500 URI's, querystring
>~30-40KB) laat GET falen met HTTP 431 "Request Header Fields Too Large".
POST is getest tot ~255KB / ~3000 URI's zonder problemen.

### Endpoints: default en fallback

Queries gaan standaard naar het "Speedy"-endpoint (standaardconforme
SPARQL 1.1). Is dat endpoint onbereikbaar of geeft het een gateway-fout
(502/503/504), dan probeert `execute_sparql()` automatisch één keer opnieuw
via het "Virtuoso"-endpoint — dat wel GeoSPARQL ondersteunt, maar de hierboven
genoemde eigenaardigheden heeft (GROUP BY-overflow, ORDER BY+OPTIONAL 504's,
geof:sfWithin-timeouts). Een queryfout (bv. een syntaxfout, 4xx) triggert geen
fallback, omdat dezelfde query daar identiek zou falen. Overschrijfbaar via de
omgevingsvariabelen `SPARQL_ENDPOINT` en `SPARQL_FALLBACK_ENDPOINT`.

## Bekende performance- en datakwaliteitskenmerken

- **Query-resultaat-caching**: het endpoint lijkt te cachen op exacte
  querytekst. Een letterlijk identieke herhaling van een eerdere query komt
  vrijwel instant terug (~0,2s); een nieuwe combinatie van patroon/`LIMIT`/
  `OFFSET` kost stelselmatig ~13-15s, ongeacht de `OFFSET`-grootte of
  joincomplexiteit. Voor interactief gebruik betekent dit: de eerste keer dat
  een client een nieuwe vraag stelt is trager dan een herhaalde/geïtereerde vraag.
- **Duplicaat-triples in de brondata**: dezelfde relatie-triple kan meerdere
  keren voorkomen (bevestigd: 116x dezelfde BRK-relatie op één monument).
  Tellingen en lijsten zonder `DISTINCT`/dedup kunnen hierdoor sterk vertekend
  zijn. Test nieuwe verzamel-achtige queries niet alleen op een klein
  eerste-resultaat, maar ook op een entiteit waarvan bekend is dat die
  meerdere relaties van hetzelfde type heeft.

## Belangrijk ontwerpprincipe

De MCP-server bevat zo min mogelijk hardgecodeerde kennis.

Voorkeur:

```text
Linked Data
    ↓
resolver
    ↓
URI
    ↓
query
```

Niet:

```text
Python dictionary
    ↓
query
```

Alleen wanneer de Linked Data onvoldoende informatie biedt, mag kennis in Python worden vastgelegd. Dit moet dan expliciet gedocumenteerd worden.

## Wat deze server niet doet

Deze server is niet verantwoordelijk voor:

- natuurlijke taal begrijpen
- conversaties voeren
- redeneerstrategieën kiezen
- UI maken
- kaarten maken
- rapportages maken
- vaste use-cases hardcoderen
- queryplanning

Dat is de verantwoordelijkheid van de client of van een aparte reference implementation.

## Toekomstige capabilities

Mogelijke uitbreidingen:

- `search_concepts`
- `list_prefixes`
- `structured_results`
- `structured_ontology`
- `python_sdk`
- `rest_api`

Nieuwe capabilities worden alleen toegevoegd wanneer ze generiek bruikbaar zijn voor meerdere clients.

## Samenvatting

De MCP levert bouwstenen.

De client combineert deze bouwstenen.

```text
ontology
    ↓
semantics
    ↓
graphs
    ↓
resolver
    ↓
validator
    ↓
execution
```

Niet:

```text
natuurlijke taal
    ↓
magische query builder
    ↓
antwoord
```

Dat onderscheid is het belangrijkste ontwerpprincipe van het project.
