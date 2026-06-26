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

### 7. Execution

Voert SPARQL-query's uit op het RCE CHO endpoint.

Huidige tools:

- `query_sparql`

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