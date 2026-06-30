import os

from rce_cho_mcp.server import mcp


def main() -> None:
    """Run the RCE CHO MCP server over Streamable HTTP."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.environ["PORT"])

    mcp.settings.host = host
    mcp.settings.port = port
    mcp.settings.stateless_http = True
    mcp.settings.json_response = True
    mcp.settings.allowed_hosts = ["*"]

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()