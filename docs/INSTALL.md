# INSTALL.md

# Installation

## Requirements

* Python 3.11 or newer
* Git
* Internet access to the public RCE CHO SPARQL endpoint

## Clone the repository

```bash
git clone https://github.com/jolietjakeblues/rce-cho-mcp.git
cd rce-cho-mcp
```

## Create a virtual environment

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

## Install the package

```bash
pip install -e .
```

This installs the MCP server in editable mode.

## Verify the installation

Start the MCP server:

```bash
python -m rce_cho_mcp.server
```

If the installation succeeded, the server starts and waits for MCP connections.

Stop the server with:

```text
Ctrl+C
```

## Compile all source files

Optional but useful during development:

```bash
python -m compileall src/rce_cho_mcp
```

## Development workflow

Typical development cycle:

```bash
git pull
python -m compileall src/rce_cho_mcp
python -m rce_cho_mcp.server
git add .
git commit -m "message"
git push
```

## Current status

The project is currently in beta stage (v0.2.0-beta).

The API, tool names and capabilities may still change between releases.
