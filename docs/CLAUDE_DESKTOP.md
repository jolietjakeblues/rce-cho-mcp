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

## Future deployment

The current installation model assumes a local MCP server.

Future versions may support remote HTTP MCP deployment, allowing users to connect by URL without installing Python locally.
