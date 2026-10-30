import os

from mcp.server.transport_security import TransportSecuritySettings

from rce_cho_mcp.server import mcp


def main() -> None:
    """Run the RCE CHO MCP server over Streamable HTTP."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.environ["PORT"])

    mcp.settings.host = host
    mcp.settings.port = port
    mcp.settings.stateless_http = True
    mcp.settings.json_response = True
    # DNS-rebinding-bescherming verwacht een Host-header als "localhost" of
    # "127.0.0.1" -- bedoeld om een lokaal draaiende MCP-server te beschermen
    # tegen een kwaadaardige webpagina die via DNS-rebinding verbinding maakt
    # met http://localhost:<port>. Deze server draait niet lokaal maar achter
    # Render's reverse proxy (zie render.yaml/Dockerfile): elk binnenkomend
    # verzoek heeft als Host-header het publieke domein (bv.
    # rce-cho-mcp.onrender.com), nooit "localhost". Met de bescherming aan
    # zou dus elk verzoek worden afgewezen, ook legitieme -- vandaar dat ze
    # hier uitstaat. Alleen veilig in een opstelling als deze, waar de proxy
    # zelf de enige binnenkomende weg is; niet blind overnemen voor een
    # server die wel écht op localhost luistert.
    mcp.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    )

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()