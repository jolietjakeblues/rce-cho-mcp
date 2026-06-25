import json
import os
import urllib.parse
import urllib.request


SPARQL_ENDPOINT = os.getenv(
    "SPARQL_ENDPOINT",
    "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/services/cho/sparql",
)


def execute_sparql(query: str, timeout: int = 30) -> dict:
    params = urllib.parse.urlencode({"query": query})
    url = f"{SPARQL_ENDPOINT}?{params}"

    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/sparql-results+json",
            "User-Agent": "rce-cho-mcp/0.1.0",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def format_results(data: dict, max_rows: int = 100) -> str:
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
        for var in variables:
            cell = row.get(var, {})
            values.append(cell.get("value", "—"))
        lines.append(" | ".join(values))

    return "\n".join(lines)