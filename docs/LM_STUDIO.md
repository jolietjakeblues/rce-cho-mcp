# LM_STUDIO.md

# LM Studio configuration

The RCE CHO MCP server can be connected directly to LM Studio using the Model Context Protocol (MCP).

This allows local models to query the Dutch RCE Cultural Heritage Linked Data environment without requiring the model to know the CEO ontology, thesauri or graph structure beforehand.

## Requirements

* LM Studio 0.3 or newer
* Python 3.11 or newer
* A local installation of `rce-cho-mcp`

## Install the MCP server

Clone the repository:

```bash
git clone https://github.com/jolietjakeblues/rce-cho-mcp.git
cd rce-cho-mcp
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux and macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the package:

```bash
pip install -e .
```

Verify the installation:

```bash
python -m rce_cho_mcp.server
```

If the server starts without errors, stop it with:

```text
Ctrl+C
```

## Add the MCP server to LM Studio

Open:

```text
Developer → MCP Servers
```

Add a new server.

### Windows example

```json
{
  "name": "rce-cho",
  "command": "C:\\AI\\rce-cho-mcp\\.venv\\Scripts\\python.exe",
  "args": [
    "-m",
    "rce_cho_mcp.server"
  ],
  "cwd": "C:\\AI\\rce-cho-mcp"
}
```

### Linux example

```json
{
  "name": "rce-cho",
  "command": "/home/user/rce-cho-mcp/.venv/bin/python",
  "args": [
    "-m",
    "rce_cho_mcp.server"
  ],
  "cwd": "/home/user/rce-cho-mcp"
}
```

### macOS example

```json
{
  "name": "rce-cho",
  "command": "/Users/user/rce-cho-mcp/.venv/bin/python",
  "args": [
    "-m",
    "rce_cho_mcp.server"
  ],
  "cwd": "/Users/user/rce-cho-mcp"
}
```

## Verify the connection

After connecting the MCP server, try:

```text
How many ontology classes are available?
```

or:

```text
Resolve the concept label "Utrecht".
```

or:

```text
Which archaeological rijksmonuments are located in the municipality of Houten?
```

LM Studio should automatically discover and invoke the available MCP tools.

## What this MCP adds

The RCE CHO MCP provides capabilities that local models usually do not possess:

* CEO ontology knowledge
* SKOS concept resolution
* OWMS municipality and province resolution
* Named graph knowledge
* Dataset semantics
* SPARQL validation
* Query execution against the public RCE endpoint

This reduces hallucinations when querying Dutch cultural heritage linked data.

## Current transport

By default, the MCP server uses local `stdio` transport: LM Studio starts it as a local process on the user's machine, using the configuration above.

## Remote HTTP deployment

The server also supports Streamable HTTP transport via `python -m rce_cho_mcp.http_server`, so it can be hosted remotely instead of run locally — see `render.yaml` for a ready-to-use Render deployment. In that case, configure LM Studio with the server's URL instead of a local `command`/`cwd`; consult LM Studio's documentation for the exact remote-server configuration syntax.