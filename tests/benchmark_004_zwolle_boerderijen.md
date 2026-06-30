# Benchmark 004 - Rijksmonumentale boerderijen in Zwolle

## Vraag

Welke rijksmonumentale boerderijen staan er in de gemeente Zwolle?

## Doel

Controleer of de client het verschil begrijpt tussen:

- gemeente
- functie
- juridische status
- naam en omschrijving

## Verwachte modellering

### Gemeente

Gebruik:

```text
Zwolle
↓
OWMS concept
↓
ceo:heeftGemeente
OWMS concept
↓
ceo:heeftGemeente

Niet gebruiken:

ceo:locatienaam = "Zwolle"

behalve als fallback wanneer de gemeente-relatie ontbreekt.

Functie

Gebruik:

ceo:heeftOorspronkelijkeFunctie
↓
ceo:heeftFunctieNaam
↓
skos:prefLabel = "Boerderij"

of een gerelateerde boerderijfunctie.

Gebruik niet:

omschrijving
naam

als primaire selectie.

Juridische status

Gebruik:

ceo:heeftJuridischeStatus
↓
skos:prefLabel = "rijksmonument"
Verwachte uitkomst

Een lijst van rijksmonumentale boerderijen in Zwolle.

De exacte aantallen kunnen veranderen door mutaties in het register.

Veelgemaakte fouten
zoeken op locatienaam in plaats van gemeente
zoeken op omschrijving in plaats van functie
juridische status overslaan
boerderij afleiden uit vrije tekst
Belangrijk leerpunt

Boerderij is een functie.

Boerderij is geen monumentaard.