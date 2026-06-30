import os

from rce_cho_mcp.server import mcp


def main() -> None:
    """Run the RCE CHO MCP server over Streamable HTTP.

    This entrypoint is intended for remote deployment, for example on Render,
    Fly.io, Railway or a VPS.

    The regular server.py entrypoint remains the local stdio server.
    """
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.environ["PORT"])

    mcp.settings.host = host
    mcp.settings.port = port
    mcp.settings.stateless_http = True
    mcp.settings.json_response = True

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()