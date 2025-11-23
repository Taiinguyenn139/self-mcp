# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a collection of self-developed MCP (Model Context Protocol) servers. The project uses Python 3.12+ with the `mcp` library to build custom tool servers that can be integrated with Claude and other LLM applications.

## Architecture

The project consists of two main components:

1. **MCP Servers** - Individual server implementations that expose tools via the MCP protocol:
   - `weather.py`: Weather server using the National Weather Service API, providing `get_alert` and `get_forecast` tools
   - Each server uses `FastMCP` from `mcp.server.fastmcp` and runs with stdio transport

2. **MCP Client** - A reusable client implementation (`client.py`):
   - `MCPClient` class that connects to MCP servers via stdio
   - Integrates with Anthropic's Claude API to process queries using available tools
   - Handles the complete tool execution loop (tool discovery, execution, and response)
   - Supports both Python (.py) and JavaScript (.js) MCP servers

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv
uv sync
```

### Running MCP Servers

Each server can be run standalone with stdio transport:
```bash
python weather.py
```

### Testing with the Client

The client connects to an MCP server and provides an interactive chat interface:
```bash
python client.py <path_to_server_script>
# Example:
python client.py weather.py
```

**Important**: The client requires an `ANTHROPIC_API_KEY` environment variable. Create a `.env` file or set it in your environment.

## Adding New MCP Servers

When creating a new MCP server in this repository:

1. Use `FastMCP` from `mcp.server.fastmcp`
2. Initialize with a descriptive name: `mcp = FastMCP("server-name")`
3. Define tools using the `@mcp.tool()` decorator with proper type hints and docstrings
4. Run the server with `mcp.run(transport='stdio')` in the `main()` function
5. Follow the pattern in `weather.py` for consistent structure

Tool functions should:
- Use async when making external requests
- Include comprehensive docstrings with Args section
- Return user-friendly string responses (not raw JSON)
- Handle errors gracefully and return descriptive error messages
