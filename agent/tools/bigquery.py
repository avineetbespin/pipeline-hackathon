"""
BigQuery tools for the PipelinePilot agent.

Provides functions to run queries, create views, and inspect tables.
"""

import os
from typing import Any
from google.cloud import bigquery

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "bgus-genai-poc2")
DATASET_ID = os.getenv("BIGQUERY_DATASET", "pipelinepilot")


async def run_query(sql: str, max_results: int = 100) -> dict[str, Any]:
    """
    Run a SQL query against BigQuery.

    Args:
        sql: The SQL query to execute
        max_results: Maximum number of rows to return (default 100)

    Returns:
        dict with query results
    """
    client = bigquery.Client(project=PROJECT_ID)

    try:
        query_job = client.query(sql)
        results = query_job.result(max_results=max_results)

        # Convert to list of dicts
        rows = []
        for row in results:
            rows.append(dict(row))

        return {
            "success": True,
            "row_count": len(rows),
            "total_rows": results.total_rows,
            "rows": rows,
            "schema": [{"name": field.name, "type": field.field_type} for field in results.schema]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def create_view(view_name: str, sql: str, dataset_id: str = DATASET_ID) -> dict[str, Any]:
    """
    Create or replace a BigQuery view.

    Args:
        view_name: Name of the view to create
        sql: SQL query that defines the view
        dataset_id: BigQuery dataset (defaults to pipelinepilot)

    Returns:
        dict with view details
    """
    client = bigquery.Client(project=PROJECT_ID)

    try:
        view_id = f"{PROJECT_ID}.{dataset_id}.{view_name}"
        view = bigquery.Table(view_id)
        view.view_query = sql

        # Create or update the view
        view = client.create_table(view, exists_ok=True)

        return {
            "success": True,
            "view_id": view_id,
            "view_name": view_name,
            "dataset": dataset_id,
            "created": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def list_tables(dataset_id: str = DATASET_ID) -> dict[str, Any]:
    """
    List all tables and views in a BigQuery dataset.

    Args:
        dataset_id: BigQuery dataset (defaults to pipelinepilot)

    Returns:
        dict with list of tables
    """
    client = bigquery.Client(project=PROJECT_ID)

    try:
        tables = client.list_tables(f"{PROJECT_ID}.{dataset_id}")

        table_list = []
        for table in tables:
            table_list.append({
                "table_id": table.table_id,
                "table_type": table.table_type,
                "full_id": f"{PROJECT_ID}.{dataset_id}.{table.table_id}"
            })

        return {
            "success": True,
            "dataset": dataset_id,
            "table_count": len(table_list),
            "tables": table_list
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_table_schema(table_id: str, dataset_id: str = DATASET_ID) -> dict[str, Any]:
    """
    Get the schema of a BigQuery table.

    Args:
        table_id: Table name
        dataset_id: BigQuery dataset (defaults to pipelinepilot)

    Returns:
        dict with table schema
    """
    client = bigquery.Client(project=PROJECT_ID)

    try:
        table_ref = f"{PROJECT_ID}.{dataset_id}.{table_id}"
        table = client.get_table(table_ref)

        schema = []
        for field in table.schema:
            schema.append({
                "name": field.name,
                "type": field.field_type,
                "mode": field.mode,
                "description": field.description or ""
            })

        return {
            "success": True,
            "table_id": table_id,
            "num_rows": table.num_rows,
            "num_bytes": table.num_bytes,
            "created": table.created.isoformat() if table.created else None,
            "schema": schema
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Map function names to implementations
TOOL_FUNCTIONS = {
    "run_query": run_query,
    "create_view": create_view,
    "list_tables": list_tables,
    "get_table_schema": get_table_schema,
}

TOOL_NAMES = list(TOOL_FUNCTIONS.keys())
