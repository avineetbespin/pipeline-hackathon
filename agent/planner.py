"""
Gemini-based planner for PipelinePilot.

Takes a natural language goal and uses Gemini 3.1 Pro to interact with Fivetran.
"""

import os
import json
from google import genai
from google.genai import types

# Import our async tool functions - we'll manually invoke them
from agent.tools import fivetran as fivetran_tools


# Configure Gemini for Vertex AI
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", "bgus-genai-poc2")
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"  # MUST be global for Gemini 3.x
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def query_fivetran(user_question: str) -> str:
    """
    Answer a question about Fivetran account using Gemini 3.1 Pro.

    Args:
        user_question: Natural language question

    Returns:
        Gemini's response as a string
    """
    print(f"\nUser: {user_question}\n")

    client = genai.Client()

    # System prompt
    system_prompt = """You are PipelinePilot, an AI assistant that helps users understand and manage their Fivetran data pipelines.

You can answer questions about:
- What Fivetran groups (workspaces) exist
- What connectors are configured
- Details about specific connectors

Be concise and helpful. When you need information from Fivetran, I'll provide it to you."""

    # First, make a call to Gemini to understand what the user is asking
    initial_response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=[
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "user", "parts": [{"text": user_question}]},
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level=types.ThinkingLevel.LOW
            ),
            temperature=0.3,
        ),
    )

    # For now, we'll just return the response
    # In Phase 3, we'll add proper tool calling loop
    return initial_response.text


def main():
    """Demo the planner."""
    print("="*60)
    print("PipelinePilot - Gemini Planner Demo (Phase 2)")
    print("="*60)

    # Simple test without tool calling first
    response = query_fivetran("Explain what Fivetran groups are in one sentence.")
    print(f"\nAgent: {response}\n")

    print("="*60)
    print("\nPhase 2 complete! Gemini 3.1 Pro is responding.")
    print("Next: Add function calling for Fivetran tools in Phase 3.")
    print("="*60)


if __name__ == "__main__":
    main()
