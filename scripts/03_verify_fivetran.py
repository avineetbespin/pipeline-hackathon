"""
PipelinePilot — Day 1 verification: Fivetran API access

Confirms that the Fivetran API key + secret authenticate correctly and that
the account can be queried. We don't use the MCP server yet — just the bare
REST API — because we want to isolate "is the credential good?" from "is the
MCP wrapper working?". Day 2 brings the MCP server online.

The Fivetran API key and secret should be stored in Secret Manager
(see 01_setup.sh). For this verification script you can either:
  (a) export them as env vars locally, or
  (b) read them from Secret Manager (recommended).

Run (option a):
    export FIVETRAN_API_KEY=...
    export FIVETRAN_API_SECRET=...
    python 03_verify_fivetran.py

Run (option b):
    python 03_verify_fivetran.py --from-secret-manager

Requirements:
    pip install requests google-cloud-secret-manager
"""

import argparse
import base64
import os
import sys

import requests

FIVETRAN_BASE = "https://api.fivetran.com/v1"


def load_creds_from_env() -> tuple[str, str]:
    key = os.environ.get("FIVETRAN_API_KEY")
    secret = os.environ.get("FIVETRAN_API_SECRET")
    if not key or not secret:
        sys.exit(
            "Missing FIVETRAN_API_KEY / FIVETRAN_API_SECRET env vars. "
            "Either export them or use --from-secret-manager."
        )
    return key, secret


def load_creds_from_secret_manager(project_id: str) -> tuple[str, str]:
    from google.cloud import secretmanager  # lazy import

    client = secretmanager.SecretManagerServiceClient()

    def access(secret_id: str) -> str:
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        return client.access_secret_version(name=name).payload.data.decode("utf-8")

    return access("fivetran-api-key"), access("fivetran-api-secret")


def auth_header(key: str, secret: str) -> dict[str, str]:
    token = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-secret-manager", action="store_true")
    parser.add_argument(
        "--project",
        default=os.environ.get("GOOGLE_CLOUD_PROJECT", "bgus-genai-poc2"),
    )
    args = parser.parse_args()

    if args.from_secret_manager:
        print(f"Loading Fivetran creds from Secret Manager in {args.project} ...")
        key, secret = load_creds_from_secret_manager(args.project)
    else:
        key, secret = load_creds_from_env()

    headers = auth_header(key, secret)

    # 1) Smoke test: list groups (a "group" is a Fivetran workspace).
    print("\n--- GET /groups ---")
    r = requests.get(f"{FIVETRAN_BASE}/groups", headers=headers, timeout=15)
    if r.status_code != 200:
        sys.exit(f"FAILED: {r.status_code} {r.text}")
    groups = r.json().get("data", {}).get("items", [])
    print(f"OK. Found {len(groups)} group(s):")
    for g in groups:
        print(f"   - {g.get('name')}  ({g.get('id')})")

    if not groups:
        print(
            "\nNo groups exist yet. Create one in the Fivetran UI "
            "(it's the workspace that holds connectors)."
        )
        return

    # 2) List connectors in the first group.
    gid = groups[0]["id"]
    print(f"\n--- GET /groups/{gid}/connectors ---")
    r = requests.get(
        f"{FIVETRAN_BASE}/groups/{gid}/connectors", headers=headers, timeout=15
    )
    if r.status_code != 200:
        sys.exit(f"FAILED: {r.status_code} {r.text}")
    items = r.json().get("data", {}).get("items", [])
    print(f"OK. Found {len(items)} connector(s) in group '{groups[0]['name']}'.")
    for c in items[:10]:
        print(
            f"   - {c.get('schema'):<24}  "
            f"service={c.get('service'):<16}  "
            f"status={c.get('status', {}).get('setup_state')}"
        )

    print("\n*** Fivetran credentials are working. ***")


if __name__ == "__main__":
    main()
