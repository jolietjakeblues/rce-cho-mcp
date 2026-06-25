from reference_client.builder.builder import build_sparql
from reference_client.planner.parser import parse_question
from rce_cho_mcp.resolver import resolve_label
from rce_cho_mcp.sparql import execute_sparql, format_results
from rce_cho_mcp.validator import validate_sparql


def answer_question(question: str, max_rows: int = 100) -> str:
    """Run the full question pipeline: plan, resolve, build, validate, execute."""
    plan = parse_question(question)

    if "gemeente" in plan.filters:
        gemeente_uri = resolve_label(plan.filters["gemeente"], graph_name="owms")
        if gemeente_uri is None:
            return f"Gemeente niet gevonden in OWMS: {plan.filters['gemeente']}"
        plan.filters["gemeente_uri"] = gemeente_uri

    query = build_sparql(plan)

    errors, warnings = validate_sparql(query)

    if errors:
        return (
            "Query niet uitgevoerd vanwege validatiefouten:\n\n"
            + "\n".join(f"- {error}" for error in errors)
            + "\n\nGegenereerde query:\n"
            + query
        )

    data = execute_sparql(query)

    lines = [
        "Pipeline uitgevoerd.",
        "",
        "Plan:",
        f"- Intent: {plan.intent}",
        f"- Entity: {plan.entity}",
        f"- Filters: {plan.filters}",
        f"- Output: {plan.output}",
        "",
        "Validatie:",
        "Geen blokkerende fouten.",
    ]

    if warnings:
        lines.append("")
        lines.append("Waarschuwingen:")
        lines.extend(f"- {warning}" for warning in warnings)

    lines.append("")
    lines.append("Resultaat:")
    lines.append(format_results(data, max_rows=max_rows))

    return "\n".join(lines)