"""
Enhanced Gemini planner that creates structured execution plans.
"""

import json
import os
import uuid
from datetime import datetime

from google import genai
from google.genai import types

from agent.models import Plan, Step, ToolType, StepStatus


os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", "bgus-genai-poc2")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


PLANNING_PROMPT = """You are PipelinePilot, an AI agent that creates data pipeline execution plans.

Given a user goal, you create a structured plan with specific steps.

Available tools:
**Fivetran (READ):**
- list_groups() - List all Fivetran groups/workspaces. Returns: {"data": {"items": [{"id": "...", "name": "..."}]}}
- list_connectors(group_id) - List connectors in a group. Returns: {"data": {"items": [{"id": "...", "schema": "...", "service": "..."}]}}
- get_connector(connector_id) - Get connector details
- list_destinations() - List all destinations. Returns: {"data": {"items": [{"id": "...", "group_id": "...", "service": "bigquery"}]}}
- get_connector_schemas(connector_id) - Get schema info

**Fivetran (WRITE - requires approval):**
- create_connector(connector_config) - Create new connector
- sync_connector(connector_id) - Trigger a sync

**BigQuery (READ):**
- list_tables(dataset_id) - List tables in dataset
- get_table_schema(table_id) - Get table schema
- run_query(sql) - Run a SELECT query

**BigQuery (WRITE - requires approval):**
- create_view(view_name, sql) - Create or update a view

**Result References:**
You can reference results from previous steps using {{step_N.path}} syntax (note: no ".result" - the step result IS the data):
- {{step_0.data.items[0].id}} - Get the first group's ID from list_groups
- {{step_1.data.items[0].id}} - Get the first connector's ID from list_connectors
- {{step_2.destination_id}} - Get a specific field

Example multi-step plan:
{
  "steps": [
    {
      "description": "List all Fivetran groups",
      "tool_name": "list_groups",
      "tool_type": "fivetran_read",
      "arguments": {},
      "requires_approval": false
    },
    {
      "description": "List connectors in the first group",
      "tool_name": "list_connectors",
      "tool_type": "fivetran_read",
      "arguments": {
        "group_id": "{{step_0.data.items[0].id}}"
      },
      "requires_approval": false
    }
  ],
  "estimated_duration_minutes": 2
}

Important rules:
1. ALL write operations (create_connector, sync_connector, create_view) MUST have requires_approval: true
2. Read operations should have requires_approval: false
3. tool_type must be one of: fivetran_read, fivetran_write, bigquery_read, bigquery_write
4. Break complex goals into small, sequential steps
5. Always start by discovering current state (list groups, list connectors, etc.)
6. Use {{step_N.result.path}} to reference values from previous steps
7. Only reference steps that come BEFORE the current step (no forward references)
"""


class StructuredPlanner:
    """Creates structured execution plans using Gemini."""

    def __init__(self, model_id: str = "gemini-3.1-pro-preview"):
        self.model_id = model_id
        self.client = genai.Client()

    def create_plan(self, goal: str) -> Plan:
        """
        Create a structured execution plan for a user goal.

        Args:
            goal: Natural language description of what user wants

        Returns:
            Plan object with structured steps
        """
        print(f"\n[Planner] Creating plan for goal: {goal}")

        # Ask Gemini to create the plan
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[
                {"role": "user", "parts": [{"text": PLANNING_PROMPT}]},
                {"role": "user", "parts": [{"text": f"User goal: {goal}\n\nCreate an execution plan (JSON only):"}]},
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
            ),
        )

        # Parse the JSON response
        response_text = response.text.strip()

        # Remove markdown code fences if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        try:
            plan_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"[Planner] Failed to parse JSON: {e}")
            print(f"[Planner] Response was: {response_text[:500]}")
            raise ValueError(f"Gemini did not return valid JSON: {e}")

        # Build Plan object
        plan_id = str(uuid.uuid4())
        steps = []

        for idx, step_data in enumerate(plan_data.get("steps", [])):
            step = Step(
                step_id=f"{plan_id}-step-{idx}",
                description=step_data["description"],
                tool_name=step_data["tool_name"],
                tool_type=ToolType(step_data["tool_type"]),
                arguments=step_data.get("arguments", {}),
                requires_approval=step_data.get("requires_approval", False),
                status=StepStatus.PENDING
            )
            steps.append(step)

        plan = Plan(
            plan_id=plan_id,
            goal=goal,
            steps=steps,
            estimated_duration_minutes=plan_data.get("estimated_duration_minutes")
        )

        print(f"[Planner] Created plan with {len(steps)} steps")
        for idx, step in enumerate(steps):
            approval_mark = " [NEEDS APPROVAL]" if step.requires_approval else ""
            print(f"  {idx+1}. {step.description}{approval_mark}")

        return plan


def main():
    """Demo the structured planner."""
    print("="*60)
    print("PipelinePilot - Structured Planner Demo")
    print("="*60)

    planner = StructuredPlanner()

    # Example goal
    goal = "Show me what Fivetran connectors I currently have set up"

    plan = planner.create_plan(goal)

    print("\n" + "="*60)
    print("Plan created successfully!")
    print("="*60)
    print(f"Plan ID: {plan.plan_id}")
    print(f"Goal: {plan.goal}")
    print(f"Steps: {len(plan.steps)}")
    print(f"Estimated duration: {plan.estimated_duration_minutes} minutes")


if __name__ == "__main__":
    main()
