"""
Fivetran tool wrapper - calls the deployed MCP HTTP server.

This module provides Python functions that the Gemini agent can call
to interact with Fivetran (list groups, connectors, create connectors, etc.).
"""

import os
from typing import Any
import httpx

# MCP server URL - defaults to Cloud Run, can override for local dev
MCP_BASE_URL = os.getenv(
    "FIVETRAN_MCP_URL",
    "https://pipelinepilot-mcp-956500419273.us-central1.run.app"
)


async def list_groups() -> dict[str, Any]:
    """
    List all Fivetran groups (workspaces).

    Returns:
        dict with "data" containing list of groups
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{MCP_BASE_URL}/api/v1/groups")
        response.raise_for_status()
        return response.json()


async def list_connectors(group_id: str) -> dict[str, Any]:
    """
    List all connectors in a specific group.

    Args:
        group_id: The Fivetran group ID

    Returns:
        dict with "data" containing list of connectors
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{MCP_BASE_URL}/api/v1/groups/{group_id}/connectors")
        response.raise_for_status()
        return response.json()


async def get_connector(connector_id: str) -> dict[str, Any]:
    """
    Get details of a specific connector.

    Args:
        connector_id: The Fivetran connector ID

    Returns:
        dict with connector details
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{MCP_BASE_URL}/api/v1/connectors/{connector_id}")
        response.raise_for_status()
        return response.json()


async def list_destinations() -> dict[str, Any]:
    """
    List all Fivetran destinations.

    Returns:
        dict with "data" containing list of destinations
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{MCP_BASE_URL}/api/v1/destinations")
        response.raise_for_status()
        return response.json()


async def create_connector(connector_config: dict[str, Any]) -> dict[str, Any]:
    """
    Create a new Fivetran connector.

    Args:
        connector_config: Connector configuration dict

    Returns:
        dict with created connector details
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{MCP_BASE_URL}/api/v1/connectors",
            json=connector_config
        )
        response.raise_for_status()
        return response.json()


async def sync_connector(connector_id: str) -> dict[str, Any]:
    """
    Trigger a sync for a connector.

    Args:
        connector_id: The Fivetran connector ID

    Returns:
        dict with sync status
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{MCP_BASE_URL}/api/v1/connectors/{connector_id}/sync")
        response.raise_for_status()
        return response.json()


async def get_connector_schemas(connector_id: str) -> dict[str, Any]:
    """
    Get schema information for a connector.

    Args:
        connector_id: The Fivetran connector ID

    Returns:
        dict with schema details
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{MCP_BASE_URL}/api/v1/connectors/{connector_id}/schemas")
        response.raise_for_status()
        return response.json()


# Map function names to implementations for tool calling
TOOL_FUNCTIONS = {
    "list_groups": list_groups,
    "list_connectors": list_connectors,
    "list_destinations": list_destinations,
    "get_connector": get_connector,
    "get_connector_schemas": get_connector_schemas,
    "create_connector": create_connector,
    "sync_connector": sync_connector,
}

# List of all available tool names
TOOL_NAMES = list(TOOL_FUNCTIONS.keys())
