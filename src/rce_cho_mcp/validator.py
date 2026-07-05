import re

from rce_cho_mcp.config import DEFAULT_DATASET_GRAPH


FORBIDDEN_PREFIXES = [
    "ceosp:",
    "ceox:",
]

FORBIDDEN_LANGUAGE_FILTERS = [
    "lang(",
    "LANG(",
    "LANGMATCHES(",
    "langmatches(",
]

# Matches "skos:prefLabel ?varname", used to find variables bound to a
# (likely language-tagged) label literal.
LABEL_BINDING_PATTERN = re.compile(
    r"skos:prefLabel\s+\?(\w+)",
    re.IGNORECASE,
)

# Matches "FILTER(...)" blocks so we can inspect their contents in isolation.
FILTER_BLOCK_PATTERN = re.compile(
    r"FILTER\s*\((.*?)\)\s*(?=\.|\}|FILTER|$)",
    re.IGNORECASE | re.DOTALL,
)

# Detecteer GROUP BY in combinatie met variabelen die gebonden zijn via
# omschrijving- of naam-paden (lange tekstvelden die Virtuoso niet kan groeperen).
LONG_TEXT_BINDINGS = re.compile(
    r"ceo:(?:heeftOmschrijving|omschrijving|heeftNaam|naam)\s+\?(\w+)",
    re.IGNORECASE,
)

GEOSPARQL_RELATIONS = re.compile(
    r"geof:(?:sfWithin|sfContains|sfIntersects|sfOverlaps|sfTouches|sfCrosses)",
    re.IGNORECASE,
)

OPTIONAL_BLOCK_PATTERN = re.compile(r"\bOPTIONAL\b", re.IGNORECASE)

# Properties die in deze dataset ongetypeerde string-literals zijn (bv. "19"),
# geen xsd:integer. Een kaal getal (ceo:huisnummer 19) matcht dan niets en
# geeft stil 0 resultaten, net als het skos:prefLabel-taalfilter-probleem hieronder.
UNTYPED_STRING_PROPERTIES = ("huisnummer", "perceelnummer")
UNTYPED_NUMERIC_LITERAL_PATTERN = re.compile(
    r"ceo:(" + "|".join(UNTYPED_STRING_PROPERTIES) + r")\s+(\d+)\b",
    re.IGNORECASE,
)


def _find_order_by_optional_timeout_risk(query: str) -> list[str]:
    """Detecteer ORDER BY gecombineerd met OPTIONAL-joins.

    Bevestigd (2026-07): dit combinatiepatroon veroorzaakt consistent een
    HTTP 504 op het Virtuoso-endpoint, zelfs met een kleine LIMIT -- de
    triplestore lijkt eerst de volledige gejoinde resultatenset te sorteren
    voordat LIMIT/OFFSET wordt toegepast.
    """
    if "ORDER BY" not in query.upper():
        return []
    if not OPTIONAL_BLOCK_PATTERN.search(query):
        return []
    return [
        "ORDER BY gecombineerd met OPTIONAL-joins veroorzaakt op dit endpoint "
        "consistent een HTTP 504 timeout, ook met een kleine LIMIT. Gebruik een "
        "tweetraps-subquery: sorteer/pagineer eerst goedkoop op een enkele "
        "variabele in een binnenste SELECT DISTINCT, en voeg de duurdere "
        "OPTIONAL-joins pas toe in de buitenste query op de al-beperkte set."
    ]


def _find_cartesian_product_risk(query: str) -> list[str]:
    """Detecteer meerdere onafhankelijke OPTIONAL-blokken in dezelfde query.

    Bevestigd (2026-07): twee of meer multi-valued OPTIONAL-blokken in
    dezelfde WHERE leveren een cartesisch product op (bv. 5 relaties x 3
    relaties = 15 rijen i.p.v. de werkelijke 5+3=8 losse feiten), inclusief
    onzinnige combinaties tussen de twee relaties. Dit valt niet op bij een
    klein testresultaat en wordt pas zichtbaar bij entiteiten met echt
    meerdere relaties van beide soorten.
    """
    count = len(OPTIONAL_BLOCK_PATTERN.findall(query))
    if count < 2:
        return []
    return [
        f"{count} OPTIONAL-blokken gevonden in dezelfde query. Als dit "
        "onafhankelijke multi-valued relaties zijn (bv. meerdere BRK-percelen "
        "EN meerdere BAG-adressen), levert dit een cartesisch product op "
        "(aantal_a x aantal_b rijen i.p.v. aantal_a + aantal_b losse feiten), "
        "inclusief onzinnige combinaties. Haal multi-valued relaties die niet "
        "inherent aan elkaar gekoppeld zijn op in aparte queries (evt. met een "
        "gedeelde VALUES-clause) en combineer ze in code, niet als losse "
        "OPTIONAL-blokken in dezelfde SELECT."
    ]


def _find_untyped_numeric_literal_risk(query: str) -> list[str]:
    """Detecteer een kaal getal-literal bij properties die in deze dataset
    ongetypeerde string-literals zijn (bv. ceo:huisnummer "19", geen
    ceo:huisnummer 19). Een numerieke vergelijking matcht hier stil niets,
    zonder foutmelding -- net zo verraderlijk als het taalgetagde-labelfilter-
    probleem hierboven."""
    warnings = []
    seen = set()
    for match in UNTYPED_NUMERIC_LITERAL_PATTERN.finditer(query):
        prop = match.group(1).lower()
        if prop in seen:
            continue
        seen.add(prop)
        warnings.append(
            f"ceo:{prop} gebruikt met een kaal getal ({match.group(2)}). "
            f"ceo:{prop} is in deze data een ongetypeerd string-literal, geen "
            f'xsd:integer. Gebruik ceo:{prop} "{match.group(2)}" (met '
            "aanhalingstekens) -- zonder aanhalingstekens matcht de query stil "
            "niets, ook als het object gegarandeerd bestaat."
        )
    return warnings


def _find_geosparql_timeout_risk(query: str) -> list[str]:
    """Detecteer GeoSPARQL-relaties die structureel timeout veroorzaken op Virtuoso."""
    matches = GEOSPARQL_RELATIONS.findall(query)
    if not matches:
        return []
    found = ", ".join(set(matches))
    return [
        f"Gevonden: {found}. Ruimtelijke joins met geof:sfWithin e.d. lopen "
        "structureel vast op dit Virtuoso-endpoint (timeout). "
        "Gebruik een tweetraps-aanpak: haal WKT-geometrieën eerst op via query_sparql(), "
        "voer de ruimtelijke join daarna lokaal uit (bijv. met Shapely in Python). "
        "Zie ook: semantics_describe_topic('geometry')."
    ]

def _find_groupby_overflow_risk(query: str) -> list[str]:
    """Detecteer GROUP BY met lange tekstvelden die Virtuoso niet kan verwerken."""
    if "GROUP BY" not in query.upper():
        return []

    risky_vars = set(LONG_TEXT_BINDINGS.findall(query))
    if not risky_vars:
        return []

    warnings = []
    for var in risky_vars:
        groupby_pattern = re.compile(rf"GROUP\s+BY\b.*\?{re.escape(var)}\b", re.IGNORECASE | re.DOTALL)
        if groupby_pattern.search(query):
            warnings.append(
                f"?{var} is gebonden via een omschrijving- of naampad en staat in GROUP BY. "
                "Virtuoso geeft hier de fout 'Value of ANY type column too long'. "
                f"Herschrijf: haal ?{var} op buiten de GROUP BY via een subquery op twee niveaus."
            )
    return warnings

def _find_unsafe_label_filters(query: str) -> list[str]:
    """Detect FILTER expressions that compare a skos:prefLabel-bound
    variable directly to a string literal, without STR().

    Labels in this dataset are frequently language-tagged (e.g. "Zwolle"@nl).
    Comparing such a variable to a plain string in a FILTER (e.g.
    FILTER(?label = "Zwolle") or FILTER(?label IN ("Zwolle", "Amersfoort")))
    does not match the language-tagged RDF term and silently returns zero
    results, with no error. Wrapping in STR(), or resolving the label to a
    URI first via resolve_concept_label(), avoids this.
    """
    label_vars = set(LABEL_BINDING_PATTERN.findall(query))

    if not label_vars:
        return []

    warnings: list[str] = []

    for filter_body in FILTER_BLOCK_PATTERN.findall(query):
        for var in label_vars:
            var_pattern = re.compile(rf"\?{re.escape(var)}\b")

            if not var_pattern.search(filter_body):
                continue

            # If STR() already wraps the variable somewhere in this filter,
            # treat it as safe.
            str_wrapped = re.search(
                rf"STR\s*\(\s*\?{re.escape(var)}\s*\)", filter_body, re.IGNORECASE
            )

            if str_wrapped:
                continue

            warnings.append(
                f"FILTER gebruikt ?{var}, dat gebonden is via skos:prefLabel, "
                "zonder STR(). Labels zijn vaak taalgetagd (bv. \"Zwolle\"@nl); "
                f"een vergelijking als FILTER(?{var} = \"...\") of "
                f"FILTER(?{var} IN (...)) matcht dan niets en geeft stil 0 "
                f"resultaten. Gebruik STR(?{var}) = \"...\", of resolveer het "
                "label eerst naar een URI met resolve_concept_label() en "
                "filter/join op die URI in plaats van op de labeltekst."
            )

    return warnings


def validate_sparql(query: str) -> dict:
    """Validate a SPARQL query against known RCE CHO pitfalls.

    This validator does not validate domain classes or properties.
    Use ontology tools for that.
    """
    errors: list[str] = []
    warnings: list[str] = []

    q = query
    q_upper = q.upper()

    for prefix in FORBIDDEN_PREFIXES:
        if prefix in q:
            warnings.append(
                f"Verdachte prefix gevonden: {prefix}. "
                "Controleer met ontology_search() of deze prefix echt bestaat."
            )

    for term in FORBIDDEN_LANGUAGE_FILTERS:
        if term in q:
            warnings.append(
                f"Taalfilter gevonden: {term}. "
                "Controleer of labels in deze data daadwerkelijk taalgetagd zijn."
            )

    warnings.extend(_find_unsafe_label_filters(q))
    warnings.extend(_find_groupby_overflow_risk(q))
    warnings.extend(_find_geosparql_timeout_risk(q))
    warnings.extend(_find_order_by_optional_timeout_risk(q))
    warnings.extend(_find_cartesian_product_risk(q))
    warnings.extend(_find_untyped_numeric_literal_risk(q))

    select_pos = q_upper.find("SELECT")
    from_pos = q_upper.find("FROM")
    where_pos = q_upper.find("WHERE")

    if select_pos == -1:
        errors.append("SELECT ontbreekt.")

    if where_pos == -1:
        errors.append("WHERE ontbreekt.")

    uses_named_graph = "GRAPH " in q_upper

    if from_pos == -1 and not uses_named_graph:
        warnings.append(
            "Geen FROM of GRAPH gevonden. Dit kan bewust zijn bij queries "
            "over meerdere named graphs. Controleer of dit gewenst is. "
            f"Gebruik anders FROM <{DEFAULT_DATASET_GRAPH}> of expliciete GRAPH-blokken."
        )

    if select_pos != -1 and from_pos != -1 and from_pos < select_pos:
        errors.append(
            "FROM staat vóór SELECT. Gebruik: SELECT ... FROM ... WHERE ..."
        )

    if select_pos != -1 and from_pos != -1 and where_pos != -1:
        if not (select_pos < from_pos < where_pos):
            errors.append(
                "Onjuiste SPARQL-volgorde. Gebruik: "
                "SELECT ... FROM ... WHERE ..."
            )

    expected_from = f"FROM <{DEFAULT_DATASET_GRAPH}>"

    if "FROM" in q_upper and expected_from not in q:
        warnings.append(
            f"Controleer de graph. Verwacht vaak: {expected_from}. "
            "Bij cross-graph queries kan een andere aanpak nodig zijn."
        )

    if "SELECT COUNT(" in q_upper:
        errors.append(
            "Gebruik een alias bij COUNT: "
            "SELECT (COUNT(DISTINCT ?rm) AS ?aantal)"
        )

    if "COUNT(" in q_upper and "DISTINCT" not in q_upper:
        warnings.append(
            "Gebruik meestal COUNT(DISTINCT ?var) bij tellingen met joins."
        )

    if (
        "SELECT " in q_upper
        and "DISTINCT" not in q_upper
        and "COUNT(" not in q_upper
    ):
        warnings.append(
            "Overweeg SELECT DISTINCT bij lijstqueries met joins."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def format_validation_report(query: str) -> str:
    """Return a human-readable validation report."""
    result = validate_sparql(query)

    if result["valid"] and not result["warnings"]:
        return "OK: geen bekende fouten gevonden."

    lines = ["Validatierapport:"]

    for error in result["errors"]:
        lines.append(f"ERROR: {error}")

    for warning in result["warnings"]:
        lines.append(f"WARNING: {warning}")

    return "\n".join(lines)


def has_blocking_errors(query: str) -> bool:
    result = validate_sparql(query)
    return not result["valid"]