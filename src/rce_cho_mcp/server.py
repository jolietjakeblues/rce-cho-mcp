import urllib.error

from mcp.server.fastmcp import FastMCP

from rce_cho_mcp.prompts import WORKFLOW_INSTRUCTIONS
from rce_cho_mcp.sparql import SPARQL_ENDPOINT, execute_sparql, format_results


mcp = FastMCP("RCE CHO SPARQL", instructions=WORKFLOW_INSTRUCTIONS)


@mcp.tool()
def ping() -> str:
    """Test of de MCP-server bereikbaar is."""
    return "RCE CHO MCP werkt."


@mcp.tool()
def query_sparql(sparql_query: str, max_rows: int = 100) -> str:
    """Voer een SPARQL SELECT of ASK query uit op het RCE CHO endpoint."""
    try:
        data = execute_sparql(sparql_query)
        return format_results(data, max_rows=max_rows)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return (
            f"HTTP fout {e.code} van endpoint {SPARQL_ENDPOINT}: {e.reason}\n\n"
            f"Endpoint antwoord:\n{body[:1000]}"
        )
    except Exception as e:
        return f"Onverwachte fout: {type(e).__name__}: {e}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()