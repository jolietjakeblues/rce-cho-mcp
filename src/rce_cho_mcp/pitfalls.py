"""Canonische Nederlandse waarschuwingsteksten voor terugkerende RCE CHO
SPARQL-valkuilen.

validator.py gebruikt deze als basis voor zijn automatische controles.
Andere modules (sparql.py, resolver.py, server.py, prompts.py) hergebruiken
dezelfde tekst in hun documentatie/foutmeldingen, zodat een toekomstige
aanpassing van de kernboodschap niet apart op elke plek moet worden
bijgehouden.
"""

LANGUAGE_TAG_WARNING = (
    'skos:prefLabel-waarden zijn taalgetagd (bv. "Zwolle"@nl). Een FILTER die '
    "een labelvariabele vergelijkt met een kale string (FILTER(?label = "
    '"Zwolle") of FILTER(?label IN (...))) geeft stil 0 resultaten, zonder '
    "fout. Gebruik resolve_concept_label() om eerst de concept-URI op te "
    "halen, of wrap de vergelijking in STR()."
)

TWO_STAGE_SUBQUERY_REMEDY = (
    "ORDER BY gecombineerd met OPTIONAL-joins veroorzaakt op dit endpoint "
    "consistent een HTTP 504 timeout, ook met een kleine LIMIT. Gebruik een "
    "tweetraps-subquery: sorteer/pagineer eerst goedkoop op een enkele "
    "variabele in een binnenste SELECT DISTINCT, en voeg de duurdere "
    "OPTIONAL-joins pas toe in de buitenste query op de al-beperkte set."
)

CARTESIAN_PRODUCT_WARNING = (
    "Meerdere onafhankelijke multi-valued OPTIONAL-blokken in dezelfde query "
    "(bv. meerdere BRK-percelen EN meerdere BAG-adressen) leveren een "
    "cartesisch product op (aantal_a x aantal_b rijen i.p.v. aantal_a + "
    "aantal_b losse feiten), inclusief onzinnige combinaties. Haal "
    "multi-valued relaties die niet inherent aan elkaar gekoppeld zijn op in "
    "aparte queries (evt. met een gedeelde VALUES-clause) en combineer ze in "
    "code, niet als losse OPTIONAL-blokken in dezelfde SELECT."
)
