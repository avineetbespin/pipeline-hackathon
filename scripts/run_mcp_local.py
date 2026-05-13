"""
Run the MCP HTTP wrapper locally with credentials from Secret Manager.
"""
import os
import sys
from google.cloud import secretmanager

def load_and_run():
    # Load credentials from Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    project_id = "bgus-genai-poc2"

    def get_secret(secret_id):
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("utf-8")

    os.environ["FIVETRAN_API_KEY"] = get_secret("fivetran-api-key")
    os.environ["FIVETRAN_API_SECRET"] = get_secret("fivetran-api-secret")
    os.environ["FIVETRAN_ALLOW_WRITES"] = "false"
    os.environ["PORT"] = "8081"

    print("OK - Loaded Fivetran credentials from Secret Manager")
    print("Starting MCP HTTP wrapper on http://localhost:8081")
    print("Press Ctrl+C to stop\n")

    # Import and run the server
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from mcp.http_wrapper import app
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)


if __name__ == "__main__":
    load_and_run()
