"""Herbruikbare SPARQL-querybouwer voor het tweetraps-subquery-patroon.

area.py (largest_by_area) en gemeente.py (monumenten_in_gemeente) bouwden dit
patroon elk met de hand op: een binnenste SELECT DISTINCT die filtert/
sorteert/limiteert zonder OPTIONAL, en een buitenste query die daarna
naam en rijksmonumentnummer toevoegt via OPTIONAL op de al-beperkte
kandidatenset. Dat vermijdt de bekende ORDER BY + OPTIONAL-504-valkuil op
dit endpoint (zie pitfalls.TWO_STAGE_SUBQUERY_REMEDY): de duurdere
OPTIONAL-joins draaien hier alleen nog over de kandidatenset die de
binnenste subquery al heeft geselecteerd, niet over de volledige,
ongefilterde resultatenset.

Dit bouwt alleen de buitenste schil; de binnenste { SELECT ... } blijft
specifiek per aanroeper (de filters verschillen te veel om zinvol te
generaliseren).
"""

CEO_PREFIX = "PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>"


def build_name_lookup_query(
    outer_vars: str,
    inner_select: str,
    subject_var: str,
    extra_prefixes: str = "",
    outer_order_by: str = "",
) -> str:
    """Wrap een kant-en-klare binnenste subquery met de standaard
    rijksmonumentnummer/naam-OPTIONALs, in de buitenste query.

    outer_vars: SELECT-variabelen van de buitenste query, als SPARQL-tekst
    (bv. "?rm ?opp ?naam ?rijksmonumentnummer").
    inner_select: de volledige binnenste "{ SELECT ... WHERE { ... } ... }"
    als kant-en-klare SPARQL-tekst (zonder OPTIONAL); de aanroeper bouwt dit
    zelf op, inclusief zijn eigen filters en eventuele ORDER BY/LIMIT.
    subject_var: naam van de subjectvariabele in de kandidatenset (zonder
    voorloop-"?", bv. "rm" of "obj") waarop de naam/nummer-OPTIONALs joinen.
    extra_prefixes: optionele extra PREFIX-regels (bv. voor geo:/geof:/uom:)
    naast het altijd toegevoegde ceo:-prefix.
    outer_order_by: optionele ORDER BY-clausule voor de buitenste query (bv.
    "ORDER BY DESC(?opp)"); nodig wanneer de buitenste query, net als de
    binnenste, ook weer op de berekende sorteerwaarde moet sorteren.
    """
    prefixes = CEO_PREFIX if not extra_prefixes else f"{extra_prefixes}\n{CEO_PREFIX}"
    return f"""
{prefixes}
SELECT DISTINCT {outer_vars} WHERE {{
  {inner_select}
  OPTIONAL {{ ?{subject_var} ceo:rijksmonumentnummer ?rijksmonumentnummer . }}
  OPTIONAL {{ ?{subject_var} ceo:heeftNaam ?nObj . ?nObj ceo:naam ?naam . }}
}}
{outer_order_by}
"""
