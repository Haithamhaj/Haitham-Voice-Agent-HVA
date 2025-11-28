"""
OAuth 2.0 Flow for Gmail API

Implements browser-based OAuth flow with automatic token refresh.
From Gmail Module SRS Section 6.1.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from ...config import Config
from .credentials_store import get_credential_store

logger = logging.getLogger(__name__)


class OAuthFlow:
    """
    OAuth 2.0 authentication flow for Gmail API
    
    Features:
    - Browser-based initial authorization
    - Automatic token refresh before expiry
    - Secure storage in macOS Keychain
    """
    
    # Gmail API scopes (from SRS Section 6.1)
    SCOPES = Config.GMAIL_SCOPES
    
    def __init__(self):
        self.credential_store = get_credential_store()
        self.client_secret_path = Config.CREDENTIALS_DIR / "client_secret.json"
        
        logger.info("OAuthFlow initialized")
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Get valid OAuth credentials
        
        Flow:
        1. Check if credentials exist in store
        2. If expired, refresh automatically
        3. If no credentials, initiate OAuth flow
        
        Returns:
            Credentials: Valid OAuth credentials or None
        """
        try:
            # Try to retrieve existing credentials
            cred_data = self.credential_store.retrieve_credential("gmail_oauth")
            
            if cred_data:
                # Reconstruct Credentials object
                creds = Credentials(
                    token=cred_data.get("token"),
                    refresh_token=cred_data.get("refresh_token"),
                    token_uri=cred_data.get("token_uri"),
                    client_id=cred_data.get("client_id"),
                    client_secret=cred_data.get("client_secret"),
                    scopes=cred_data.get("scopes")
                )
                
                # Check if token is expired
                if creds.expired and creds.refresh_token:
                    logger.info("Token expired, refreshing...")
                    creds.refresh(Request())
                    
                    # Save refreshed token
                    self._save_credentials(creds)
                    logger.info("Token refreshed successfully")
                
                elif creds.valid:
                    logger.debug("Using existing valid credentials")
                
                return creds
            
            else:
                # No credentials found, need to authorize
                logger.info("No credentials found, initiating OAuth flow...")
                return self.authorize()
                
        except Exception as e:
            logger.error(f"Failed to get credentials: {e}")
            return None
    
    def authorize(self) -> Optional[Credentials]:
        """
        Initiate OAuth 2.0 authorization flow
        
        Opens browser for user to grant permissions.
        
        Returns:
            Credentials: OAuth credentials or None
        """
        try:
            # Check if client_secret.json exists
            if not self.client_secret_path.exists():
                logger.error(f"client_secret.json not found at: {self.client_secret_path}")
                logger.error("Please download OAuth 2.0 credentials from Google Cloud Console")
                logger.error(f"and place them at: {self.client_secret_path}")
                return None
            
            # Create flow
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secret_path),
                scopes=self.SCOPES
            )
            
            # Run local server for OAuth callback
            logger.info("Opening browser for authorization...")
            logger.info("Please grant permissions in the browser window")
            
            creds = flow.run_local_server(
                port=0,  # Use random available port
                authorization_prompt_message='Please visit this URL to authorize: {url}',
                success_message='Authorization successful! You can close this window.',
                open_browser=True
            )
            
            # Save credentials
            self._save_credentials(creds)
            
            logger.info("Authorization successful")
            return creds
            
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            return None
    
    def _save_credentials(self, creds: Credentials) -> bool:
        """
        Save credentials to encrypted store
        
        Args:
            creds: OAuth credentials
            
        Returns:
            bool: Success status
        """
        try:
            # Convert to dict
            cred_data = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }
            
            # Store encrypted
            success = self.credential_store.store_credential("gmail_oauth", cred_data)
            
            if success:
                logger.debug("Credentials saved successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            return False
    
    def revoke_credentials(self) -> bool:
        """
        Revoke and delete stored credentials
        
        Returns:
            bool: Success status
        """
        try:
            # Delete from store
            success = self.credential_store.delete_credential("gmail_oauth")
            
            if success:
                logger.info("Credentials revoked and deleted")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to revoke credentials: {e}")
            return False
    
    def has_credentials(self) -> bool:
        """
        Check if credentials exist
        
        Returns:
            bool: True if credentials exist
        """
        return self.credential_store.has_credential("gmail_oauth")
    
    def build_service(self):
        """
        Build Gmail API service
        
        Returns:
            Resource: Gmail API service or None
        """
        try:
            creds = self.get_credentials()
            
            if not creds:
                logger.error("No valid credentials available")
                return None
            
            # Build Gmail API service
            service = build('gmail', 'v1', credentials=creds)
            
            logger.debug("Gmail API service built successfully")
            return service
            
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            return None


# Singleton instance
_oauth_flow: Optional[OAuthFlow] = None


def get_oauth_flow() -> OAuthFlow:
    """Get singleton OAuth flow instance"""
    global _oauth_flow
    if _oauth_flow is None:
        _oauth_flow = OAuthFlow()
    return _oauth_flow


if __name__ == "__main__":
    # Test OAuth flow
    flow = get_oauth_flow()
    
    print("Testing OAuthFlow...")
    print(f"Has credentials: {flow.has_credentials()}")
    
    if not flow.has_credentials():
        print("\nNo credentials found. To test:")
        print(f"1. Place client_secret.json at: {flow.client_secret_path}")
        print("2. Run: flow.authorize()")
    else:
        print("\nTesting credential retrieval...")
        creds = flow.get_credentials()
        if creds:
            print(f"✓ Credentials valid: {creds.valid}")
            print(f"✓ Scopes: {creds.scopes}")
        
        print("\nTesting service build...")
        service = flow.build_service()
        if service:
            print("✓ Gmail API service built successfully")
    
    print("\nOAuthFlow test completed")
