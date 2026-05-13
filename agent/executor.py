"""
Plan executor - walks through plan steps and calls tools.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional

from agent.models import Plan, Step, StepStatus, ApprovalRequest, PlanExecution
from agent.state_memory import InMemoryStateManager
from agent.tools import fivetran, bigquery


class PlanExecutor:
    """
    Executes plans step by step, handling approvals for write operations.
    """

    def __init__(self, state_manager: Optional[InMemoryStateManager] = None):
        self.state = state_manager or InMemoryStateManager()
        self.tool_registry = {
            **fivetran.TOOL_FUNCTIONS,
            **bigquery.TOOL_FUNCTIONS
        }

    async def execute_plan(self, plan: Plan) -> PlanExecution:
        """
        Execute a plan step by step.

        Args:
            plan: The plan to execute

        Returns:
            PlanExecution with results
        """
        execution_id = str(uuid.uuid4())
        execution = PlanExecution(
            execution_id=execution_id,
            plan=plan,
            status="running"
        )

        # Save initial state
        self.state.save_plan(plan)
        self.state.save_execution(execution)

        print(f"\n[Executor] Starting execution {execution_id}")
        print(f"[Executor] Goal: {plan.goal}")
        print(f"[Executor] Steps: {len(plan.steps)}\n")

        for idx, step in enumerate(plan.steps):
            execution.current_step_index = idx
            print(f"[Executor] Step {idx+1}/{len(plan.steps)}: {step.description}")

            # Check if approval is required
            if step.requires_approval:
                print(f"[Executor] Step requires approval - creating approval request")
                approval_id = await self._request_approval(plan, step)
                step.status = StepStatus.WAITING_APPROVAL
                self.state.save_plan(plan)

                print(f"[Executor] Waiting for approval (ID: {approval_id})")
                print(f"[Executor] In production, this would poll Firestore for approval")
                print(f"[Executor] For now, automatically approving...")

                # In production, we'd poll here. For demo, auto-approve
                await asyncio.sleep(1)
                self.state.approve_step(approval_id)

            # Execute the step
            step.status = StepStatus.IN_PROGRESS
            step.started_at = datetime.utcnow()

            try:
                result = await self._execute_step(step)
                step.result = result
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.utcnow()

                print(f"[Executor] Step completed successfully")
                if result:
                    print(f"[Executor] Result: {str(result)[:200]}...")

            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                step.completed_at = datetime.utcnow()

                print(f"[Executor] Step failed: {e}")
                execution.status = "failed"
                break

            # Save progress
            self.state.save_plan(plan)
            self.state.save_execution(execution)

        # Mark execution as complete
        if execution.status == "running":
            execution.status = "completed"

        execution.completed_at = datetime.utcnow()
        self.state.save_execution(execution)

        print(f"\n[Executor] Execution {execution.status}")
        return execution

    async def _execute_step(self, step: Step) -> dict:
        """Execute a single step by calling the appropriate tool."""
        tool_func = self.tool_registry.get(step.tool_name)

        if not tool_func:
            raise ValueError(f"Unknown tool: {step.tool_name}")

        # Call the tool function
        result = await tool_func(**step.arguments)
        return result

    async def _request_approval(self, plan: Plan, step: Step) -> str:
        """Create an approval request for a step."""
        approval_id = str(uuid.uuid4())

        approval = ApprovalRequest(
            approval_id=approval_id,
            plan_id=plan.plan_id,
            step_id=step.step_id,
            step_description=step.description,
            tool_name=step.tool_name,
            arguments=step.arguments,
            cost_estimate=self._estimate_cost(step)
        )

        self.state.save_approval_request(approval)
        return approval_id

    def _estimate_cost(self, step: Step) -> Optional[str]:
        """Estimate the cost impact of a step."""
        if "create_connector" in step.tool_name:
            return "Fivetran connector cost depends on data volume synced"
        return None


async def main():
    """Demo the executor."""
    print("="*60)
    print("PipelinePilot - Executor Demo")
    print("="*60)

    # Import planner to create a plan
    from agent.planner_v2 import StructuredPlanner

    planner = StructuredPlanner()
    plan = planner.create_plan("List my Fivetran connectors")

    # Execute the plan
    executor = PlanExecutor()
    execution = await executor.execute_plan(plan)

    print("\n" + "="*60)
    print("Execution Results:")
    print("="*60)
    print(f"Status: {execution.status}")
    print(f"Duration: {(execution.completed_at - execution.started_at).total_seconds():.1f}s")

    for idx, step in enumerate(execution.plan.steps):
        print(f"\nStep {idx+1}: {step.description}")
        print(f"  Status: {step.status}")
        if step.result:
            print(f"  Result: {str(step.result)[:150]}...")


if __name__ == "__main__":
    asyncio.run(main())
