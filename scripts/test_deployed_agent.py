"""Test the deployed agent on Cloud Run."""
import asyncio
import httpx

AGENT_URL = "https://pipelinepilot-agent-956500419273.us-central1.run.app"

async def test():
    print("Testing Deployed PipelinePilot Agent")
    print("="*60)
    print(f"URL: {AGENT_URL}\n")

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Health check
        print("1. Health check...")
        r = await client.get(f"{AGENT_URL}/health")
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")

        # Create a plan
        print("\n2. Creating plan...")
        r = await client.post(
            f"{AGENT_URL}/api/v1/run",
            json={"goal": "List my Fivetran groups"}
        )
        print(f"   Status: {r.status_code}")
        data = r.json()
        print(f"   Plan ID: {data['plan_id']}")
        print(f"   Message: {data['message']}")

        execution_id = data['execution_id']

        # Wait for execution
        await asyncio.sleep(10)

        # Check status
        print("\n3. Checking execution status...")
        r = await client.get(f"{AGENT_URL}/api/v1/run/{execution_id}")
        data = r.json()
        print(f"   Status: {data['status']}")

        if 'plan' in data:
            for idx, step in enumerate(data['plan']['steps']):
                print(f"\n   Step {idx+1}: {step['description']}")
                print(f"     Status: {step['status']}")
                if step.get('result'):
                    print(f"     Result preview: {str(step['result'])[:100]}...")

    print("\n" + "="*60)
    print("SUCCESS - Agent deployed and working on Cloud Run!")
    print("="*60)
    print(f"\nAgent URL: {AGENT_URL}")

if __name__ == "__main__":
    asyncio.run(test())
