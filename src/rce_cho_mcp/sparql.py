import json
import re
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
    
def classify_error(body: str, http_code: int) -> tuple[str, str]:
    """Classificeer een bekende Virtuoso- of endpointfout."""
    b = body.lower()
    if "value of any type column too long" in b:
        return (
            "GROUPBY_OVERFLOW",
            "Virtuoso kan dit veld niet groeperen (tekst te lang voor GROUP BY). "
            "Herschrijf de query met een subquery op twee niveaus: haal eerst de "
            "URI's op in een subquery, join daarna de lange tekstvelden buiten de GROUP BY.",
        )
    if "timeout" in b or "rdfr20" in b:
        return (
            "TIMEOUT",
            "Het endpoint heeft de query afgebroken wegens een tijdslimiet. "
            "Voeg een LIMIT toe, verklein het bereik, of splits de query op.",
        )
    if "sparql compiler" in b or "sp029" in b or "syntax" in b:
        return (
            "SYNTAX",
            "De SPARQL-query bevat een syntaxfout. "
            "Gebruik validate_query() om de fout op te sporen.",
        )
    if http_code == 503:
        return (
            "ENDPOINT_UNAVAILABLE",
            "Het RCE CHO endpoint is tijdelijk niet beschikbaar. Probeer het later opnieuw.",
        )
    return ("HTTP_ERROR", f"HTTP {http_code}: onbekende fout van het endpoint.")


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


# Matches WKT literals with an optional datatype suffix, e.g.:
# POINT(4.9041 52.3676)
# POINT(4.9041 52.3676)^^<http://www.opengis.net/ont/geosparql#wktLiteral>
_WKT_STRIP = re.compile(r"\^\^<[^>]+>$")

_POINT_RE = re.compile(r"^POINT\s*\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)$", re.IGNORECASE)
_POLYGON_RE = re.compile(r"^POLYGON\s*\(\((.+)\)\)$", re.IGNORECASE | re.DOTALL)
_MULTIPOLYGON_RE = re.compile(r"^MULTIPOLYGON\s*\(\((.+)\)\)$", re.IGNORECASE | re.DOTALL)


def _parse_coord_pair(pair: str) -> list[float]:
    lon, lat = pair.strip().split()
    return [float(lon), float(lat)]


def _parse_ring(ring_str: str) -> list[list[float]]:
    return [_parse_coord_pair(p) for p in ring_str.strip().split(",")]


def wkt_to_geometry(wkt: str) -> dict | None:
    """Parse a WKT string to a GeoJSON geometry dict. Returns None on failure."""
    wkt = _WKT_STRIP.sub("", wkt).strip()

    m = _POINT_RE.match(wkt)
    if m:
        return {"type": "Point", "coordinates": [float(m.group(1)), float(m.group(2))]}

    m = _POLYGON_RE.match(wkt)
    if m:
        return {"type": "Polygon", "coordinates": [_parse_ring(m.group(1))]}

    m = _MULTIPOLYGON_RE.match(wkt)
    if m:
        # Split on ")(" to get individual polygon rings
        rings = [_parse_ring(r) for r in re.split(r"\)\s*,\s*\(", m.group(1))]
        return {"type": "MultiPolygon", "coordinates": [[ring] for ring in rings]}

    return None


def to_geojson(data: dict, wkt_var: str = "wkt") -> dict:
    """Convert SPARQL JSON results to a GeoJSON FeatureCollection.

    wkt_var: the name of the result variable that contains the WKT geometry.
    All other variables become feature properties.
    Rows without a valid geometry are skipped.
    """
    bindings = data.get("results", {}).get("bindings", [])
    variables = data.get("head", {}).get("vars", [])
    prop_vars = [v for v in variables if v != wkt_var]

    features = []
    skipped = 0

    for row in bindings:
        raw_wkt = row.get(wkt_var, {}).get("value", "")
        geometry = wkt_to_geometry(raw_wkt) if raw_wkt else None

        if geometry is None:
            skipped += 1
            continue

        properties = {v: row[v]["value"] for v in prop_vars if v in row}
        features.append({"type": "Feature", "geometry": geometry, "properties": properties})

    result = {"type": "FeatureCollection", "features": features}

    if skipped:
        result["_skipped"] = skipped

    return result