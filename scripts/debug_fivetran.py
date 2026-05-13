"""
Debug script to test Fivetran authentication directly
"""
import base64
import os
import sys
from google.cloud import secretmanager

PROJECT_ID = "bgus-genai-poc2"

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("utf-8")

def main():
    print("Fetching credentials from Secret Manager...")
    api_key = get_secret("fivetran-api-key")
    api_secret = get_secret("fivetran-api-secret")

    print(f"\nAPI Key length: {len(api_key)} characters")
    print(f"API Key first 4 chars: {api_key[:4]}***")
    print(f"API Key last 4 chars: ***{api_key[-4:]}")
    print(f"API Key has whitespace: {api_key != api_key.strip()}")

    print(f"\nAPI Secret length: {len(api_secret)} characters")
    print(f"API Secret first 4 chars: {api_secret[:4]}***")
    print(f"API Secret last 4 chars: ***{api_secret[-4:]}")
    print(f"API Secret has whitespace: {api_secret != api_secret.strip()}")

    # Create the Basic auth header
    credentials = f"{api_key}:{api_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()

    print(f"\nBase64 encoded length: {len(encoded)}")
    print(f"Base64 encoded (first 20 chars): {encoded[:20]}...")

    # Test the API call
    print("\n" + "="*60)
    print("Testing Fivetran API call...")
    print("="*60)

    import requests
    headers = {"Authorization": f"Basic {encoded}"}

    try:
        response = requests.get(
            "https://api.fivetran.com/v1/groups",
            headers=headers,
            timeout=15
        )
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")

        if response.status_code == 200:
            print("\n✓ Authentication successful!")
            data = response.json()
            groups = data.get("data", {}).get("items", [])
            print(f"Found {len(groups)} group(s)")
            for g in groups:
                print(f"  - {g.get('name')} ({g.get('id')})")
        else:
            print("\n✗ Authentication failed!")
            print("\nPossible issues:")
            print("1. API Key or Secret is incorrect")
            print("2. Fivetran account is not active/verified")
            print("3. API access is not enabled for your account")
            print("\nPlease verify:")
            print("- Go to https://fivetran.com/account/settings")
            print("- Check that API access is enabled")
            print("- Regenerate API Key/Secret if needed")

    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    main()
