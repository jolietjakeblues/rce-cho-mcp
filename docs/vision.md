# Vision

## RCE Linked Data MCP

Version: 0.1 (Draft)

---

# Mission

The RCE Linked Data MCP project aims to make the Dutch Cultural Heritage Linked Data ecosystem accessible through natural language.

Instead of requiring users to understand SPARQL, RDF, ontologies and Linked Data, the project enables researchers, heritage professionals and the general public to ask questions in everyday language.

The MCP translates those questions into reliable Linked Data queries and presents the results in a human-friendly way.

---

# Why this project exists

The Rijksdienst voor het Cultureel Erfgoed publishes a growing collection of Linked Data resources.

These datasets are rich, well-structured and openly available, but they remain difficult to explore for many users.

This project lowers that barrier.

The goal is not to replace Linked Data.

The goal is to unlock Linked Data.

---

# A broader vision

The current implementation focuses on the Cultural Heritage Objects (CHO) dataset.

However, CHO is only the starting point.

The long-term vision is an intelligent assistant that can work across the complete Linked Data landscape of the RCE.

---

# Future data sources

Examples include, but are not limited to:

## Cultural Heritage Objects (CHO)

* Rijksmonumenten
* Complexen
* Archeologie
* Werelderfgoed
* Beschermde gezichten

---

## RCE Image Bank

Natural language access to photographs, drawings, maps and other visual material.

Examples:

* Show photographs of windmills in Friesland.
* Find aerial photographs of fortified towns.
* Show images related to a specific monument.

---

## RCE Library

Natural language search through books, reports and publications.

Examples:

* Which books discuss Roman archaeology in Limburg?
* Find publications about restoration techniques.
* Show reports related to a monument.

---

## Historic GIS and Geometry

Support for geometry datasets and spatial reasoning.

Examples:

* Which monuments are located within this protected area?
* Show monuments within 500 metres of a church.
* Which archaeological sites intersect this municipality?

---

## Future RCE Linked Data datasets

The architecture should support additional datasets without redesigning the system.

Adding a new dataset should primarily involve adding a new ontology module and new query patterns.

---

# Design philosophy

The project is built around three principles.

## Knowledge

The assistant understands the meaning of heritage concepts rather than matching keywords.

---

## Transparency

Every answer should be traceable to Linked Data.

Generated SPARQL should always be inspectable.

The reasoning process should be understandable.

---

## Reusability

The architecture should not be tied to a single dataset.

It should become a reusable framework for cultural heritage Linked Data.

---

# Users

The project is intended for:

* heritage professionals
* researchers
* librarians
* archaeologists
* GIS specialists
* information managers
* Linked Data specialists
* software developers
* educators
* students

No prior knowledge of SPARQL should be required.

---

# Long-term architecture

The MCP should evolve from a single-dataset assistant into a modular platform.

```text
Natural language

↓

Intent detection

↓

Dataset selection

↓

Ontology selection

↓

Query planning

↓

SPARQL generation

↓

Validation

↓

Execution

↓

Result enrichment

↓

Natural language response
```

Each dataset contributes its own ontology module while sharing the same planning and execution pipeline.

---

# Beyond querying

The project should eventually support more than search.

Examples include:

* comparing datasets
* combining results from multiple datasets
* generating timelines
* spatial analysis
* discovering relationships
* suggesting related heritage objects
* connecting publications, images and monuments
* exporting reusable Linked Data queries

---

# Open Source

The project is developed in the open.

Goals include:

* transparent development
* reusable components
* comprehensive documentation
* benchmark-driven quality
* community contributions

The project welcomes contributions from developers, Linked Data specialists and cultural heritage professionals.

---

# Independence

This project is an independent open-source initiative.

It is not an official product of the Rijksdienst voor het Cultureel Erfgoed.

It builds upon publicly available Linked Data and open standards including RDF, SPARQL, SKOS, OWL and the Model Context Protocol (MCP).

---

# Long-term goal

The ultimate goal is to build the reference open-source AI interface for Dutch cultural heritage Linked Data.

Rather than creating an assistant for a single dataset, the project aims to provide a reusable architecture capable of connecting language models to the complete Linked Data ecosystem of the Rijksdienst voor het Cultureel Erfgoed.

As new datasets become available, they should become accessible by adding knowledge, not by redesigning the system.
