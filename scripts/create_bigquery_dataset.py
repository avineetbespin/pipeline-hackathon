#!/usr/bin/env python3
"""
Create the BigQuery dataset for PipelinePilot.
"""

import os
from google.cloud import bigquery

# Set project
os.environ["GOOGLE_CLOUD_PROJECT"] = "bgus-genai-poc2"

def create_dataset():
    """Create the pipelinepilot dataset if it doesn't exist."""
    client = bigquery.Client(project="bgus-genai-poc2")

    dataset_id = "bgus-genai-poc2.pipelinepilot"

    # Check if dataset exists
    try:
        dataset = client.get_dataset(dataset_id)
        print(f"[OK] Dataset {dataset_id} already exists")
        return
    except Exception as e:
        print(f"Dataset doesn't exist, creating it...")

    # Create dataset
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    dataset.description = "PipelinePilot data warehouse"

    dataset = client.create_dataset(dataset, timeout=30)
    print(f"[OK] Created dataset {dataset_id}")
    print(f"  Location: {dataset.location}")


if __name__ == "__main__":
    create_dataset()
