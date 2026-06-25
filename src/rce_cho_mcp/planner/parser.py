from rce_cho_mcp.planner.models import QueryPlan


def parse_question(question: str) -> QueryPlan:
    """Parse a simple Dutch heritage question into a QueryPlan."""
    q = question.lower().strip()

    intent = "list"
    output = "list"

    if q.startswith("hoeveel") or "aantal" in q:
        intent = "count"
        output = "number"

    entity = None
    if "rijksmonument" in q or "rijksmonumenten" in q:
        entity = "Rijksmonument"

    filters = {}

    if "zeist" in q:
        filters["gemeente"] = "Zeist"

    return QueryPlan(
        intent=intent,
        entity=entity,
        filters=filters,
        output=output,
    )