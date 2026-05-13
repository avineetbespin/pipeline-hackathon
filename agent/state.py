"""
Firestore-backed state management for plans and approvals.
"""

import os
from datetime import datetime
from typing import Optional
from google.cloud import firestore

from agent.models import Plan, ApprovalRequest, PlanExecution


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "bgus-genai-poc2")


class StateManager:
    """
    Manages persistent state in Firestore.

    Collections:
    - plans: Plan documents
    - approvals: ApprovalRequest documents
    - executions: PlanExecution documents
    """

    def __init__(self, project_id: str = PROJECT_ID):
        self.db = firestore.Client(project=project_id)

    def save_plan(self, plan: Plan) -> None:
        """Save a plan to Firestore."""
        doc_ref = self.db.collection("plans").document(plan.plan_id)
        doc_ref.set(plan.model_dump(mode="json"))

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Retrieve a plan from Firestore."""
        doc_ref = self.db.collection("plans").document(plan_id)
        doc = doc_ref.get()
        if doc.exists:
            return Plan(**doc.to_dict())
        return None

    def save_approval_request(self, approval: ApprovalRequest) -> None:
        """Save an approval request to Firestore."""
        doc_ref = self.db.collection("approvals").document(approval.approval_id)
        doc_ref.set(approval.model_dump(mode="json"))

    def get_approval_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Retrieve an approval request from Firestore."""
        doc_ref = self.db.collection("approvals").document(approval_id)
        doc = doc_ref.get()
        if doc.exists:
            return ApprovalRequest(**doc.to_dict())
        return None

    def approve_step(self, approval_id: str) -> bool:
        """Mark an approval request as approved."""
        doc_ref = self.db.collection("approvals").document(approval_id)
        doc_ref.update({
            "approved": True,
            "approved_at": datetime.utcnow().isoformat()
        })
        return True

    def reject_step(self, approval_id: str) -> bool:
        """Mark an approval request as rejected."""
        doc_ref = self.db.collection("approvals").document(approval_id)
        doc_ref.update({
            "approved": False,
            "approved_at": datetime.utcnow().isoformat()
        })
        return True

    def save_execution(self, execution: PlanExecution) -> None:
        """Save execution state to Firestore."""
        doc_ref = self.db.collection("executions").document(execution.execution_id)
        doc_ref.set(execution.model_dump(mode="json"))

    def get_execution(self, execution_id: str) -> Optional[PlanExecution]:
        """Retrieve execution state from Firestore."""
        doc_ref = self.db.collection("executions").document(execution_id)
        doc = doc_ref.get()
        if doc.exists:
            return PlanExecution(**doc.to_dict())
        return None

    def list_recent_plans(self, limit: int = 10) -> list[Plan]:
        """List recent plans."""
        docs = (
            self.db.collection("plans")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [Plan(**doc.to_dict()) for doc in docs]
