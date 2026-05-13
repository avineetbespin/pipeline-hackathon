#!/usr/bin/env python
"""
Helper script to store Fivetran credentials in Secret Manager.
This ensures no extra whitespace or newlines are added.

Usage:
    python scripts/store_fivetran_secrets.py
"""

import subprocess
import sys
from getpass import getpass


def store_secret(secret_name: str, secret_value: str, project_id: str = "bgus-genai-poc2"):
    """Store a secret in Google Secret Manager."""
    try:
        # Use stdin to pass the secret value to avoid shell escaping issues
        result = subprocess.run(
            [
                "gcloud",
                "secrets",
                "create",
                secret_name,
                "--data-file=-",
                "--replication-policy=automatic",
                f"--project={project_id}",
            ],
            input=secret_value.encode("utf-8"),
            capture_output=True,
            check=True,
        )
        print(f"✓ Created secret: {secret_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create {secret_name}: {e.stderr.decode()}")
        return False


def main():
    print("=" * 60)
    print("Fivetran Secret Manager Setup")
    print("=" * 60)
    print("\nThis will store your Fivetran API credentials securely.")
    print("Paste your credentials when prompted (they won't be displayed).\n")

    # Get credentials from user
    api_key = getpass("Enter Fivetran API Key: ").strip()
    api_secret = getpass("Enter Fivetran API Secret: ").strip()

    if not api_key or not api_secret:
        print("\n✗ API Key and Secret cannot be empty!")
        sys.exit(1)

    print(f"\nAPI Key length: {len(api_key)} characters")
    print(f"API Secret length: {len(api_secret)} characters")

    confirm = input("\nStore these credentials in Secret Manager? (yes/no): ").lower()
    if confirm not in ["yes", "y"]:
        print("Cancelled.")
        sys.exit(0)

    # Store secrets
    print("\nStoring secrets...")
    success = True
    success &= store_secret("fivetran-api-key", api_key)
    success &= store_secret("fivetran-api-secret", api_secret)

    if success:
        print("\n" + "=" * 60)
        print("✓ Secrets stored successfully!")
        print("=" * 60)
        print("\nYou can now verify with:")
        print("  python scripts/03_verify_fivetran.py --from-secret-manager")
    else:
        print("\n✗ Some secrets failed to store. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
