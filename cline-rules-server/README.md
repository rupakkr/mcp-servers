# CLine Rules MCP Server

An MCP (Model Context Protocol) server that provides access to Global and Local Rules for the CLine extension.

## Overview

This server exposes two MCP tools that allow CLine to access rule files written in Markdown format:
- `get_global_rules()`: Returns the contents of `rules/global_rules.md`
- `get_local_rules()`: Returns the contents of `rules/local_rules.md`

## Setup

1. Ensure you have Python 3.10 or higher installed
2. Install dependencies:
   ```bash
   pip install -e .
   ```
   or using uv:
   ```bash
   uv sync
   ```

3. Place your rule files in the `rules/` directory:
   - `rules/global_rules.md`: Global rules that apply to all projects
   - `rules/local_rules.md`: Project-specific rules

## Usage

Run the MCP server:
```bash
cline-rules
```

The server will start and communicate via stdio, making the tools available to MCP clients.

## File Structure

```
cline-rules-server/
├── rules/
│   ├── global_rules.md
│   └── local_rules.md
├── rules_server.py
├── pyproject.toml
└── README.md
```

## Integration with CLine

Configure CLine to use this MCP server by adding it to your MCP configuration. The server will provide the `get_global_rules` and `get_local_rules` tools that CLine can use to access the rule files.

## Customization

Edit the Markdown files in the `rules/` directory to customize the rules for your needs. The server will automatically read these files when the tools are called.
