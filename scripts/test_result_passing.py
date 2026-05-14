"""
Test result passing between steps in a multi-step plan.
"""
import asyncio
import sys
sys.path.insert(0, '.')

from agent.planner_v2 import StructuredPlanner
from agent.executor import PlanExecutor

async def test():
    print("="*60)
    print("Testing Result Passing in Multi-Step Plans")
    print("="*60)

    planner = StructuredPlanner()
    executor = PlanExecutor()

    # Test 1: Simple multi-step plan
    print("\n### Test 1: List groups, then list connectors from first group")
    goal = "List all connectors in my first Fivetran group"

    plan = planner.create_plan(goal)

    print(f"\nPlan created with {len(plan.steps)} steps:")
    for idx, step in enumerate(plan.steps):
        print(f"  Step {idx}: {step.description}")
        print(f"    Tool: {step.tool_name}")
        print(f"    Args: {step.arguments}")

    # Execute the plan
    print("\n" + "-"*60)
    print("Executing plan...")
    print("-"*60)

    execution = await executor.execute_plan(plan)

    print("\n" + "="*60)
    print("Execution Results:")
    print("="*60)
    print(f"Status: {execution.status}")

    for idx, step in enumerate(execution.plan.steps):
        print(f"\nStep {idx}: {step.description}")
        print(f"  Status: {step.status}")
        print(f"  Resolved Args: {step.arguments}")
        if step.result:
            result_preview = str(step.result)[:150]
            print(f"  Result: {result_preview}...")
        if step.error:
            print(f"  Error: {step.error}")

    # Check if result passing worked
    success = True
    if len(plan.steps) > 1:
        step_1_args = execution.plan.steps[1].arguments
        if "{{step_0" in str(step_1_args) or "<" in str(step_1_args):
            print("\n❌ FAILED: Step 1 still has unresolved references!")
            success = False
        else:
            print("\n✅ SUCCESS: Result passing worked! Arguments were resolved.")

    return success

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
