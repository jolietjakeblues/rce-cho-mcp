import json
import re
import urllib.error
import urllib.parse
import urllib.request

from rce_cho_mcp.config import SPARQL_ENDPOINT, SPARQL_FALLBACK_ENDPOINT, USER_AGENT

# Gateway-level codes that mean "this endpoint instance is having trouble",
# as opposed to a 4xx that reflects a problem with the query itself.
_FALLBACK_HTTP_CODES = {502, 503, 504}


def _post_sparql(endpoint: str, data: bytes, timeout: int) -> dict:
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw)


def execute_sparql(query: str, timeout: int = 30) -> dict:
    """Execute a SPARQL query and return the JSON response.

    Uses POST, not GET: a query with a large VALUES clause (>~300-500 URIs,
    querystring >~30-40KB) causes GET to fail with HTTP 431 "Request Header
    Fields Too Large". POST has been tested with querystrings up to ~255KB /
    ~3000 URIs without issues.

    Tries SPARQL_ENDPOINT ("Speedy") first. If that endpoint cannot be
    reached at all, or answers with a gateway-level error (502/503/504),
    the query is retried once against SPARQL_FALLBACK_ENDPOINT ("Virtuoso").
    A query-level error (e.g. a 4xx syntax error) is not retried on the
    fallback, since the same query would fail there identically.
    """
    data = urllib.parse.urlencode({"query": query}).encode("utf-8")

    endpoints = [SPARQL_ENDPOINT]
    if SPARQL_FALLBACK_ENDPOINT and SPARQL_FALLBACK_ENDPOINT != SPARQL_ENDPOINT:
        endpoints.append(SPARQL_FALLBACK_ENDPOINT)

    for index, endpoint in enumerate(endpoints):
        is_last_attempt = index == len(endpoints) - 1

        try:
            return _post_sparql(endpoint, data, timeout)
        except urllib.error.HTTPError as e:
            if not is_last_attempt and e.code in _FALLBACK_HTTP_CODES:
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if not is_last_attempt:
                continue
            raise


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
    if http_code == 504 or "timeout" in b or "time-out" in b or "rdfr20" in b:
        return (
            "TIMEOUT",
            "Het endpoint heeft de query afgebroken wegens een tijdslimiet "
            f"(HTTP {http_code}; een 504 van de gateway bevat vaak geen 'timeout' "
            "in de body). Voeg een LIMIT toe, verklein het bereik, of splits de query op. "
            "Combineert de query ORDER BY met OPTIONAL-joins? Gebruik dan een "
            "tweetraps-subquery: sorteer/pagineer eerst goedkoop op een enkele variabele "
            "in een binnenste SELECT DISTINCT, en voeg de duurdere OPTIONAL-joins pas toe "
            "in de buitenste query op de al-beperkte set. Zie validate_query_structured().",
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


# ---------------------------------------------------------------------------
# RD (Rijksdriehoek, EPSG:28992) → WGS84 conversion
# Based on the Amersfoort / RD New correction formulas published by NSGI.
# Accuracy: ~0.01 m, sufficient for mapping purposes.
# ---------------------------------------------------------------------------

_RD_X0 = 155_000.0   # false easting of Amersfoort origin
_RD_Y0 = 463_000.0   # false northing

_RD_TO_WGS84_LAT = [
    (0, 1,  3236.0331637),
    (2, 0, -32.5915821),
    (0, 2,  -0.2472814),
    (2, 1,  -0.8501341),
    (0, 3,   0.0560508),
    (2, 2,   0.0560337),
    (1, 0,   0.0025886),
    (4, 0,   0.0008848),
    (2, 3,  -0.0000666),
    (1, 1,  -0.0000652),
]

_RD_TO_WGS84_LON = [
    (1, 0,  5261.3028966),
    (1, 1,  105.9780241),
    (1, 2,    2.4576469),
    (3, 0,   -0.8192156),
    (1, 3,   -0.0560859),
    (3, 1,   -0.0560267),
    (0, 1,    0.0025726),
    (3, 2,    0.0022244),
    (1, 4,    0.0000661),
    (0, 2,    0.0000183),
]


def rd_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """Convert RD New (EPSG:28992) coordinates to WGS84 (lon, lat).

    Returns (longitude, latitude) in decimal degrees.
    """
    dx = (x - _RD_X0) * 1e-5
    dy = (y - _RD_Y0) * 1e-5

    lat0 = 52.156160556
    lon0 = 5.387638889

    d_lat = sum(c * dx**p * dy**q for p, q, c in _RD_TO_WGS84_LAT) / 3600
    d_lon = sum(c * dx**p * dy**q for p, q, c in _RD_TO_WGS84_LON) / 3600

    return (lon0 + d_lon, lat0 + d_lat)


def _is_rd(x: float, y: float) -> bool:
    """Heuristic: RD coordinates fall within Dutch national bounds."""
    return 0 <= x <= 300_000 and 300_000 <= y <= 625_000


# ---------------------------------------------------------------------------
# WKT parsing
# ---------------------------------------------------------------------------

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


def wkt_to_geometry(wkt: str, convert_rd: bool = False) -> dict | None:
    """Parse a WKT string to a GeoJSON geometry dict. Returns None on failure.

    convert_rd: when True, coordinates detected as RD (EPSG:28992) are
    automatically converted to WGS84 before building the geometry.
    When False (default), RD coordinates are rejected and None is returned.
    """
    wkt = _WKT_STRIP.sub("", wkt).strip()

    m = _POINT_RE.match(wkt)
    if m:
        x, y = float(m.group(1)), float(m.group(2))
        if _is_rd(x, y):
            if not convert_rd:
                return None  # RD-coördinaten, geen WGS84 — gebruik convert_rd=True om te converteren
            x, y = rd_to_wgs84(x, y)
        elif abs(x) > 180 or abs(y) > 90:
            return None  # onbekend coördinatenstelsel
        return {"type": "Point", "coordinates": [x, y]}

    m = _POLYGON_RE.match(wkt)
    if m:
        ring = _parse_ring(m.group(1))
        if convert_rd and ring and _is_rd(*ring[0]):
            ring = [list(rd_to_wgs84(p[0], p[1])) for p in ring]
        return {"type": "Polygon", "coordinates": [ring]}

    m = _MULTIPOLYGON_RE.match(wkt)
    if m:
        rings = [_parse_ring(r) for r in re.split(r"\)\s*,\s*\(", m.group(1))]
        if convert_rd and rings and rings[0] and _is_rd(*rings[0][0]):
            rings = [[list(rd_to_wgs84(p[0], p[1])) for p in ring] for ring in rings]
        return {"type": "MultiPolygon", "coordinates": [[ring] for ring in rings]}

    return None


def to_geojson(data: dict, wkt_var: str = "wkt", convert_rd: bool = False) -> dict:
    """Convert SPARQL JSON results to a GeoJSON FeatureCollection.

    wkt_var: the name of the result variable that contains the WKT geometry.
    convert_rd: when True, RD (EPSG:28992) coordinates are converted to WGS84.
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
        geometry = wkt_to_geometry(raw_wkt, convert_rd=convert_rd) if raw_wkt else None

        if geometry is None:
            skipped += 1
            continue

        properties = {v: row[v]["value"] for v in prop_vars if v in row}
        features.append({"type": "Feature", "geometry": geometry, "properties": properties})

    result = {"type": "FeatureCollection", "features": features}

    if skipped:
        result["_skipped"] = skipped

    return result
