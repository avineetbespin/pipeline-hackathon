"""
Test the agent FastAPI backend.
"""
import asyncio
import httpx
import json

AGENT_URL = "http://localhost:8080"

async def test():
    print("Testing PipelinePilot Agent API")
    print("="*60)

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Health check
        print("\n1. Health check...")
        r = await client.get(f"{AGENT_URL}/health")
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")

        # Create and run a plan
        print("\n2. Creating plan...")
        r = await client.post(
            f"{AGENT_URL}/api/v1/run",
            json={"goal": "What Fivetran groups do I have?"}
        )
        print(f"   Status: {r.status_code}")
        data = r.json()
        print(f"   Plan ID: {data['plan_id']}")
        print(f"   Status: {data['status']}")

        execution_id = data['execution_id']

        # Wait a bit for execution
        await asyncio.sleep(5)

        # Check status
        print("\n3. Checking execution status...")
        r = await client.get(f"{AGENT_URL}/api/v1/run/{execution_id}")
        data = r.json()
        print(f"   Status: {data['status']}")
        if 'current_step' in data:
            print(f"   Steps: {data['current_step']}/{data['total_steps']}")

        # Show plan details
        print("\n4. Plan details:")
        for idx, step in enumerate(data['plan']['steps']):
            print(f"   Step {idx+1}: {step['description']}")
            print(f"     Tool: {step['tool_name']}")
            print(f"     Status: {step['status']}")
            if step.get('result'):
                print(f"     Result: {str(step['result'])[:100]}...")

    print("\n" + "="*60)
    print("Agent API is working!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test())
