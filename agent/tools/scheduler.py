"""
Cloud Scheduler and Slack webhook tools for PipelinePilot agent.

Provides functions to create scheduled BigQuery queries and send alerts to Slack.
"""

import os
import json
from typing import Any
from google.cloud import scheduler_v1
from google.protobuf import duration_pb2
import httpx

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "bgus-genai-poc2")
REGION = os.getenv("CLOUD_SCHEDULER_REGION", "us-central1")


async def create_scheduled_job(
    job_name: str,
    schedule: str,
    query_sql: str,
    slack_webhook_url: str,
    threshold_condition: str = None,
    description: str = None
) -> dict[str, Any]:
    """
    Create a Cloud Scheduler job that runs a BigQuery query and sends alerts to Slack.

    Args:
        job_name: Name for the scheduled job (alphanumeric, hyphens, underscores)
        schedule: Cron schedule (e.g., "0 9 * * *" for daily at 9am)
        query_sql: SQL query to run
        slack_webhook_url: Slack webhook URL for alerts
        threshold_condition: Optional condition description for alerts (e.g., "CAC payback > 6 months")
        description: Optional human-readable description

    Returns:
        dict with job details
    """
    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{PROJECT_ID}/locations/{REGION}"
    job_path = f"{parent}/jobs/{job_name}"

    try:
        # Create HTTP target that calls our agent backend
        # In production, this would call a Cloud Function that runs the query + Slack logic
        # For now, we'll create a simple job structure

        # Build the payload
        payload = {
            "query_sql": query_sql,
            "slack_webhook_url": slack_webhook_url,
            "threshold_condition": threshold_condition,
            "job_name": job_name
        }

        # Note: In production, you'd set up a Cloud Function endpoint here
        # For hackathon demo, we'll create the job structure but won't set a real target
        # This allows the approval flow to work without needing a Cloud Function deployed

        job = scheduler_v1.Job(
            name=job_path,
            description=description or f"Scheduled query: {job_name}",
            schedule=schedule,
            time_zone="America/Los_Angeles",
            http_target=scheduler_v1.HttpTarget(
                uri=f"https://pipelinepilot-agent-956500419273.us-central1.run.app/scheduler/execute",
                http_method=scheduler_v1.HttpMethod.POST,
                body=json.dumps(payload).encode('utf-8'),
                headers={
                    "Content-Type": "application/json"
                }
            ),
            attempt_deadline=duration_pb2.Duration(seconds=180)
        )

        # Create the job
        created_job = client.create_job(request={"parent": parent, "job": job})

        return {
            "success": True,
            "job_name": job_name,
            "job_path": created_job.name,
            "schedule": schedule,
            "description": description,
            "query": query_sql,
            "slack_webhook": slack_webhook_url[:50] + "..." if len(slack_webhook_url) > 50 else slack_webhook_url
        }

    except Exception as e:
        # If job already exists, try to update it
        if "already exists" in str(e).lower():
            try:
                job = scheduler_v1.Job(
                    name=job_path,
                    description=description or f"Scheduled query: {job_name}",
                    schedule=schedule,
                    time_zone="America/Los_Angeles",
                    http_target=scheduler_v1.HttpTarget(
                        uri=f"https://pipelinepilot-agent-956500419273.us-central1.run.app/scheduler/execute",
                        http_method=scheduler_v1.HttpMethod.POST,
                        body=json.dumps(payload).encode('utf-8'),
                        headers={
                            "Content-Type": "application/json"
                        }
                    ),
                    attempt_deadline=duration_pb2.Duration(seconds=180)
                )

                updated_job = client.update_job(request={"job": job})

                return {
                    "success": True,
                    "job_name": job_name,
                    "job_path": updated_job.name,
                    "schedule": schedule,
                    "updated": True
                }
            except Exception as update_error:
                return {
                    "success": False,
                    "error": f"Job exists but could not update: {str(update_error)}"
                }

        return {
            "success": False,
            "error": str(e)
        }


async def list_scheduled_jobs() -> dict[str, Any]:
    """
    List all Cloud Scheduler jobs in the project.

    Returns:
        dict with list of jobs
    """
    client = scheduler_v1.CloudSchedulerClient()
    parent = f"projects/{PROJECT_ID}/locations/{REGION}"

    try:
        jobs = []
        for job in client.list_jobs(request={"parent": parent}):
            jobs.append({
                "name": job.name.split("/")[-1],
                "full_path": job.name,
                "schedule": job.schedule,
                "description": job.description,
                "state": scheduler_v1.Job.State(job.state).name,
                "time_zone": job.time_zone
            })

        return {
            "success": True,
            "job_count": len(jobs),
            "jobs": jobs
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def delete_scheduled_job(job_name: str) -> dict[str, Any]:
    """
    Delete a Cloud Scheduler job.

    Args:
        job_name: Name of the job to delete

    Returns:
        dict with deletion status
    """
    client = scheduler_v1.CloudSchedulerClient()
    job_path = f"projects/{PROJECT_ID}/locations/{REGION}/jobs/{job_name}"

    try:
        client.delete_job(request={"name": job_path})

        return {
            "success": True,
            "job_name": job_name,
            "deleted": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def send_slack_alert(
    webhook_url: str,
    message: str,
    threshold_breach: dict[str, Any] = None,
    is_error: bool = False
) -> dict[str, Any]:
    """
    Send an alert to Slack via webhook.

    Args:
        webhook_url: Slack webhook URL
        message: Main message text
        threshold_breach: Optional dict with breach details (query_result, threshold, condition)
        is_error: Whether this is an error alert (changes color)

    Returns:
        dict with send status
    """
    try:
        # Build Slack message payload
        color = "#FF0000" if is_error else "#36A64F"  # Red for error, green for success

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*PipelinePilot Alert*\n{message}"
                }
            }
        ]

        # Add threshold breach details if provided
        if threshold_breach:
            breach_text = f"*Condition:* {threshold_breach.get('condition', 'N/A')}\n"
            breach_text += f"*Current Value:* {threshold_breach.get('current_value', 'N/A')}\n"
            breach_text += f"*Threshold:* {threshold_breach.get('threshold', 'N/A')}"

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": breach_text
                }
            })

        payload = {
            "blocks": blocks,
            "attachments": [{
                "color": color,
                "text": "View details in BigQuery or PipelinePilot dashboard"
            }]
        }

        # Send to Slack
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10.0)
            response.raise_for_status()

        return {
            "success": True,
            "message": "Alert sent to Slack",
            "status_code": response.status_code
        }

    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def pause_scheduled_job(job_name: str) -> dict[str, Any]:
    """
    Pause a Cloud Scheduler job.

    Args:
        job_name: Name of the job to pause

    Returns:
        dict with pause status
    """
    client = scheduler_v1.CloudSchedulerClient()
    job_path = f"projects/{PROJECT_ID}/locations/{REGION}/jobs/{job_name}"

    try:
        client.pause_job(request={"name": job_path})

        return {
            "success": True,
            "job_name": job_name,
            "paused": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def resume_scheduled_job(job_name: str) -> dict[str, Any]:
    """
    Resume a paused Cloud Scheduler job.

    Args:
        job_name: Name of the job to resume

    Returns:
        dict with resume status
    """
    client = scheduler_v1.CloudSchedulerClient()
    job_path = f"projects/{PROJECT_ID}/locations/{REGION}/jobs/{job_name}"

    try:
        client.resume_job(request={"name": job_path})

        return {
            "success": True,
            "job_name": job_name,
            "resumed": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Map function names to implementations
TOOL_FUNCTIONS = {
    "create_scheduled_job": create_scheduled_job,
    "list_scheduled_jobs": list_scheduled_jobs,
    "delete_scheduled_job": delete_scheduled_job,
    "send_slack_alert": send_slack_alert,
    "pause_scheduled_job": pause_scheduled_job,
    "resume_scheduled_job": resume_scheduled_job,
}

TOOL_NAMES = list(TOOL_FUNCTIONS.keys())
