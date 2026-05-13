"""
Test the MCP HTTP wrapper locally before deploying to Cloud Run.
"""
import asyncio
import sys
from google.cloud import secretmanager

# Load Fivetran credentials from Secret Manager
def load_fivetran_creds():
    client = secretmanager.SecretManagerServiceClient()
    project_id = "bgus-genai-poc2"

    def get_secret(secret_id):
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("utf-8")

    import os
    os.environ["FIVETRAN_API_KEY"] = get_secret("fivetran-api-key")
    os.environ["FIVETRAN_API_SECRET"] = get_secret("fivetran-api-secret")
    os.environ["FIVETRAN_ALLOW_WRITES"] = "false"
    print("OK - Loaded Fivetran credentials from Secret Manager")


async def test_mcp():
    """Test the MCP wrapper endpoints."""
    import httpx

    base_url = "http://localhost:8081"

    print("\n" + "="*60)
    print("Testing MCP HTTP Wrapper")
    print("="*60)

    async with httpx.AsyncClient() as client:
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            print("\n   Make sure the MCP server is running:")
            print("   python mcp/http_wrapper.py")
            sys.exit(1)

        # Test list groups
        print("\n2. Testing list groups...")
        try:
            response = await client.get(f"{base_url}/api/v1/groups")
            data = response.json()
            print(f"   Status: {response.status_code}")
            groups = data.get("data", {}).get("items", [])
            print(f"   Found {len(groups)} group(s):")
            for g in groups:
                print(f"     - {g.get('name')} ({g.get('id')})")
        except Exception as e:
            print(f"   ✗ Failed: {e}")

        # Test list connectors
        if groups:
            group_id = groups[0]["id"]
            print(f"\n3. Testing list connectors in group {group_id}...")
            try:
                response = await client.get(f"{base_url}/api/v1/groups/{group_id}/connectors")
                data = response.json()
                print(f"   Status: {response.status_code}")
                connectors = data.get("data", {}).get("items", [])
                print(f"   Found {len(connectors)} connector(s)")
                for c in connectors[:5]:
                    print(f"     - {c.get('schema')} ({c.get('service')})")
            except Exception as e:
                print(f"   ✗ Failed: {e}")

    print("\n" + "="*60)
    print("✓ MCP HTTP wrapper is working!")
    print("="*60)


if __name__ == "__main__":
    load_fivetran_creds()
    asyncio.run(test_mcp())
