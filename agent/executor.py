"""
Plan executor - walks through plan steps and calls tools.
"""

import asyncio
import re
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from agent.models import Plan, Step, StepStatus, ApprovalRequest, PlanExecution
from agent.state_memory import InMemoryStateManager
from agent.tools import fivetran, bigquery, scheduler


class PlanExecutor:
    """
    Executes plans step by step, handling approvals for write operations.
    """

    def __init__(self, state_manager: Optional[InMemoryStateManager] = None):
        self.state = state_manager or InMemoryStateManager()
        self.tool_registry = {
            **fivetran.TOOL_FUNCTIONS,
            **bigquery.TOOL_FUNCTIONS,
            **scheduler.TOOL_FUNCTIONS
        }
        # Track results from completed steps for reference
        self.step_results: Dict[int, Any] = {}

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

            # Resolve references to previous step results
            resolved_arguments = self._resolve_step_references(step.arguments, idx)
            step.arguments = resolved_arguments

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

                # Store result for future reference
                self.step_results[idx] = result

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

    def _resolve_step_references(self, arguments: Dict[str, Any], current_step_idx: int) -> Dict[str, Any]:
        """
        Resolve references to previous step results in arguments.

        Supports syntax like:
        - {{step_0.data.items[0].id}} - Extract nested value (preferred)
        - <GROUP_ID_FROM_STEP_N> - Legacy angle bracket syntax (auto-converted)

        Args:
            arguments: Raw arguments dict that may contain {{...}} or <...> references
            current_step_idx: Index of current step (for validation)

        Returns:
            Resolved arguments with actual values
        """
        if not arguments:
            return arguments

        print(f"[Executor] Resolving references for step {current_step_idx}, arguments: {arguments}")

        resolved = {}

        for key, value in arguments.items():
            if isinstance(value, str):
                resolved_value = value

                print(f"[Executor] Processing argument {key}={value}")

                # Handle {{step_N.path}} syntax (preferred)
                if "{{" in value and "}}" in value:
                    pattern = r'\{\{([^}]+)\}\}'
                    matches = re.findall(pattern, value)

                    for match in matches:
                        actual_value = self._extract_from_reference(match, current_step_idx)
                        if actual_value is not None:
                            resolved_value = resolved_value.replace(f"{{{{{match}}}}}", str(actual_value))
                            print(f"[Executor] Resolved reference {key}: {match} => {actual_value}")
                        else:
                            print(f"[Executor] WARNING: Could not resolve reference in {key}: {match}")

                # Handle <DESCRIPTION_FROM_STEP_N> syntax (fallback - try to auto-resolve)
                elif "<" in value and ">" in value and "STEP" in value.upper():
                    # Extract step number from patterns like <GROUP_ID_FROM_STEP_1>
                    step_pattern = r'<[^>]*STEP[_\s]*(\d+)[^>]*>'
                    step_match = re.search(step_pattern, value, re.IGNORECASE)

                    if step_match:
                        step_num = int(step_match.group(1))
                        print(f"[Executor] Found legacy angle bracket reference to step {step_num}")

                        # Try to extract the first ID-like field from that step
                        if step_num < current_step_idx and step_num in self.step_results:
                            result = self.step_results[step_num]

                            # Try common paths for IDs
                            actual_value = None
                            if isinstance(result, dict):
                                # Try data.items[0].id (common Fivetran pattern)
                                if "data" in result and isinstance(result["data"], dict):
                                    items = result["data"].get("items", [])
                                    if items and len(items) > 0 and isinstance(items[0], dict):
                                        actual_value = items[0].get("id")

                                # Fallback: try top-level id
                                if not actual_value:
                                    actual_value = result.get("id")

                            if actual_value:
                                resolved_value = str(actual_value)
                                print(f"[Executor] Auto-resolved angle bracket reference {key}: {value} => {actual_value}")
                            else:
                                print(f"[Executor] WARNING: Could not auto-resolve angle bracket reference in {key}: {value}")
                        else:
                            print(f"[Executor] WARNING: Invalid step reference in {key}: {value}")

                resolved[key] = resolved_value
            else:
                resolved[key] = value

        return resolved

    def _extract_from_reference(self, reference: str, current_step_idx: int) -> Any:
        """
        Extract value from a step reference path.

        Args:
            reference: Path like "step_0.data.items[0].id"
            current_step_idx: Current step index (for validation)

        Returns:
            Extracted value or None if not found
        """
        parts = reference.strip().split(".")

        # First part should be step_N
        if not parts[0].startswith("step_"):
            return None

        try:
            step_idx = int(parts[0].split("_")[1])
        except (IndexError, ValueError):
            return None

        # Validate step index
        if step_idx >= current_step_idx:
            return None

        if step_idx not in self.step_results:
            return None

        # Navigate the path
        current = self.step_results[step_idx]

        for part in parts[1:]:  # Skip step_N, start from first field
            if "[" in part:
                # Handle array indexing like "items[0]"
                field, index_str = part.split("[")
                index = int(index_str.rstrip("]"))

                if isinstance(current, dict) and field in current:
                    current = current[field]
                elif field == "":
                    # Just indexing current, like [0]
                    pass
                else:
                    return None

                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                # Regular field access
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None

        return current

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
