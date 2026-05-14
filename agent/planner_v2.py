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

CRITICAL: When referencing previous step results, you MUST use the exact syntax: {{step_N.path}}
DO NOT use angle brackets like <SOMETHING_FROM_STEP_N>. Always use double curly braces.

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

**Scheduler (READ):**
- list_scheduled_jobs() - List all Cloud Scheduler jobs

**Scheduler (WRITE - requires approval):**
- create_scheduled_job(job_name, schedule, query_sql, slack_webhook_url, threshold_condition, description) - Create scheduled query with Slack alerts
- delete_scheduled_job(job_name) - Delete a scheduled job
- pause_scheduled_job(job_name) - Pause a job
- resume_scheduled_job(job_name) - Resume a job

**Alerts (WRITE - requires approval):**
- send_slack_alert(webhook_url, message, threshold_breach, is_error) - Send alert to Slack

**Result References:**
You MUST reference results from previous steps using {{step_N.path}} syntax with double curly braces:
- {{step_0.data.items[0].id}} - Get the first group's ID from list_groups
- {{step_1.data.items[0].id}} - Get the first connector's ID from list_connectors
- {{step_2.destination_id}} - Get a specific field

IMPORTANT: Always use {{step_N.path}} with DOUBLE curly braces. Never use angle brackets like <GROUP_ID_FROM_STEP_1>.

Example 1 - Multi-step plan with result references:
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
    },
    {
      "description": "Get details of the first connector",
      "tool_name": "get_connector",
      "tool_type": "fivetran_read",
      "arguments": {
        "connector_id": "{{step_1.data.items[0].id}}"
      },
      "requires_approval": false
    }
  ],
  "estimated_duration_minutes": 2
}

Example 2 - Stripe revenue query:
{
  "steps": [
    {
      "description": "List Fivetran groups",
      "tool_name": "list_groups",
      "tool_type": "fivetran_read",
      "arguments": {},
      "requires_approval": false
    },
    {
      "description": "List connectors to find Stripe",
      "tool_name": "list_connectors",
      "tool_type": "fivetran_read",
      "arguments": {
        "group_id": "{{step_0.data.items[0].id}}"
      },
      "requires_approval": false
    },
    {
      "description": "Query Stripe revenue",
      "tool_name": "run_query",
      "tool_type": "bigquery_read",
      "arguments": {
        "sql": "SELECT SUM(amount)/100.0 as revenue FROM pipelinepilot.revenue_summary WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)"
      },
      "requires_approval": false
    }
  ],
  "estimated_duration_minutes": 3
}

Important rules:
1. ALL write operations (create_connector, sync_connector, create_view, create_scheduled_job, send_slack_alert, delete_scheduled_job) MUST have requires_approval: true
2. Read operations should have requires_approval: false
3. tool_type must be one of: fivetran_read, fivetran_write, bigquery_read, bigquery_write, scheduler_read, scheduler_write, alerts_write
4. Break complex goals into small, sequential steps
5. Always start by discovering current state (list groups, list connectors, etc.)
6. Use {{step_N.result.path}} to reference values from previous steps
7. Only reference steps that come BEFORE the current step (no forward references)
8. For scheduled alerts, use cron syntax: "0 9 * * *" = daily at 9am, "0 */6 * * *" = every 6 hours
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

        # Post-process: Fix angle bracket references
        plan_data = self._fix_angle_bracket_references(plan_data)

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

    def _fix_angle_bracket_references(self, plan_data: dict) -> dict:
        """
        Post-process plan to fix angle bracket references like <GROUP_ID_FROM_STEP_1>
        and convert them to proper {{step_N.path}} syntax.

        Common patterns:
        - <GROUP_ID_FROM_STEP_1> -> {{step_0.data.items[0].id}}
        - <CONNECTOR_ID_FROM_STEP_2> -> {{step_1.data.items[0].id}}
        - <DATASET_ID_FROM_STEP_3> -> {{step_2.dataset_id}}
        """
        import re

        print(f"[Planner] Post-processing plan to fix angle bracket references")

        fixed_steps = []

        for idx, step_data in enumerate(plan_data.get("steps", [])):
            fixed_args = {}

            for key, value in step_data.get("arguments", {}).items():
                if isinstance(value, str) and "<" in value and ">" in value:
                    # Find angle bracket patterns (case-insensitive)
                    pattern = r'<([A-Za-z_]+)_FROM_STEP_(\d+)>'
                    matches = re.findall(pattern, value, re.IGNORECASE)

                    if matches:
                        fixed_value = value
                        for field_name, step_num in matches:
                            # Reconstruct the exact reference as it appears in the value (preserve case)
                            old_ref_pattern = re.compile(f'<{re.escape(field_name)}_FROM_STEP_{step_num}>', re.IGNORECASE)
                            old_ref_match = old_ref_pattern.search(value)
                            old_ref = old_ref_match.group(0) if old_ref_match else f"<{field_name}_FROM_STEP_{step_num}>"

                            # Convert to proper syntax based on field name (case-insensitive check)
                            field_upper = field_name.upper()
                            if "GROUP_ID" in field_upper or "CONNECTOR_ID" in field_upper or "DESTINATION_ID" in field_upper:
                                # These come from Fivetran list APIs: data.items[0].id
                                new_ref = f"{{{{step_{step_num}.data.items[0].id}}}}"
                            elif "DATASET" in field_upper:
                                # Dataset IDs might be in different locations
                                new_ref = f"{{{{step_{step_num}.dataset}}}}"
                            elif "SCHEMA" in field_upper:
                                # Schema names
                                new_ref = f"{{{{step_{step_num}.schema}}}}"
                            else:
                                # Generic: try data.items[0].id first
                                new_ref = f"{{{{step_{step_num}.data.items[0].id}}}}"

                            fixed_value = old_ref_pattern.sub(new_ref, fixed_value)
                            print(f"[Planner] Fixed reference in step {idx}, {key}: {old_ref} -> {new_ref}")

                        fixed_args[key] = fixed_value
                    else:
                        fixed_args[key] = value
                else:
                    fixed_args[key] = value

            # Update the step with fixed arguments
            step_data["arguments"] = fixed_args
            fixed_steps.append(step_data)

        plan_data["steps"] = fixed_steps
        return plan_data


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
