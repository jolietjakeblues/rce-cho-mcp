import functools
import inspect
import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from rce_cho_mcp.config import SPARQL_ENDPOINT, SPARQL_FALLBACK_ENDPOINT, USER_AGENT
from rce_cho_mcp.pitfalls import TWO_STAGE_SUBQUERY_REMEDY

# Root-logging wordt al naar stderr geconfigureerd door FastMCP zelf
# (configure_logging(), aangeroepen vanuit FastMCP.__init__() in server.py's
# `mcp = FastMCP(...)`-regel) -- nooit naar stdout loggen, dat zou bij de
# stdio-transport het JSON-RPC-berichtenverkeer corrumperen. Deze module
# gebruikt alleen een gewone getLogger(); geen eigen handler/config nodig.
logger = logging.getLogger(__name__)

# Gateway-level codes that mean "this endpoint instance is having trouble",
# as opposed to a 4xx that reflects a problem with the query itself.
_FALLBACK_HTTP_CODES = {502, 503, 504}


def escape_sparql_string(value: str) -> str:
    """Escape a string value for safe use in a SPARQL string literal.

    Single shared implementation -- used by every module that interpolates
    user input (a label, gemeente name, rijksmonumentnummer, WKT literal)
    into a hand-built SPARQL query string.
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


# SPARQL 1.1 grammar: IRIREF ::= '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' -- none
# of these characters (nor space/control chars) can legally appear inside
# <...>. A caller-supplied value containing one is either invalid SPARQL
# syntax, or -- '>' specifically -- breaks out of the <...> token and lets
# the rest of the string inject arbitrary graph patterns into the query.
# escape_sparql_string() above does not help here: it escapes a value for a
# quoted string literal ("..."), not for a bare <...> IRIREF, which has no
# escape mechanism at all -- an unsafe character must be rejected, not
# escaped. Use this wherever a caller-supplied string is interpolated
# directly into <{...}> rather than resolved first (e.g. via a
# get_classes()-style lookup) or wrapped in a string literal.
_UNSAFE_IRI_CHARS = frozenset('<>"{}|^`\\')


def is_safe_iri(value: str) -> bool:
    """Return False if value contains a character that can never legally
    appear inside a SPARQL IRIREF (<...>), so it must not be interpolated
    there as-is."""
    return not any(ch in _UNSAFE_IRI_CHARS or ord(ch) <= 0x20 for ch in value)


def rows(data: dict) -> list[dict]:
    """Return the SPARQL JSON result bindings, or [] if there are none.

    Single shared accessor for data["results"]["bindings"], used everywhere
    a SPARQL JSON response is read.
    """
    return data.get("results", {}).get("bindings", [])


def post_sparql(endpoint: str, query: str, timeout: int = 30) -> dict:
    """POST a single SPARQL query to one endpoint and return the JSON response.

    No retry/fallback across endpoints -- execute_sparql() builds that on top
    of this for the default RCE endpoints. Exposed directly for callers that
    talk to a different, single SPARQL endpoint (e.g. brk_spatial.py's
    Kadaster KKG queries), so they don't have to reimplement the HTTP/encoding
    details themselves.
    """
    data = urllib.parse.urlencode({"query": query}).encode("utf-8")
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

    logger.debug("POST %s (%d bytes query)", endpoint, len(data))
    start = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            elapsed = time.monotonic() - start
            logger.debug("POST %s klaar in %.2fs (HTTP %s)", endpoint, elapsed, response.status)
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        elapsed = time.monotonic() - start
        logger.warning("POST %s gaf HTTP %s na %.2fs", endpoint, e.code, elapsed)
        raise
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        elapsed = time.monotonic() - start
        logger.warning("POST %s onbereikbaar na %.2fs: %s", endpoint, elapsed, e)
        raise


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
    endpoints = [SPARQL_ENDPOINT]
    if SPARQL_FALLBACK_ENDPOINT and SPARQL_FALLBACK_ENDPOINT != SPARQL_ENDPOINT:
        endpoints.append(SPARQL_FALLBACK_ENDPOINT)

    for index, endpoint in enumerate(endpoints):
        is_last_attempt = index == len(endpoints) - 1

        try:
            return post_sparql(endpoint, query, timeout)
        except urllib.error.HTTPError as e:
            if not is_last_attempt and e.code in _FALLBACK_HTTP_CODES:
                logger.warning(
                    "%s gaf HTTP %s (gateway-fout) -- val terug op %s",
                    endpoint, e.code, endpoints[index + 1],
                )
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if not is_last_attempt:
                logger.warning("%s onbereikbaar -- val terug op %s", endpoint, endpoints[index + 1])
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
            f"Combineert de query ORDER BY met OPTIONAL-joins? {TWO_STAGE_SUBQUERY_REMEDY} "
            "Zie validate_query_structured().",
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


def _log_tool_exception(func_name: str, exc: Exception) -> None:
    """Centrale foutlogging voor elke tool die via een van de decorators
    hieronder loopt -- één plek, dus logging voor alle ~20 betrokken tools
    tegelijk in plaats van losse logregels per tool."""
    if isinstance(exc, urllib.error.HTTPError):
        logger.error("%s: HTTP %s van %s", func_name, exc.code, exc.url)
    else:
        logger.error("%s: onverwachte fout %s: %s", func_name, type(exc).__name__, exc)


def sparql_text_errors(include_body: bool = False):
    """Decorator for an @mcp.tool() that returns str.

    Catches urllib.error.HTTPError and any other exception and formats them
    the same way every such tool does (classify_error() + a consistent Dutch
    foutmelding), instead of each tool in server.py repeating the same
    try/except block. Werkt op zowel een gewone als een async tool-functie
    (nodig voor tools die ctx.report_progress() awaiten).

    include_body: when True, append the raw error body (truncated) to the
    message -- used by query_sparql(), which shows it for debugging.
    """
    def decorator(func):
        def _format_http_error(e: urllib.error.HTTPError) -> str:
            body = e.read().decode("utf-8", errors="replace")
            code, advies = classify_error(body, e.code)
            text = f"[{code}] HTTP {e.code} van {e.url}\n\nAdvies: {advies}"
            if include_body:
                text += f"\n\nRuwe foutmelding:\n{body[:500]}"
            return text

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except urllib.error.HTTPError as e:
                    _log_tool_exception(func.__name__, e)
                    return _format_http_error(e)
                except Exception as e:
                    _log_tool_exception(func.__name__, e)
                    return f"Onverwachte fout: {type(e).__name__}: {e}"

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except urllib.error.HTTPError as e:
                _log_tool_exception(func.__name__, e)
                return _format_http_error(e)
            except Exception as e:
                _log_tool_exception(func.__name__, e)
                return f"Onverwachte fout: {type(e).__name__}: {e}"

        return wrapper

    return decorator


def sparql_dict_errors(func):
    """Same as sparql_text_errors(), for an @mcp.tool() that returns a dict."""

    def _error_dict(e: urllib.error.HTTPError) -> dict:
        body = e.read().decode("utf-8", errors="replace")
        code, advies = classify_error(body, e.code)
        return {
            "error": code,
            "status": e.code,
            "advies": advies,
            "endpoint": e.url,
            "body": body[:500],
        }

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except urllib.error.HTTPError as e:
                _log_tool_exception(func.__name__, e)
                return _error_dict(e)
            except Exception as e:
                _log_tool_exception(func.__name__, e)
                return {"error": "unexpected_error", "type": type(e).__name__, "message": str(e)}

        return async_wrapper

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except urllib.error.HTTPError as e:
            _log_tool_exception(func.__name__, e)
            return _error_dict(e)
        except Exception as e:
            _log_tool_exception(func.__name__, e)
            return {"error": "unexpected_error", "type": type(e).__name__, "message": str(e)}

    return wrapper


def format_results(data: dict, max_rows: int = 100) -> str:
    """Format SPARQL JSON results as readable text."""
    if "boolean" in data:
        return f"Resultaat: {data['boolean']}"

    bindings = rows(data)
    variables = data.get("head", {}).get("vars", [])

    if not bindings:
        return "Geen resultaten gevonden."

    total = len(bindings)
    shown_rows = bindings[:max_rows]

    lines = [f"Gevonden: {total} resultaat/resultaten (max {max_rows} getoond)\n"]
    lines.append(" | ".join(variables))
    lines.append("-" * 60)

    for row in shown_rows:
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
_POLYGON_RE = re.compile(r"^POLYGON\s*\((.+)\)$", re.IGNORECASE | re.DOTALL)
_MULTIPOLYGON_RE = re.compile(r"^MULTIPOLYGON\s*\((.+)\)$", re.IGNORECASE | re.DOTALL)
# Anchored at ^, so e.g. "MULTILINESTRING(...)" never matches _LINESTRING_RE
# (it doesn't start with the literal text "LINESTRING") -- same mutual
# exclusivity as POLYGON vs MULTIPOLYGON above, match order doesn't matter.
_LINESTRING_RE = re.compile(r"^LINESTRING\s*\((.+)\)$", re.IGNORECASE | re.DOTALL)
_MULTILINESTRING_RE = re.compile(r"^MULTILINESTRING\s*\((.+)\)$", re.IGNORECASE | re.DOTALL)


def _parse_coord_pair(pair: str) -> list[float]:
    lon, lat = pair.strip().split()
    return [float(lon), float(lat)]


def _parse_ring(ring_str: str) -> list[list[float]]:
    return [_parse_coord_pair(p) for p in ring_str.strip().split(",")]


def _split_top_level(text: str) -> list[str]:
    """Split text on commas that sit outside any parentheses.

    Used to separate sibling rings/polygons in WKT (e.g. an exterior ring
    from its holes, or one polygon from the next in a MULTIPOLYGON) without
    also splitting on the commas between coordinate pairs inside a ring,
    which sit one paren level deeper.
    """
    parts = []
    depth = 0
    start = 0

    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(text[start:i])
            start = i + 1

    parts.append(text[start:])
    return [p.strip() for p in parts]


def _strip_parens(text: str) -> str:
    text = text.strip()
    if text.startswith("(") and text.endswith(")"):
        return text[1:-1].strip()
    return text


def _parse_polygon_rings(rings_text: str) -> list[list[list[float]]]:
    """Parse a POLYGON's ring list, e.g. "(ext ring), (hole ring), ...".

    The first ring is the exterior ring, any further rings are holes --
    this is exactly GeoJSON's Polygon coordinates convention, so the
    result can be used as-is for both a standalone Polygon and one
    polygon within a MultiPolygon.
    """
    return [_parse_ring(_strip_parens(r)) for r in _split_top_level(rings_text)]


def _resolve_coordinate_system(first_point: list[float], convert_rd: bool) -> str | None:
    """Decide what to do with a POLYGON/MULTIPOLYGON based on its first point.

    Returns "rd" (convert every point), "wgs84" (leave as-is), or None
    (reject the geometry -- RD coordinates without convert_rd=True, or an
    unrecognized coordinate system). Mirrors the POINT branch's logic below,
    factored out so POLYGON and MULTIPOLYGON can't drift apart again like
    they did before this fix (MULTIPOLYGON used to convert unconditionally,
    without checking _is_rd() first, and neither ever rejected RD
    coordinates when convert_rd=False -- both silently returned bogus
    "WGS84" coordinates far outside valid lon/lat range).
    """
    x, y = first_point
    if _is_rd(x, y):
        return "rd" if convert_rd else None
    if abs(x) > 180 or abs(y) > 90:
        return None  # onbekend coördinatenstelsel
    return "wgs84"


def wkt_to_geometry(wkt: str, convert_rd: bool = False) -> dict | None:
    """Parse a WKT string to a GeoJSON geometry dict. Returns None on failure.

    Supports POINT, POLYGON, MULTIPOLYGON, LINESTRING and MULTILINESTRING,
    including interior rings (holes) on POLYGON/MULTIPOLYGON. LINESTRING/
    MULTILINESTRING were added 2026-11-06: the 'linies' graph's
    ceo:asWKT-RD property (see query_sparql_geojson()'s docstring) uses
    exactly this shape, in RD coordinates -- before this, every row from
    that graph was silently skipped (an unrecognized WKT shape, same as any
    other parse failure), giving an always-empty FeatureCollection despite
    being the tool's own documented example.

    convert_rd: when True, coordinates detected as RD (EPSG:28992) are
    automatically converted to WGS84 before building the geometry.
    When False (default), RD coordinates are rejected and None is returned
    -- for every geometry type, not just POINT.

    Any malformed numeric literal (e.g. a non-numeric coordinate) is treated
    as a parse failure and returns None, same as an unrecognized WKT shape --
    it never raises, so one bad row in a larger result set can be skipped by
    the caller (see to_geojson()) instead of aborting the whole conversion.
    """
    wkt = _WKT_STRIP.sub("", wkt).strip()

    try:
        m = _POINT_RE.match(wkt)
        if m:
            x, y = float(m.group(1)), float(m.group(2))
            if _is_rd(x, y):
                if not convert_rd:
                    return None  # RD-coördinaten -- gebruik convert_rd=True om te converteren
                x, y = rd_to_wgs84(x, y)
            elif abs(x) > 180 or abs(y) > 90:
                return None  # onbekend coördinatenstelsel
            return {"type": "Point", "coordinates": [x, y]}

        m = _POLYGON_RE.match(wkt)
        if m:
            rings = _parse_polygon_rings(m.group(1))
            if not rings or not rings[0]:
                return None
            action = _resolve_coordinate_system(rings[0][0], convert_rd)
            if action is None:
                return None
            if action == "rd":
                rings = [[list(rd_to_wgs84(p[0], p[1])) for p in ring] for ring in rings]
            return {"type": "Polygon", "coordinates": rings}

        m = _MULTIPOLYGON_RE.match(wkt)
        if m:
            polygons = [
                _parse_polygon_rings(_strip_parens(p)) for p in _split_top_level(m.group(1))
            ]
            if not polygons or not polygons[0] or not polygons[0][0]:
                return None
            action = _resolve_coordinate_system(polygons[0][0][0], convert_rd)
            if action is None:
                return None
            if action == "rd":
                polygons = [
                    [[list(rd_to_wgs84(pt[0], pt[1])) for pt in ring] for ring in polygon]
                    for polygon in polygons
                ]
            return {"type": "MultiPolygon", "coordinates": polygons}

        m = _LINESTRING_RE.match(wkt)
        if m:
            line = _parse_ring(m.group(1))
            if not line:
                return None
            action = _resolve_coordinate_system(line[0], convert_rd)
            if action is None:
                return None
            if action == "rd":
                line = [list(rd_to_wgs84(p[0], p[1])) for p in line]
            return {"type": "LineString", "coordinates": line}

        m = _MULTILINESTRING_RE.match(wkt)
        if m:
            # Structurally identical to a MULTIPOLYGON's list-of-rings (each
            # top-level comma-separated, paren-wrapped piece is one flat
            # coordinate list) -- _parse_polygon_rings() already does exactly
            # this split+parse, so it's reused as-is rather than duplicated.
            lines = _parse_polygon_rings(m.group(1))
            if not lines or not lines[0]:
                return None
            action = _resolve_coordinate_system(lines[0][0], convert_rd)
            if action is None:
                return None
            if action == "rd":
                lines = [[list(rd_to_wgs84(p[0], p[1])) for p in line] for line in lines]
            return {"type": "MultiLineString", "coordinates": lines}

        return None
    except ValueError:
        return None


def to_geojson(data: dict, wkt_var: str = "wkt", convert_rd: bool = False) -> dict:
    """Convert SPARQL JSON results to a GeoJSON FeatureCollection.

    wkt_var: the name of the result variable that contains the WKT geometry.
    convert_rd: when True, RD (EPSG:28992) coordinates are converted to WGS84.
    All other variables become feature properties.
    Rows without a valid geometry are skipped.
    """
    bindings = rows(data)
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
