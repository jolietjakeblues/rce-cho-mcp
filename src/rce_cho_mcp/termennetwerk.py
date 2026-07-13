import json
import urllib.error
import urllib.request

from rce_cho_mcp.config import TERMENNETWERK_ENDPOINT, USER_AGENT

# Short aliases for the terminology sources most relevant to RCE CHO data.
# Any other Network of Terms source can be passed as a full URI instead.
KNOWN_SOURCES = {
    "cht": "https://data.cultureelerfgoed.nl/term/id/cht",
    "abr": "https://data.cultureelerfgoed.nl/term/id/abr",
    "wikidata": "https://www.wikidata.org#entities-all",
    "aat": "http://vocab.getty.edu/aat",
}

# The API rejects an explicitly passed genres: null or genres: [] ("does not
# contain 1 required value(s)") -- the argument must be omitted from the
# query entirely when no genre filter is wanted, not just set to a falsy
# value. Hence two variants instead of one query with a nullable variable.
_TERMS_QUERY = """
query Zoek($sources: [ID!]!, $query: String!, $limit: Int, $timeoutMs: Int) {
  terms(sources: $sources, query: $query, limit: $limit, timeoutMs: $timeoutMs) {
    source { uri name }
    result {
      __typename
      ... on Terms {
        terms {
          uri
          prefLabel
          altLabel
          definition
          broader { uri prefLabel }
          narrower { uri prefLabel }
        }
      }
      ... on Error { message }
    }
  }
}
"""

_TERMS_QUERY_WITH_GENRES = """
query Zoek($sources: [ID!]!, $query: String!, $genres: [ID!]!, $limit: Int, $timeoutMs: Int) {
  terms(sources: $sources, query: $query, genres: $genres, limit: $limit, timeoutMs: $timeoutMs) {
    source { uri name }
    result {
      __typename
      ... on Terms {
        terms {
          uri
          prefLabel
          altLabel
          definition
          broader { uri prefLabel }
          narrower { uri prefLabel }
        }
      }
      ... on Error { message }
    }
  }
}
"""

_LOOKUP_QUERY = """
query Lookup($uris: [ID!]!) {
  lookup(uris: $uris) {
    uri
    source {
      ... on Source { uri name }
      ... on Error { message }
    }
    result {
      ... on Term {
        uri
        prefLabel
        altLabel
        definition
        broader { uri prefLabel }
        narrower { uri prefLabel }
      }
      ... on Error { message }
    }
  }
}
"""


def _post_graphql(query: str, variables: dict, timeout: int = 20) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        TERMENNETWERK_ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Termennetwerk gaf HTTP {e.code}: {body[:300]}") from e
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        raise RuntimeError(f"Termennetwerk niet bereikbaar: {e}") from e


def _resolve_sources(sources: list[str]) -> list[str]:
    """Map known short keys (cht, abr, ...) to full source URIs.

    Values that are not a known key are assumed to already be a full URI
    and are passed through unchanged.
    """
    return [KNOWN_SOURCES.get(s, s) for s in sources]


def search_terms(
    term: str,
    sources: list[str] | None = None,
    genres: list[str] | None = None,
    max_results: int = 25,
    timeout_ms: int = 10000,
) -> list[dict]:
    """Fuzzy-search SKOS concepts by natural-language term across one or more
    Network of Terms terminology sources.

    Unlike an exact skos:prefLabel match, this searches prefLabel and
    altLabel (synonyms), ranked by relevance, and returns broader/narrower
    terms for query expansion. Defaults to the RCE thesauri (CHT, ABR) when
    no sources are given.
    """
    resolved_sources = _resolve_sources(sources or ["cht", "abr"])
    variables = {
        "sources": resolved_sources,
        "query": term,
        "limit": max_results,
        "timeoutMs": timeout_ms,
    }

    if genres:
        query_doc = _TERMS_QUERY_WITH_GENRES
        variables["genres"] = _resolve_sources(genres)
    else:
        query_doc = _TERMS_QUERY

    data = _post_graphql(query_doc, variables)
    if data.get("errors"):
        raise RuntimeError(f"GraphQL fout: {data['errors']}")
    return data.get("data", {}).get("terms", [])


def lookup_terms(uris: list[str], timeout_ms: int = 10000) -> list[dict]:
    """Resolve known external concept URIs (e.g. a skos:exactMatch target
    found via describe_resource_uri) to labels, via the Network of Terms.
    """
    data = _post_graphql(
        _LOOKUP_QUERY,
        {"uris": uris, "timeoutMs": timeout_ms},
    )
    if data.get("errors"):
        raise RuntimeError(f"GraphQL fout: {data['errors']}")
    return data.get("data", {}).get("lookup", [])
