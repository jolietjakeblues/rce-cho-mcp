from rce_cho_mcp.config import DEFAULT_GRAPH


FORBIDDEN_PREFIXES = [
    "ceosp:",
    "ceox:",
]

FORBIDDEN_CLASSES = [
    "ceo:Rijksmonumenten",
    "ceo:ArcheologischeComplexen",
    "ceo:ArcheologischeTerreinen",
    "ceo:Vondst",
]

FORBIDDEN_PROPERTIES = [
    "ceosp:heeftProvincie",
    "ceox:heeftProvincie",
    "ceox:heeftAdresgegevens",
    "ceo:heeftPlaats",
    "ceo:heeftGemeente",
    "ceo:heeftAdres",
    "ceo:heeftArchitect",
    "ceo:heeftFunctie",
]

FORBIDDEN_LANGUAGE_FILTERS = [
    "lang(",
    "LANG(",
    "LANGMATCHES(",
    "langmatches(",
    "@nl",
]


def validate_sparql(query: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    q = query
    q_upper = q.upper()

    for prefix in FORBIDDEN_PREFIXES:
        if prefix in q:
            errors.append(f"Verboden prefix gevonden: {prefix}")

    for class_name in FORBIDDEN_CLASSES:
        if class_name in q:
            errors.append(f"Verboden classnaam gevonden: {class_name}")

    for prop in FORBIDDEN_PROPERTIES:
        if prop in q:
            errors.append(f"Verboden property gevonden: {prop}")

    for term in FORBIDDEN_LANGUAGE_FILTERS:
        if term in q:
            errors.append(f"Verboden taalfilter gevonden: {term}")

    select_pos = q_upper.find("SELECT")
    from_pos = q_upper.find("FROM")
    where_pos = q_upper.find("WHERE")

    if select_pos == -1:
        errors.append("SELECT ontbreekt.")

    if where_pos == -1:
        errors.append("WHERE ontbreekt.")

    if from_pos == -1:
        errors.append(
            f"FROM ontbreekt. Gebruik: FROM <{DEFAULT_GRAPH}>"
        )

    if select_pos != -1 and from_pos != -1 and from_pos < select_pos:
        errors.append("FROM staat vóór SELECT. Gebruik: SELECT ... FROM ... WHERE ...")

    if select_pos != -1 and from_pos != -1 and where_pos != -1:
        if not (select_pos < from_pos < where_pos):
            errors.append("Onjuiste SPARQL-volgorde. Gebruik: SELECT ... FROM ... WHERE ...")

    expected_from = f"FROM <{DEFAULT_GRAPH}>"
    if "FROM" in q_upper and expected_from not in q:
        warnings.append(f"Controleer de graph. Verwacht: {expected_from}")

    if "SELECT COUNT(" in q_upper:
        errors.append(
            "Gebruik een alias bij COUNT: SELECT (COUNT(DISTINCT ?rm) AS ?aantal)"
        )

    if "COUNT(" in q_upper and "DISTINCT" not in q_upper:
        warnings.append("Gebruik COUNT(DISTINCT ?var) bij tellingen met joins.")

    if "SELECT " in q_upper and "DISTINCT" not in q_upper and "COUNT(" not in q_upper:
        warnings.append("Overweeg SELECT DISTINCT bij lijstqueries met joins.")

    return errors, warnings


def format_validation_report(query: str) -> str:
    errors, warnings = validate_sparql(query)

    if not errors and not warnings:
        return "✅ Geen bekende fouten gevonden. Query ziet er geldig uit."

    lines = ["Validatierapport:"]

    for error in errors:
        lines.append(f"❌ {error}")

    for warning in warnings:
        lines.append(f"⚠️ {warning}")

    return "\n".join(lines)


def has_blocking_errors(query: str) -> bool:
    errors, _warnings = validate_sparql(query)
    return len(errors) > 0