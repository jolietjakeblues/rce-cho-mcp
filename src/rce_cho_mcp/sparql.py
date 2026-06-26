import json
import urllib.parse
import urllib.request

from rce_cho_mcp.config import SPARQL_ENDPOINT, USER_AGENT


def execute_sparql(query: str, timeout: int = 30) -> dict:
    """Execute a SPARQL query and return the JSON response."""
    params = urllib.parse.urlencode({"query": query})
    url = f"{SPARQL_ENDPOINT}?{params}"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/sparql-results+json",
            "User-Agent": USER_AGENT,
        },
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw)


def format_results(data: dict, max_rows: int = 100) -> str:
    """Format SPARQL JSON results as readable text."""
    if "boolean" in data:
        return f"Resultaat: {data['boolean']}"

    bindings = data.get("results", {}).get("bindings", [])
    variables = data.get("head", {}).get("vars", [])

    if not bindings:
        return "Geen resultaten gevonden."

    total = len(bindings)
    rows = bindings[:max_rows]

    lines = [f"Gevonden: {total} resultaat/resultaten (max {max_rows} getoond)\n"]
    lines.append(" | ".join(variables))
    lines.append("-" * 60)

    for row in rows:
        values = []
        for variable in variables:
            cell = row.get(variable, {})
            values.append(cell.get("value", "-"))

        lines.append(" | ".join(values))

    return "\n".join(lines)