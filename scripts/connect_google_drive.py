"""
Dione AI — Connect Google Drive OAuth2
=====================================
Launches the official Google OAuth consent flow using your client_secret file.
Opens your default browser so you can sign in and authorize Google Drive.
Saves the permanent refresh token directly into Dione.
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Allow OAuth over http://localhost
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]

def main():
    secret_path = Path("credentials.json")
    if not secret_path.exists():
        secret_path = Path("data/credentials/client_secret.json")

    if not secret_path.exists():
        print("ERROR: credentials.json not found in project directory.")
        return

    print(f"Loading OAuth client config from: {secret_path}")
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(
        str(secret_path),
        scopes=SCOPES
    )

    print("\nOpening your web browser for Google Authorization...")
    print("Please select your Google Account and click 'Continue' / 'Allow'...")
    creds = flow.run_local_server(port=0, prompt="consent")

    # Read client secret details
    raw_secret = json.loads(secret_path.read_text(encoding="utf-8"))
    block = raw_secret.get("installed") or raw_secret.get("web") or {}

    token_data = {
        "token": creds.token,
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri or block.get("token_uri", "https://oauth2.googleapis.com/token"),
        "client_id": creds.client_id or block.get("client_id", ""),
        "client_secret": getattr(creds, "client_secret", "") or block.get("client_secret", ""),
        "scopes": list(creds.scopes or SCOPES),
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
    }

    # 1. Save to data/google_oauth_token.json
    out_token = Path("data/google_oauth_token.json")
    out_token.parent.mkdir(parents=True, exist_ok=True)
    out_token.write_text(json.dumps(token_data, indent=2), encoding="utf-8")
    print(f"Saved OAuth token to: {out_token}")

    # 2. Save to data/credentials/google_drive.json
    drive_cred = {
        "auth_type": "oauth2",
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_expiry": creds.expiry.isoformat() if creds.expiry else None,
        "api_key": None,
        "extra": {
            "client_id": token_data["client_id"],
            "client_secret": token_data["client_secret"],
            "token_uri": token_data["token_uri"],
            "scopes": token_data["scopes"],
            "service": "google_drive",
        },
        "stored_at": datetime.now().isoformat(),
    }
    out_drive = Path("data/credentials/google_drive.json")
    out_drive.write_text(json.dumps(drive_cred, indent=2), encoding="utf-8")
    print(f"Saved Google Drive credentials to: {out_drive}")

    print("\nGoogle Drive linked successfully to Dione!")

if __name__ == "__main__":
    main()
