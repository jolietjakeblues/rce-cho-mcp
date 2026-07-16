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
- `rest_api_wrappers`
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

### 5b. Conceptzoeken (NDE Termennetwerk)

Zoekt SKOS-concepten op natuurlijke taal, met synoniemen en verwante termen,
over gepubliceerde thesauri (via de publieke, auth-vrije GraphQL-API van het
NDE Termennetwerk) — een aanvulling op de resolver, niet een vervanging.

Huidige tools:

- `zoek_concept_termennetwerk`
- `lookup_termennetwerk_uri`

Verschil met `resolve_concept_label`:

```text
resolve_concept_label:
  exacte skos:prefLabel-match, alleen binnen onze eigen named graphs
  → vereist dat je de precieze schrijfwijze al kent

zoek_concept_termennetwerk:
  relevantie-gerangschikt, matcht ook altLabel-synoniemen
  → toont broader/narrower-termen
  → doorzoekt ook externe bronnen (Wikidata, AAT) naast CHT/ABR
```

`lookup_termennetwerk_uri` vertaalt een bekende externe concept-URI (bv. een
`skos:exactMatch` naar Wikidata, gevonden via `describe_resource_uri`) terug
naar een leesbaar label.

Standaardbronnen: CHT en ABR (de RCE-thesauri). Andere bronnen via de
`sources`-parameter (`wikidata`, `aat`, of een volledige bron-URI).

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

### 8. Statistics

Geeft live cijfers over de actuele dataset, in plaats van wat de
ontologie-definitie beweert te bevatten.

Huidige tools:

- `dataset_statistics` — triples, entiteiten, klassen en properties in gebruik
- `class_instance_counts` — aantal instanties per klasse
- `property_usage_counts` — aantal triples per property

```text
ontology_statistics():
  telt wat de ontologie DEFINIEERT (statisch, uit CEO_RCE.ttl)

dataset_statistics() / class_instance_counts() / property_usage_counts():
  telt wat er FEITELIJK in de dataset staat (live, dagelijks ververst)
```

Een klasse of property die de ontologie kent maar die hier ontbreekt of op 0
staat, bevat geen instanties in de live data — belangrijk om te weten vóórdat
een query op die klasse wordt opgesteld.

Dit zijn full-dataset scans (~58 miljoen triples zonder `GRAPH`-restrictie,
dat is de hele dataset). Gemeten: `dataset_statistics` ~114s (vier
opeenvolgende scans), `property_usage_counts` ~57s, `class_instance_counts`
~21s.

### 9. Exploration

Ontdekt empirisch welke querypaden daadwerkelijk in de data bestaan, op basis
van een steekproef — onafhankelijk van wat de ontologie of dataset semantics
al documenteren.

Huidige tools:

- `explore_class` — welke predicaten vertrekken vanaf een klasse, en waar ze naartoe leiden (doelklasse of datatype)
- `explore_incoming` — welke klassen en predicaten verwijzen náár een klasse (de omgekeerde richting)

Voorbeeld:

```text
explore_incoming(ceo:Rijksmonument):
  ceo:Complex --heeftRijksmonument--> ceo:Rijksmonument
  ceo:Kennisregistratie --heeftBetrekkingOp--> ceo:Rijksmonument
```

Nuttig voor vragen waarvan het pad nog niet in `semantics_describe_topic()`
of de workflow-instructies staat, of om te verifiëren of een in de ontologie
gedeclareerd pad ook daadwerkelijk gevuld is. De getoonde aantallen gelden
alleen binnen de steekproef, niet voor de hele dataset. Snel (steekproef,
geen full-dataset scan): enkele seconden.

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
- **Monument-URI's zijn niet opgebouwd uit het rijksmonumentnummer**: het
  numerieke deel in `.../rijksmonument/{N}` is het interne
  `cultuurhistorischObjectnummer`, niet `ceo:rijksmonumentnummer` — deze twee
  nummers verschillen meestal. Bevestigd: `ceo:rijksmonumentnummer "16388"`
  hoort bij `.../rijksmonument/31287`, terwijl `.../rijksmonument/16388` zelf
  bestaat maar `cultuurhistorischObjectnummer "16388"` en
  `rijksmonumentnummer "21625"` heeft. Een zelf opgebouwde URI faalt hier niet
  met een foutmelding — hij levert stilzwijgend het verkeerde monument.
  Filter altijd op `ceo:rijksmonumentnummer` en laat de query de URI opzoeken.

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

- `list_prefixes`
- `structured_results`
- `structured_ontology`
- `python_sdk`
- `rest_api`

(`search_concepts` is inmiddels gebouwd als `zoek_concept_termennetwerk`, zie
capabilitygroep 5b.)

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
