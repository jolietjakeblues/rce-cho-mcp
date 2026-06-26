# RCE CHO MCP Capabilities

## Doel

Het doel van `rce-cho-mcp` is niet om Nederlandse vragen zelf te beantwoorden.

Het doel is een generieke open source MCP-server te bieden waarmee LLM-clients betrouwbaar de RCE Linked Data kunnen raadplegen.

De server biedt capabilities voor:

- CEO-ontologie
- OWMS en SKOS-concepten
- URI-resolutie
- SPARQL-validatie
- SPARQL-executie

Een client, zoals Claude Desktop, ChatGPT, Gemini, Cursor, VS Code of een Python-script, bepaalt zelf hoe deze capabilities worden gecombineerd.

---

## Architectuur

```text
                 LLM client
                     │
              MCP protocol
                     │
          rce-cho-mcp server
                     │
     ┌───────────────┼────────────────┐
     │               │                │
 Ontology         Resolver        Query tools
     │               │                │
     └───────────────┼────────────────┘
                     │
              RCE CHO SPARQL endpoint
```

---

## Capabilitygroepen

### 1. Discovery

Helpt een client ontdekken wat beschikbaar is.

Huidige tools:

- `ping`
- `ontology_statistics`
- `ontology_search`

---

### 2. Ontology

Geeft kennis over het datamodel.

Huidige tools:

- `ontology_describe_class`
- `ontology_describe_property`

Voorbeelden:

- Welke properties horen bij `Rijksmonument`?
- Welke classes bevatten het woord `Adres`?
- Welke properties hebben `Gemeente` in hun label?

---

### 3. Resolver

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

---

### 4. Validator

Controleert SPARQL-query's op bekende valkuilen.

Huidige tools:

- `validate_query`
- `validate_query_structured`

Voorbeelden van controles:

- verboden prefixes
- onjuiste `SELECT/FROM/WHERE` volgorde
- ontbreken van `DISTINCT`
- gebruik van bekende foutieve properties

---

### 5. Execution

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

---

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

Alleen wanneer de Linked Data onvoldoende informatie biedt, mag kennis in Python worden vastgelegd.

---

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

---

## Toekomstige capabilities

Mogelijke uitbreidingen:

- `list_graphs`
- `list_prefixes`
- `structured_results`
- `structured_ontology`
- `python_sdk`
- `rest_api`

Nieuwe capabilities worden alleen toegevoegd wanneer ze generiek bruikbaar zijn voor meerdere clients.

---

## Voorbeelden van clients

Deze architectuur maakt gebruik mogelijk vanuit onder andere:

- Claude Desktop
- ChatGPT
- Gemini
- LM Studio
- VS Code
- Cursor
- Windsurf
- Python
- LangChain
- LlamaIndex

---

## Samenvatting

De MCP levert bouwstenen.

De client combineert deze bouwstenen.

```text
ontology
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