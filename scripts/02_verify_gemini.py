"""
PipelinePilot — Day 1 verification: Gemini access

Confirms that Gemini 3.1 Pro is callable from this GCP project via Vertex AI's
GLOBAL endpoint. If 3.1 Pro is not yet allowlisted in the project, falls back
to gemini-3-flash-preview, which is the same family and is fine for early
prototyping. We'll switch back to 3.1 Pro for the final agent.

Requirements (install once):
    pip install --upgrade "google-genai>=1.51.0"

Authentication:
    gcloud auth application-default login
    # Make sure the active account has roles/aiplatform.user on the project.

Run:
    python 02_verify_gemini.py
"""

import os
import sys

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "bgus-genai-poc2")

# Gemini 3.x preview models are only available on the GLOBAL endpoint.
# This is the #1 footgun — do not change to a regional location.
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

try:
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit("Install the SDK first:  pip install --upgrade 'google-genai>=1.51.0'")


def try_model(model_id: str) -> bool:
    print(f"\n--- Trying {model_id} ---")
    try:
        client = genai.Client()
        resp = client.models.generate_content(
            model=model_id,
            contents=(
                "In one sentence, what makes an autonomous agent different "
                "from a simple chatbot? Answer concisely."
            ),
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.LOW
                ),
            ),
        )
        print("OK. Response:")
        print(resp.text.strip())
        return True
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        return False


def main() -> None:
    print(f"Project:  {PROJECT_ID}")
    print(f"Location: global  (required for Gemini 3.x previews)")

    # Primary: the model the final agent will use.
    if try_model("gemini-3.1-pro-preview"):
        print("\n*** Gemini 3.1 Pro is available. You're set. ***")
        return

    # Fallback: same family, faster/cheaper, for early prototyping.
    print("\nFalling back to gemini-3-flash-preview ...")
    if try_model("gemini-3-flash-preview"):
        print(
            "\n*** Flash works. For the final submission, request quota for "
            "gemini-3.1-pro-preview via the GCP console. ***"
        )
        return

    sys.exit(
        "\nNeither model worked. Likely causes:\n"
        "  - aiplatform.googleapis.com not enabled (run 01_setup.sh)\n"
        "  - Your ADC user lacks roles/aiplatform.user on the project\n"
        "  - Org policy or model-garden allowlist blocks preview models\n"
        "  - Quota not yet provisioned for Gemini 3.x in this project\n"
    )


if __name__ == "__main__":
    main()
