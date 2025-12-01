"""
Drive Tools

Google Drive integration for HVA.
Handles file listing, searching, and basic management.
"""

import os
import logging
import io
from typing import Dict, Any, List, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.errors import HttpError

from haitham_voice_agent.config import Config
from haitham_voice_agent.tools.gmail.auth.credentials_store import get_credential_store

logger = logging.getLogger(__name__)

class DriveTools:
    """Google Drive operations"""
    
    def __init__(self):
        self.service = None
        self.credential_store = get_credential_store()
        self.client_secret_path = Config.CREDENTIALS_DIR / "client_secret.json"
        
        logger.info("DriveTools initialized")

    def _get_credentials(self) -> Optional[Credentials]:
        """Get valid OAuth credentials for Drive"""
        try:
            # Try to retrieve existing credentials
            # We use a separate key "drive_oauth" to keep tokens distinct if needed,
            # though often one token can hold multiple scopes.
            # For simplicity/robustness, let's use a distinct key for now.
            cred_data = self.credential_store.retrieve_credential("drive_oauth")
            
            if cred_data:
                creds = Credentials(
                    token=cred_data.get("token"),
                    refresh_token=cred_data.get("refresh_token"),
                    token_uri=cred_data.get("token_uri"),
                    client_id=cred_data.get("client_id"),
                    client_secret=cred_data.get("client_secret"),
                    scopes=cred_data.get("scopes")
                )
                
                if creds.expired and creds.refresh_token:
                    logger.info("Drive token expired, refreshing...")
                    creds.refresh(Request())
                    self._save_credentials(creds)
                
                return creds
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get drive credentials: {e}")
            return None

    def _save_credentials(self, creds: Credentials) -> bool:
        """Save credentials to store"""
        try:
            cred_data = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }
            return self.credential_store.store_credential("drive_oauth", cred_data)
        except Exception as e:
            logger.error(f"Failed to save drive credentials: {e}")
            return False

    def authorize(self) -> Dict[str, Any]:
        """Initiate OAuth flow"""
        try:
            if not self.client_secret_path.exists():
                return {
                    "error": True,
                    "message": f"client_secret.json not found at {self.client_secret_path}",
                    "suggestion": "Download OAuth credentials from Google Cloud Console"
                }
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secret_path),
                scopes=Config.DRIVE_SCOPES
            )
            
            creds = flow.run_local_server(port=0, open_browser=True)
            self._save_credentials(creds)
            
            return {"success": True, "message": "Drive authorized successfully"}
            
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            return {"error": True, "message": str(e)}

    def _ensure_service(self) -> bool:
        """Ensure API service is ready"""
        if self.service:
            return True
            
        creds = self._get_credentials()
        if not creds:
            return False
            
        try:
            self.service = build('drive', 'v3', credentials=creds)
            return True
        except Exception as e:
            logger.error(f"Failed to build drive service: {e}")
            return False

    async def list_files(self, limit: int = 10) -> Dict[str, Any]:
        """List recent files"""
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Drive not authorized. Please say 'Authorize Drive'."}
            
            results = self.service.files().list(
                pageSize=limit,
                fields="nextPageToken, files(id, name, mimeType, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            return {
                "success": True,
                "count": len(files),
                "files": files
            }
            
        except Exception as e:
            logger.error(f"List files failed: {e}")
            return {"error": True, "message": str(e)}

    async def search_files(self, query: str) -> Dict[str, Any]:
        """Search for files by name"""
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Drive not authorized."}
            
            # Google Drive query syntax: name contains 'query'
            q = f"name contains '{query}'"
            
            results = self.service.files().list(
                q=q,
                pageSize=10,
                fields="nextPageToken, files(id, name, mimeType, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            return {
                "success": True,
                "count": len(files),
                "files": files
            }
            
        except Exception as e:
            logger.error(f"Search files failed: {e}")
            return {"error": True, "message": str(e)}

if __name__ == "__main__":
    import asyncio
    async def test():
        drive = DriveTools()
        # print(drive.authorize())
        res = await drive.list_files()
        print(res)
    
    asyncio.run(test())
