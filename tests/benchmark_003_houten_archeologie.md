# Vraag

Welke archeologische rijksmonumenten zijn er in de gemeente Houten?

## Verwachte modellering

Gemeente:
- resolve "Houten" via OWMS
- gebruik gemeente-URI
- gebruik heeftGemeente

Monumenttype:
- gebruik heeftMonumentAard
- gebruik SKOS label "archeologisch"

Niet gebruiken:
- locatienaam stringmatch
- functie "archeologie"

## Verwachte uitkomst

6 archeologische rijksmonumenten.

## Bekende fouten

- archeologie behandelen als functie
- zoeken op locatienaam
- omschrijving gebruiken als filter