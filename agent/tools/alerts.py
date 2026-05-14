"""
Alert tools for PipelinePilot agent.

Provides functions to send alerts to Slack and other notification channels.
"""

import os
from typing import Any, Optional
import httpx


async def send_slack_alert(
    webhook_url: str,
    message: str,
    threshold_breach: Optional[dict] = None,
    is_error: bool = False
) -> dict[str, Any]:
    """
    Send an alert message to Slack via webhook.

    Args:
        webhook_url: Slack webhook URL
        message: Main message text
        threshold_breach: Optional dict with threshold details (value, threshold, metric)
        is_error: Whether this is an error alert (changes color)

    Returns:
        dict with success status
    """
    try:
        # Build Slack message blocks
        color = "#ff0000" if is_error else "#ffa500" if threshold_breach else "#36a64f"

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*PipelinePilot Alert*\n{message}"
                }
            }
        ]

        # Add threshold details if provided
        if threshold_breach:
            metric = threshold_breach.get("metric", "Value")
            current = threshold_breach.get("current_value", "N/A")
            threshold = threshold_breach.get("threshold_value", "N/A")

            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Metric:*\n{metric}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Current Value:*\n{current}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Threshold:*\n{threshold}"
                    }
                ]
            })

        payload = {
            "attachments": [
                {
                    "color": color,
                    "blocks": blocks
                }
            ]
        }

        # Send to Slack
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()

        return {
            "success": True,
            "message": "Alert sent to Slack successfully",
            "webhook_response": response.text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to send Slack alert"
        }


async def send_email_alert(
    recipient: str,
    subject: str,
    message: str,
    is_error: bool = False
) -> dict[str, Any]:
    """
    Send an alert via email (placeholder for future implementation).

    Args:
        recipient: Email address
        subject: Email subject
        message: Email body
        is_error: Whether this is an error alert

    Returns:
        dict with success status
    """
    # TODO: Implement email sending via SendGrid or similar
    return {
        "success": False,
        "error": "Email alerts not yet implemented",
        "message": "Use send_slack_alert for now"
    }


# Map function names to implementations
TOOL_FUNCTIONS = {
    "send_slack_alert": send_slack_alert,
    "send_email_alert": send_email_alert,
}

TOOL_NAMES = list(TOOL_FUNCTIONS.keys())
