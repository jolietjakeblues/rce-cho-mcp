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