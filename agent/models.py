"""
Data models for PipelinePilot agent plans and execution state.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    """Status of a plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"


class ToolType(str, Enum):
    """Category of tool being called."""
    FIVETRAN_READ = "fivetran_read"
    FIVETRAN_WRITE = "fivetran_write"
    BIGQUERY_READ = "bigquery_read"
    BIGQUERY_WRITE = "bigquery_write"
    SCHEDULER = "scheduler"


class Step(BaseModel):
    """A single step in an execution plan."""
    step_id: str = Field(..., description="Unique identifier for this step")
    description: str = Field(..., description="Human-readable description of what this step does")
    tool_name: str = Field(..., description="Name of the tool to call")
    tool_type: ToolType = Field(..., description="Category of tool")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to the tool")
    requires_approval: bool = Field(default=False, description="Whether this step needs user approval")
    status: StepStatus = Field(default=StepStatus.PENDING, description="Current status")
    result: Optional[dict[str, Any]] = Field(default=None, description="Result after execution")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    started_at: Optional[datetime] = Field(default=None, description="When execution started")
    completed_at: Optional[datetime] = Field(default=None, description="When execution completed")


class Plan(BaseModel):
    """An execution plan for accomplishing a user goal."""
    plan_id: str = Field(..., description="Unique identifier for this plan")
    goal: str = Field(..., description="The user's natural language goal")
    steps: list[Step] = Field(default_factory=list, description="Ordered list of steps")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When plan was created")
    created_by: str = Field(default="gemini-3.1-pro-preview", description="Model that created the plan")
    estimated_duration_minutes: Optional[int] = Field(default=None, description="Estimated time to complete")


class ApprovalRequest(BaseModel):
    """A request for user approval of a step."""
    approval_id: str = Field(..., description="Unique identifier")
    plan_id: str = Field(..., description="Associated plan ID")
    step_id: str = Field(..., description="Step requiring approval")
    step_description: str = Field(..., description="What the step will do")
    tool_name: str = Field(..., description="Tool to be called")
    arguments: dict[str, Any] = Field(..., description="Tool arguments")
    cost_estimate: Optional[str] = Field(default=None, description="Estimated cost impact")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved: Optional[bool] = Field(default=None, description="User's decision")
    approved_at: Optional[datetime] = Field(default=None)


class PlanExecution(BaseModel):
    """Runtime state for executing a plan."""
    execution_id: str = Field(..., description="Unique execution ID")
    plan: Plan = Field(..., description="The plan being executed")
    current_step_index: int = Field(default=0, description="Index of current step")
    status: str = Field(default="running", description="Overall execution status")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
