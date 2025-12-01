"""
Unified Authorization Script
Authorizes Gmail, Calendar, and Drive in one go.
"""
import os
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from haitham_voice_agent.config import Config
from haitham_voice_agent.tools.gmail.auth.credentials_store import get_credential_store

# Combine all scopes
ALL_SCOPES = Config.GMAIL_SCOPES + Config.CALENDAR_SCOPES + Config.DRIVE_SCOPES

# Remove duplicates
ALL_SCOPES = list(set(ALL_SCOPES))

def authorize_all():
    print("🚀 Starting Unified Authorization (Gmail + Calendar + Drive)...")
    
    client_secret = Config.CREDENTIALS_DIR / "client_secret.json"
    if not client_secret.exists():
        print(f"❌ Error: client_secret.json not found at {client_secret}")
        return

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secret),
            scopes=ALL_SCOPES
        )
        
        print("🌐 Opening browser...")
        creds = flow.run_local_server(port=0, open_browser=True)
        
        # Save to store
        store = get_credential_store()
        cred_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }
        
        # Save for each service key so individual tools can find it
        # (Even though it's the same token, this ensures compatibility with existing code)
        store.store_credential("gmail_oauth", cred_data)
        store.store_credential("calendar_oauth", cred_data)
        store.store_credential("drive_oauth", cred_data)
        
        print("✅ Authorization Successful!")
        print("Tokens saved for Gmail, Calendar, and Drive.")
        
    except Exception as e:
        print(f"❌ Authorization Failed: {e}")

if __name__ == "__main__":
    authorize_all()
