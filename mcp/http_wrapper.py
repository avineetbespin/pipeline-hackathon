"""
HTTP wrapper for Fivetran MCP server to run on Cloud Run.

The official Fivetran MCP server uses stdio transport (stdin/stdout).
This wrapper exposes it as an HTTP API so it can be deployed to Cloud Run
and called by the PipelinePilot agent backend.
"""

import asyncio
import json
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Fivetran MCP HTTP Wrapper")

# Fivetran API configuration
FIVETRAN_API_KEY = os.getenv("FIVETRAN_API_KEY")
FIVETRAN_API_SECRET = os.getenv("FIVETRAN_API_SECRET")
FIVETRAN_ALLOW_WRITES = os.getenv("FIVETRAN_ALLOW_WRITES", "false").lower() == "true"
BASE_URL = "https://api.fivetran.com"


class MCPToolCall(BaseModel):
    """Request to call an MCP tool."""
    tool_name: str
    arguments: dict[str, Any]


class MCPToolResponse(BaseModel):
    """Response from an MCP tool call."""
    success: bool
    result: dict[str, Any] | None = None
    error: str | None = None


def get_auth_header() -> dict[str, str]:
    """Create Basic Auth header for Fivetran API."""
    import base64
    if not FIVETRAN_API_KEY or not FIVETRAN_API_SECRET:
        raise ValueError("FIVETRAN_API_KEY and FIVETRAN_API_SECRET must be set")
    credentials = f"{FIVETRAN_API_KEY}:{FIVETRAN_API_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json",
        "User-Agent": "pipelinepilot-mcp-http",
    }


async def fivetran_request(
    method: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make a request to the Fivetran API."""
    if method != "GET" and not FIVETRAN_ALLOW_WRITES:
        raise ValueError(
            f"Write operations ({method}) disabled. Set FIVETRAN_ALLOW_WRITES=true"
        )

    url = f"{BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            headers=get_auth_header(),
            params=params,
            json=json_body,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fivetran-mcp-http"}


@app.get("/api/v1/groups")
async def list_groups():
    """List all Fivetran groups."""
    try:
        result = await fivetran_request("GET", "/v1/groups")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/groups/{group_id}/connectors")
async def list_connectors(group_id: str):
    """List all connectors in a group."""
    try:
        result = await fivetran_request("GET", f"/v1/groups/{group_id}/connectors")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/connectors/{connector_id}")
async def get_connector(connector_id: str):
    """Get details of a specific connector."""
    try:
        result = await fivetran_request("GET", f"/v1/connectors/{connector_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/destinations")
async def list_destinations():
    """List all destinations."""
    try:
        result = await fivetran_request("GET", "/v1/destinations")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/connectors")
async def create_connector(connector_config: dict):
    """Create a new connector."""
    try:
        result = await fivetran_request("POST", "/v1/connectors", json_body=connector_config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/connectors/{connector_id}/sync")
async def sync_connector(connector_id: str):
    """Trigger a sync for a connector."""
    try:
        result = await fivetran_request("POST", f"/v1/connectors/{connector_id}/force")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/connectors/{connector_id}/schemas")
async def get_connector_schemas(connector_id: str):
    """Get schema information for a connector."""
    try:
        result = await fivetran_request("GET", f"/v1/connectors/{connector_id}/schemas")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8081"))
    uvicorn.run(app, host="0.0.0.0", port=port)
