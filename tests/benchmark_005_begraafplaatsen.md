```md
# Benchmark 005 - Rijksmonumentale begraafplaatsen

## Vraag

Hoeveel begraafplaatsen in Nederland zijn een rijksmonument?

## Uitbreidingsvraag

Wat verandert er wanneer ook kerkhoven worden meegenomen?

## Doel

Controleer of de client het verschil begrijpt tussen:

- gecontroleerde vocabulaire
- vrije tekst
- functies
- omschrijvingen

## Verwachte modellering

### Functie

Gebruik:

```text
ceo:heeftOorspronkelijkeFunctie
of
ceo:heeftHuidigeFunctie
↓
ceo:heeftFunctieNaam
↓
skos:prefLabel

Zoek op:

Begraafplaats
Kerkhof

en gerelateerde functieconcepten.

Juridische status

Gebruik:

ceo:heeftJuridischeStatus
↓
skos:prefLabel = "rijksmonument"
Omschrijving

Gebruik:

ceo:heeftOmschrijving
↓
ceo:omschrijving

uitsluitend als aanvullende bron.

Gebruik omschrijvingen niet als primaire telmethode.

Verwachte interpretatie

Een functierelatie is betrouwbaarder dan een tekstmatch in een omschrijving.

Bijvoorbeeld:

functie
→ hoge betrouwbaarheid
omschrijving
→ lage betrouwbaarheid

Een omschrijving kan verwijzen naar:

een nabijgelegen kerkhof
een verdwenen begraafplaats
een historisch gebruik
een niet beschermd onderdeel

zonder dat het object zelf een begraafplaats is.

Verwachte uitkomst

De functiebenadering levert een aanzienlijk lager maar betrouwbaarder aantal op dan de omschrijvingsbenadering.

Veelgemaakte fouten
zoeken in omschrijvingen in plaats van functies
functie en vrije tekst gelijk behandelen
resultaten uit verschillende objecttypen optellen
archeologische registraties meerekenen als rijksmonument
Belangrijk leerpunt

Gecontroleerde vocabulaire gaat vóór vrije tekst.