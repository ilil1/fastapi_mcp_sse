# FastAPI MCP SSE
[![smithery badge](https://smithery.ai/badge/@ilil1/fastapi_mcp_sse)](https://smithery.ai/server/@ilil1/fastapi_mcp_sse)

<p align="center">
  <strong>English</strong> | <a href="/README.zh-CN.md">简体中文</a>
</p>

A Server-Sent Events (SSE) implementation using FastAPI framework with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) integration.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard that enables AI models to interact with external tools and data sources. MCP solves several key challenges in AI development:

- **Context limitations**: Allows models to access up-to-date information beyond their training data
- **Tool integration**: Provides a standardized way for models to use external tools and APIs
- **Interoperability**: Creates a common interface between different AI models and tools
- **Extensibility**: Makes it easy to add new capabilities to AI systems without retraining

This project demonstrates how to implement MCP using Server-Sent Events (SSE) in a FastAPI web application.

## Description

This project demonstrates how to implement Server-Sent Events (SSE) using the FastAPI framework while integrating Model Context Protocol (MCP) functionality. The key feature is the seamless integration of MCP's SSE capabilities within a full-featured FastAPI web application that includes custom routes.

## Features

- Server-Sent Events (SSE) implementation with MCP
- FastAPI framework integration with custom routes
- Unified web application with both MCP and standard web endpoints
- Customizable route structure
- Clean separation of concerns between MCP and web functionality

## Architecture

This project showcases a modular architecture that:

1. Integrates MCP SSE endpoints (`/sse` and `/messages/`) into a FastAPI application
2. Provides standard web routes (`/`, `/about`, `/status`, `/docs`, `/redoc`)
3. Demonstrates how to maintain separation between MCP functionality and web routes

## Installation & Usage Options

### Installing via Smithery

To install FastAPI SSE MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@ilil1/fastapi_mcp_sse):

```bash
npx -y @smithery/cli install @ilil1/fastapi_mcp_sse --client claude
```

### Prerequisites

Install [UV Package Manager](https://docs.astral.sh/uv/) - A fast Python package installer written in Rust:

```cmd
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Option 1: Quick Run Without Installation

Run the application directly without cloning the repository using UV's execution tool:

```cmd
uvx --from git+https://github.com/panz2018/fastapi_mcp_sse.git start
```

### Option 2: Full Installation

#### Create Virtual Environment

Create an isolated Python environment for the project:

```cmd
uv venv
```

#### Activate Virtual Environment

Activate the virtual environment to use it:

```cmd
.venv\Scripts\activate
```

#### Install Dependencies

Install all required packages:

```cmd
uv pip install -r pyproject.toml
```

#### Start the Integrated Server

Launch the integrated FastAPI server with MCP SSE functionality:

```cmd
python src/server.py
```

or

```cmd
uv run start
```

### Available Endpoints

After starting the server (using either Option 1 or Option 2), the following endpoints will be available:

- Main server: http://localhost:8000
- Standard web routes:
  - Home page: http://localhost:8000/
  - About page: http://localhost:8000/about
  - Status API: http://localhost:8000/status
  - Documentation (Swagger UI): http://localhost:8000/docs
  - Documentation (ReDoc): http://localhost:8000/redoc
- MCP SSE endpoints:
  - SSE endpoint: http://localhost:8000/sse
  - Message posting: http://localhost:8000/messages/

### Debug with MCP Inspector

For testing and debugging MCP functionality, use the MCP Inspector:

```cmd
mcp dev ./src/weather.py
```

### Connect to MCP Inspector

1. Open MCP Inspector at http://localhost:5173
2. Configure the connection:
   - Set Transport Type to `SSE`
   - Enter URL: http://localhost:8000/sse
   - Click `Connect`

### Test the Functions

1. Navigate to `Tools` section
2. Click `List Tools` to see available functions:
   - `get_alerts` : Get weather alerts
   - `get_forcast` : Get weather forecast
3. Select a function
4. Enter required parameters
5. Click `Run Tool` to execute

## Extending the Application

### Adding Custom Routes

The application structure makes it easy to add new routes using FastAPI's APIRouter:

1. Define new route handlers in routes.py using the APIRouter:

   ```python
   @router.get("/new-route")
   async def new_route():
       return {"message": "This is a new route"}
   ```

2. All routes defined with the router will be automatically included in the main application

### Customizing MCP Integration

The MCP SSE functionality is integrated in server.py through:

- Creating an SSE transport
- Setting up an SSE handler
- Adding MCP routes to the FastAPI application

## Integration with [Continue](https://www.continue.dev/)

To use this MCP server with the Continue VS Code extension, add the following configuration to your Continue settings:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "name": "weather",
          "type": "sse",
          "url": "http://localhost:8000/sse"
        }
      }
    ]
  }
}
```
