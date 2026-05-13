"""
FastAPI backend for PipelinePilot agent.

Provides HTTP API for:
- Creating and executing plans
- Checking execution status
- Approving steps
"""

import asyncio
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.planner_v2 import StructuredPlanner
from agent.executor import PlanExecutor
from agent.state_memory import InMemoryStateManager
from agent.models import Plan, PlanExecution


app = FastAPI(
    title="PipelinePilot Agent API",
    description="Autonomous data integration agent",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, this would be Firestore)
state_manager = InMemoryStateManager()
planner = StructuredPlanner()
executor = PlanExecutor(state_manager)


class RunRequest(BaseModel):
    """Request to create and execute a plan."""
    goal: str


class RunResponse(BaseModel):
    """Response with plan and execution IDs."""
    plan_id: str
    execution_id: str
    status: str
    message: str


class ApprovalRequest(BaseModel):
    """Request to approve/reject a step."""
    approved: bool


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "pipelinepilot-agent",
        "model": "gemini-3.1-pro-preview"
    }


@app.post("/api/v1/run", response_model=RunResponse)
async def run_plan(request: RunRequest):
    """
    Create a plan for a goal and start executing it.

    The execution runs asynchronously. Use GET /api/v1/run/{execution_id}
    to check status.
    """
    try:
        # Create plan
        plan = planner.create_plan(request.goal)

        # Start execution in background
        async def execute_async():
            await executor.execute_plan(plan)

        # Fire and forget (in production, use proper background task)
        asyncio.create_task(execute_async())

        return RunResponse(
            plan_id=plan.plan_id,
            execution_id=plan.plan_id,  # For simplicity, using same ID
            status="running",
            message=f"Created plan with {len(plan.steps)} steps"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/run/{execution_id}")
async def get_execution_status(execution_id: str):
    """
    Get the status of a running or completed execution.
    """
    execution = state_manager.get_execution(execution_id)

    if not execution:
        # Try to get the plan directly (if execution not yet created)
        plan = state_manager.get_plan(execution_id)
        if plan:
            return {
                "execution_id": execution_id,
                "status": "starting",
                "plan": plan.model_dump()
            }
        raise HTTPException(status_code=404, detail="Execution not found")

    return {
        "execution_id": execution.execution_id,
        "status": execution.status,
        "current_step": execution.current_step_index,
        "total_steps": len(execution.plan.steps),
        "plan": execution.plan.model_dump(),
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
    }


@app.get("/api/v1/plans")
async def list_plans(limit: int = 10):
    """List recent plans."""
    plans = state_manager.list_recent_plans(limit=limit)
    return {
        "plans": [p.model_dump() for p in plans]
    }


@app.post("/api/v1/approvals/{approval_id}")
async def handle_approval(approval_id: str, request: ApprovalRequest):
    """Approve or reject a step."""
    approval = state_manager.get_approval_request(approval_id)

    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if request.approved:
        state_manager.approve_step(approval_id)
    else:
        state_manager.reject_step(approval_id)

    return {
        "approval_id": approval_id,
        "approved": request.approved,
        "message": "Step approved" if request.approved else "Step rejected"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
