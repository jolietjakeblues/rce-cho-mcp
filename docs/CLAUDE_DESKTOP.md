# CLAUDE_DESKTOP.md

# Claude Desktop configuration

The RCE CHO MCP server can be connected to Claude Desktop using the Model Context Protocol (MCP).

## Locate the Claude Desktop configuration file

### Windows

```text
%APPDATA%\Claude\claude_desktop_config.json
```

### macOS

```text
~/Library/Application Support/Claude/claude_desktop_config.json
```

## Example configuration

Adjust the paths to match your local installation.

```json
{
  "mcpServers": {
    "rce-cho": {
      "command": "C:\\AI\\rce-cho-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "rce_cho_mcp.server"
      ],
      "cwd": "C:\\AI\\rce-cho-mcp"
    }
  }
}
```

## Alternative configuration

If the package was installed globally:

```json
{
  "mcpServers": {
    "rce-cho": {
      "command": "rce-cho-mcp"
    }
  }
}
```

## Verify the connection

Restart Claude Desktop.

Open a new conversation and ask:

```text
What ontology classes are available?
```

or:

```text
Resolve the concept label "Utrecht".
```

If the MCP server is connected correctly, Claude will discover and call the available tools automatically.

## Troubleshooting

### Module not found

Verify that the virtual environment is active and that the package was installed using:

```bash
pip install -e .
```

### Server immediately exits

Run manually from the project directory:

```bash
python -m rce_cho_mcp.server
```

### Claude does not show MCP tools

* Restart Claude Desktop.
* Verify the JSON syntax.
* Verify the file paths.
* Check the Claude logs for startup errors.

## Remote deployment

The configuration above runs a local MCP server over stdio -- useful for
development, or to pick up local source changes immediately (a running
local server does **not** reload code automatically; restart it, or
disconnect/reconnect the server in Claude Desktop, after editing the
source).

A hosted version of this server is also deployed on Render at
`https://rce-cho-mcp.onrender.com`, speaking MCP over Streamable HTTP
(see `render.yaml`, `Dockerfile` and `http_server.py`). Connect a client
to it by adding it as a remote MCP connector pointing at that URL --
in Claude, via Settings > Connectors rather than editing this JSON file
(the JSON file above is for locally-run, command-based servers only).
Running both the local `rce-cho` entry above and a remote connector to
the hosted URL at the same time is normal and lets you compare the two:
a local server reflects whatever is on disk right now, the hosted one
reflects whatever was last deployed to Render.
