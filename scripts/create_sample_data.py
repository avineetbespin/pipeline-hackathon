#!/usr/bin/env python3
"""
Create sample tables in BigQuery for testing PipelinePilot.
"""

import os
from google.cloud import bigquery

os.environ["GOOGLE_CLOUD_PROJECT"] = "bgus-genai-poc2"

def create_sample_tables():
    """Create sample tables with realistic data."""
    client = bigquery.Client(project="bgus-genai-poc2")

    dataset_id = "bgus-genai-poc2.pipelinepilot"

    # Table 1: Connector metadata
    print("Creating connectors table...")
    connectors_schema = [
        bigquery.SchemaField("connector_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("connector_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("destination", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    connectors_table = bigquery.Table(f"{dataset_id}.connectors", schema=connectors_schema)
    connectors_table = client.create_table(connectors_table, exists_ok=True)

    # Insert sample data
    rows_to_insert = [
        {
            "connector_id": "stripe_prod_001",
            "connector_name": "Stripe Production",
            "source_type": "stripe",
            "destination": "bigquery",
            "status": "active",
            "created_at": "2026-05-01T10:00:00",
        },
        {
            "connector_id": "hubspot_crm_001",
            "connector_name": "HubSpot CRM",
            "source_type": "hubspot",
            "destination": "bigquery",
            "status": "active",
            "created_at": "2026-05-02T11:00:00",
        },
        {
            "connector_id": "google_ads_001",
            "connector_name": "Google Ads Main",
            "source_type": "google_ads",
            "destination": "bigquery",
            "status": "active",
            "created_at": "2026-05-03T12:00:00",
        },
    ]

    errors = client.insert_rows_json(connectors_table, rows_to_insert)
    if errors:
        print(f"Errors inserting connectors: {errors}")
    else:
        print(f"[OK] Inserted {len(rows_to_insert)} rows into connectors table")

    # Table 2: Sync logs
    print("\nCreating sync_logs table...")
    sync_logs_schema = [
        bigquery.SchemaField("sync_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("connector_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("connector_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("start_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("end_time", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("rows_synced", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("error_message", "STRING", mode="NULLABLE"),
    ]

    sync_logs_table = bigquery.Table(f"{dataset_id}.sync_logs", schema=sync_logs_schema)
    sync_logs_table = client.create_table(sync_logs_table, exists_ok=True)

    # Insert sample sync data
    sync_rows = [
        {
            "sync_id": "sync-001",
            "connector_id": "stripe_prod_001",
            "connector_name": "Stripe Production",
            "start_time": "2026-05-13T10:00:00",
            "end_time": "2026-05-13T10:15:00",
            "rows_synced": 15000,
            "status": "success",
            "error_message": None,
        },
        {
            "sync_id": "sync-002",
            "connector_id": "hubspot_crm_001",
            "connector_name": "HubSpot CRM",
            "start_time": "2026-05-13T11:00:00",
            "end_time": "2026-05-13T11:05:00",
            "rows_synced": 3200,
            "status": "success",
            "error_message": None,
        },
        {
            "sync_id": "sync-003",
            "connector_id": "google_ads_001",
            "connector_name": "Google Ads Main",
            "start_time": "2026-05-13T12:00:00",
            "end_time": "2026-05-13T12:10:00",
            "rows_synced": 8500,
            "status": "success",
            "error_message": None,
        },
        {
            "sync_id": "sync-004",
            "connector_id": "stripe_prod_001",
            "connector_name": "Stripe Production",
            "start_time": "2026-05-13T14:00:00",
            "end_time": "2026-05-13T14:12:00",
            "rows_synced": 12300,
            "status": "success",
            "error_message": None,
        },
    ]

    errors = client.insert_rows_json(sync_logs_table, sync_rows)
    if errors:
        print(f"Errors inserting sync logs: {errors}")
    else:
        print(f"[OK] Inserted {len(sync_rows)} rows into sync_logs table")

    # Table 3: Revenue data (sample)
    print("\nCreating revenue_summary table...")
    revenue_schema = [
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("revenue", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("transactions", "INTEGER", mode="REQUIRED"),
    ]

    revenue_table = bigquery.Table(f"{dataset_id}.revenue_summary", schema=revenue_schema)
    revenue_table = client.create_table(revenue_table, exists_ok=True)

    revenue_rows = [
        {"date": "2026-05-10", "source": "stripe", "revenue": 15234.50, "transactions": 145},
        {"date": "2026-05-11", "source": "stripe", "revenue": 18456.75, "transactions": 167},
        {"date": "2026-05-12", "source": "stripe", "revenue": 16789.25, "transactions": 152},
        {"date": "2026-05-13", "source": "stripe", "revenue": 19234.80, "transactions": 178},
    ]

    errors = client.insert_rows_json(revenue_table, revenue_rows)
    if errors:
        print(f"Errors inserting revenue: {errors}")
    else:
        print(f"[OK] Inserted {len(revenue_rows)} rows into revenue_summary table")

    print("\n[SUCCESS] All sample tables created!")
    print("\nYou can now try queries like:")
    print("- 'List all tables in pipelinepilot'")
    print("- 'Show me the latest sync logs'")
    print("- 'What is the total revenue from Stripe?'")
    print("- 'Show me connector status'")


if __name__ == "__main__":
    create_sample_tables()
