"""
Test script for result passing between steps.
"""

import asyncio
import os
import sys

# Set env vars
os.environ["GOOGLE_CLOUD_PROJECT"] = "bgus-genai-poc2"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["BIGQUERY_DATASET"] = "pipelinepilot"

# Add agent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.planner_v2 import StructuredPlanner
from agent.executor import PlanExecutor


async def test_result_passing():
    """Test that results from step N can be used in step N+1"""

    print("="*60)
    print("Testing Result Passing Between Steps")
    print("="*60)

    # Create a plan that requires result passing
    print("\n1. Creating plan...")
    planner = StructuredPlanner()

    # This goal should create:
    # Step 1: list_groups() -> get group IDs
    # Step 2: list_connectors(group_id={{step_0.result...}})
    goal = "Show me all connectors in my first Fivetran group"

    plan = planner.create_plan(goal)

    print(f"\n2. Plan created with {len(plan.steps)} steps:")
    for idx, step in enumerate(plan.steps):
        print(f"   Step {idx}: {step.description}")
        print(f"      Tool: {step.tool_name}")
        print(f"      Args: {step.arguments}")

    # Execute the plan
    print("\n3. Executing plan...")
    executor = PlanExecutor()

    try:
        execution = await executor.execute_plan(plan)

        print("\n4. Execution complete!")
        print(f"   Status: {execution.status}")

        # Check results
        print("\n5. Checking results:")
        for idx, step in enumerate(execution.plan.steps):
            print(f"\n   Step {idx}: {step.description}")
            print(f"      Status: {step.status}")
            print(f"      Arguments (after resolution): {step.arguments}")

            if step.result:
                # Show abbreviated result
                result_str = str(step.result)
                if len(result_str) > 200:
                    result_str = result_str[:200] + "..."
                print(f"      Result: {result_str}")

        # Verify that step 1 got a real group_id, not a placeholder
        if len(plan.steps) >= 2:
            step_1_args = plan.steps[1].arguments
            if "group_id" in step_1_args:
                group_id = step_1_args["group_id"]
                print(f"\n6. Result passing verification:")
                print(f"   Step 1 group_id argument: {group_id}")

                if "{{" in group_id or "<" in group_id:
                    print("   ❌ FAILED: group_id still contains placeholder")
                else:
                    print("   ✅ SUCCESS: group_id was resolved from step 0 result")

    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_result_passing())
