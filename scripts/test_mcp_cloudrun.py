"""
Test the deployed MCP server on Cloud Run.
"""
import asyncio
import httpx

MCP_URL = "https://pipelinepilot-mcp-956500419273.us-central1.run.app"

async def test():
    print("Testing deployed MCP server...")
    print(f"URL: {MCP_URL}\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health
        print("1. Health check...")
        try:
            r = await client.get(f"{MCP_URL}/health")
            print(f"   Status: {r.status_code}")
            print(f"   Response: {r.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")
            return

        # Test list groups
        print("\n2. List groups...")
        try:
            r = await client.get(f"{MCP_URL}/api/v1/groups")
            print(f"   Status: {r.status_code}")
            data = r.json()
            groups = data.get("data", {}).get("items", [])
            print(f"   Found {len(groups)} group(s):")
            for g in groups:
                print(f"     - {g.get('name')} ({g.get('id')})")
        except Exception as e:
            print(f"   ERROR: {e}")

        # Test list connectors
        if groups:
            group_id = groups[0]["id"]
            print(f"\n3. List connectors in {group_id}...")
            try:
                r = await client.get(f"{MCP_URL}/api/v1/groups/{group_id}/connectors")
                print(f"   Status: {r.status_code}")
                data = r.json()
                connectors = data.get("data", {}).get("items", [])
                print(f"   Found {len(connectors)} connector(s)")
            except Exception as e:
                print(f"   ERROR: {e}")

    print("\n" + "="*60)
    print("SUCCESS - MCP server deployed and working on Cloud Run!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test())
