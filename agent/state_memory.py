"""
In-memory state manager (for development/testing).

In production, this would be replaced with Firestore Native mode.
For the hackathon demo, in-memory state is sufficient.
"""

from datetime import datetime
from typing import Optional

from agent.models import Plan, ApprovalRequest, PlanExecution


class InMemoryStateManager:
    """
    In-memory implementation of state management.
    Data is lost when the process restarts.
    """

    def __init__(self):
        self.plans: dict[str, Plan] = {}
        self.approvals: dict[str, ApprovalRequest] = {}
        self.executions: dict[str, PlanExecution] = {}

    def save_plan(self, plan: Plan) -> None:
        """Save a plan to memory."""
        self.plans[plan.plan_id] = plan

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Retrieve a plan from memory."""
        return self.plans.get(plan_id)

    def save_approval_request(self, approval: ApprovalRequest) -> None:
        """Save an approval request to memory."""
        self.approvals[approval.approval_id] = approval

    def get_approval_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Retrieve an approval request from memory."""
        return self.approvals.get(approval_id)

    def approve_step(self, approval_id: str) -> bool:
        """Mark an approval request as approved."""
        approval = self.approvals.get(approval_id)
        if approval:
            approval.approved = True
            approval.approved_at = datetime.utcnow()
            return True
        return False

    def reject_step(self, approval_id: str) -> bool:
        """Mark an approval request as rejected."""
        approval = self.approvals.get(approval_id)
        if approval:
            approval.approved = False
            approval.approved_at = datetime.utcnow()
            return True
        return False

    def save_execution(self, execution: PlanExecution) -> None:
        """Save execution state to memory."""
        self.executions[execution.execution_id] = execution

    def get_execution(self, execution_id: str) -> Optional[PlanExecution]:
        """Retrieve execution state from memory."""
        return self.executions.get(execution_id)

    def list_recent_plans(self, limit: int = 10) -> list[Plan]:
        """List recent plans."""
        sorted_plans = sorted(
            self.plans.values(),
            key=lambda p: p.created_at,
            reverse=True
        )
        return sorted_plans[:limit]
