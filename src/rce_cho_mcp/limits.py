"""Gedeelde afkap-limieten voor tools die een steekproef/lijst teruggeven.

Eén plek voor deze waarden zodat tools met een vergelijkbaar rij-gewicht niet
zonder duidelijke reden een andere maximum-limit hanteren.

LIST_MAX_LIMIT geldt voor tools die een lijst met lichte rijen teruggeven
(een object-URI plus een paar korte velden zoals naam/rijksmonumentnummer,
geen WKT of lange tekst): monumenten_in_gemeente() en
grootste_monumenten_oppervlakte() (area.py/gemeente.py). Tools met een ander
rij-gewicht hebben bewust een eigen grens: class_instance_counts() en
property_usage_counts() (stats.py) tonen alleen een class/property-URI plus
een telling -- lichter dan LIST_MAX_LIMIT, dus een hogere eigen grens
(1-1000); query_sparql() met geo:asWKT is juist zwaarder en krijgt een eigen,
veel lagere grens (zie validator.py's _SAFE_WKT_LIMIT).
"""

LIST_MAX_LIMIT = 200
