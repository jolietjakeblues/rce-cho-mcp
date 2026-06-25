Ja. Dit is precies het goede moment om te stoppen met coderen en de architectuur vast te leggen.

Sterker nog: dit document gaat waarschijnlijk belangrijker worden dan een groot deel van de Python-code.

Ik zou **niet** beginnen met tools opsommen, maar met de visie.

Mijn voorstel:

```text
docs/
    CAPABILITIES.md
```

Inhoud:

---

# RCE CHO MCP Capabilities

## Doel

Het doel van rce-cho-mcp is niet om Nederlandse vragen te beantwoorden.

Het doel is een generieke open source MCP-server te bieden waarmee LLM's betrouwbaar de RCE Linked Data kunnen raadplegen.

De server bevat domeinkennis over:

* de CEO-ontologie
* OWMS
* SKOS-concepten
* SPARQL-validatie
* query-executie

Een client (Claude, ChatGPT, Gemini, Cursor, VS Code, Python, REST API) bepaalt zelf hoe deze capabilities worden gecombineerd.

---

# Architectuur

```text
                 LLM
                  │
          MCP protocol
                  │
        rce-cho-mcp server
                  │
     ┌────────────┼─────────────┐
     │            │             │
 Ontology     Resolver      Query Engine
     │            │             │
     └────────────┼─────────────┘
                  │
            SPARQL endpoint
```

---

# Capabilitygroepen

## 1. Ontology

Geeft kennis over het datamodel.

Mogelijke tools

* get_ontology_context()
* search_classes()
* describe_class()
* search_properties()
* describe_property()

---

## 2. Resolver

Lost labels op naar URI's.

Voorbeelden

```
Zeist
↓
OWMS URI
```

```
kerk
↓
SKOS concept
```

```
Rijksmuseum
↓
CHO URI
```

Mogelijke tools

* resolve_label()
* resolve_uri()
* search_concepts()

---

## 3. Query Builder

Helpt bij het maken van correcte SPARQL.

Mogelijke tools

* build_query()
* explain_query()

---

## 4. Validator

Controleert queries.

Mogelijke tools

* validate_query()

---

## 5. Execution

Voert queries uit.

Mogelijke tools

* execute_query()
* describe_resource()

---

## 6. Discovery

Helpt een client ontdekken wat beschikbaar is.

Mogelijke tools

* list_graphs()
* list_datasets()
* examples()
* benchmark()

---

# Belangrijk ontwerpprincipe

De MCP-server bevat zo min mogelijk hardgecodeerde kennis.

Voorkeur:

```
Linked Data
      ↓
resolver
      ↓
URI
      ↓
query
```

Niet:

```
Python dictionary
      ↓
query
```

Alleen wanneer de Linked Data onvoldoende informatie biedt, mag kennis in Python worden vastgelegd.

---

# Niet de verantwoordelijkheid van deze server

Deze server is niet verantwoordelijk voor:

* natuurlijke taal begrijpen
* conversaties voeren
* redeneerstrategieën
* UI
* rapportages

Dat is de taak van de client.

---

## Toekomst

Deze architectuur maakt clients mogelijk zoals:

* Claude Desktop
* ChatGPT
* Gemini
* VS Code
* Cursor
* Windsurf
* Python SDK
* REST API
* LangChain
* LlamaIndex

---