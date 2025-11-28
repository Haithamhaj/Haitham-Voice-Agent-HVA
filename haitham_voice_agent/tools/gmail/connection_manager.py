"""
Connection Manager

Intelligent connection manager for Gmail operations.
Auto-switches between Gmail API and IMAP/SMTP based on availability.
From Gmail Module SRS Section 3.3.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from .gmail_api_handler import GmailAPIHandler
from .imap_handler import IMAPHandler
from .smtp_handler import SMTPHandler

logger = logging.getLogger(__name__)


class ConnectionMethod(Enum):
    """Connection method types"""
    GMAIL_API = "gmail_api"
    IMAP_SMTP = "imap_smtp"


class ConnectionManager:
    """
    Intelligent connection manager
    
    Strategy:
    1. Try Gmail API first (if credentials exist)
    2. If API fails (quota/auth error), auto-switch to IMAP/SMTP
    3. Maintain active connection state
    4. All methods return unified EmailMessage model
    """
    
    def __init__(self):
        self.gmail_api = GmailAPIHandler()
        self.imap = IMAPHandler()
        self.smtp = SMTPHandler()
        
        self.active_method = None
        self.api_available = None  # Cache API availability
        
        logger.info("ConnectionManager initialized")
    
    def _check_api_availability(self) -> bool:
        """
        Check if Gmail API is available
        
        Returns:
            bool: True if API is available
        """
        if self.api_available is not None:
            return self.api_available
        
        # Check if API service can be built
        try:
            available = self.gmail_api._ensure_service()
            self.api_available = available
            
            if available:
                logger.info("Gmail API is available")
                self.active_method = ConnectionMethod.GMAIL_API
            else:
                logger.info("Gmail API not available, will use IMAP/SMTP")
                self.active_method = ConnectionMethod.IMAP_SMTP
            
            return available
            
        except Exception as e:
            logger.warning(f"Gmail API check failed: {e}")
            self.api_available = False
            self.active_method = ConnectionMethod.IMAP_SMTP
            return False
    
    def _try_api_with_fallback(self, api_method, imap_method, *args, **kwargs):
        """
        Try API method first, fallback to IMAP if it fails
        
        Args:
            api_method: Gmail API method
            imap_method: IMAP method
            *args, **kwargs: Method arguments
            
        Returns:
            Result from either API or IMAP
        """
        # Try API first if available
        if self._check_api_availability():
            try:
                result = api_method(*args, **kwargs)
                
                # Check if result indicates API error
                if isinstance(result, dict) and result.get("error"):
                    error_msg = result.get("message", "")
                    
                    # Check for quota or auth errors
                    if "quota" in error_msg.lower() or "auth" in error_msg.lower() or "credential" in error_msg.lower():
                        logger.warning(f"Gmail API error ({error_msg}), switching to IMAP")
                        self.api_available = False
                        self.active_method = ConnectionMethod.IMAP_SMTP
                        
                        # Retry with IMAP
                        return imap_method(*args, **kwargs)
                
                return result
                
            except Exception as e:
                logger.warning(f"Gmail API method failed: {e}, switching to IMAP")
                self.api_available = False
                self.active_method = ConnectionMethod.IMAP_SMTP
                
                # Fallback to IMAP
                return imap_method(*args, **kwargs)
        
        # Use IMAP directly
        return imap_method(*args, **kwargs)
    
    # ==================== EMAIL OPERATIONS ====================
    
    async def fetch_latest_email(self, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch latest emails (API with IMAP fallback)
        
        Args:
            limit: Number of emails to fetch
            
        Returns:
            dict: Email list
        """
        logger.info(f"Fetching latest {limit} emails...")
        
        result = await self._try_api_with_fallback(
            self.gmail_api.fetch_latest_email,
            self.imap.fetch_latest_email,
            limit=limit
        )
        
        # Add connection method to result
        if isinstance(result, dict) and not result.get("error"):
            result["connection_method"] = self.active_method.value if self.active_method else "unknown"
        
        return result
    
    async def search_emails(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search emails (API with IMAP fallback)
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            dict: Search results
        """
        logger.info(f"Searching emails: {query}")
        
        result = await self._try_api_with_fallback(
            self.gmail_api.search_emails,
            self.imap.search_emails,
            query=query,
            limit=limit
        )
        
        if isinstance(result, dict) and not result.get("error"):
            result["connection_method"] = self.active_method.value if self.active_method else "unknown"
        
        return result
    
    async def get_email_by_id(self, email_id: str) -> Dict[str, Any]:
        """
        Get specific email by ID (API with IMAP fallback)
        
        Args:
            email_id: Email ID
            
        Returns:
            dict: Email data
        """
        logger.info(f"Getting email: {email_id}")
        
        result = await self._try_api_with_fallback(
            self.gmail_api.get_email_by_id,
            self.imap.get_email_by_id,
            email_id=email_id
        )
        
        if isinstance(result, dict) and not result.get("error"):
            result["connection_method"] = self.active_method.value if self.active_method else "unknown"
        
        return result
    
    # ==================== DRAFT OPERATIONS ====================
    
    async def create_draft(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create email draft (API with SMTP fallback)
        
        Args:
            to: Recipients
            subject: Subject
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
            
        Returns:
            dict: Draft info
        """
        logger.info(f"Creating draft: {subject}")
        
        result = await self._try_api_with_fallback(
            self.gmail_api.create_draft,
            self.smtp.create_draft,
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc
        )
        
        if isinstance(result, dict) and not result.get("error"):
            result["connection_method"] = self.active_method.value if self.active_method else "unknown"
        
        return result
    
    async def send_draft(self, draft_id: str, confirmed: bool = False) -> Dict[str, Any]:
        """
        Send draft (REQUIRES CONFIRMATION)
        
        Args:
            draft_id: Draft ID
            confirmed: Confirmation flag (MUST be True)
            
        Returns:
            dict: Send status
        """
        # CRITICAL: Never auto-send without confirmation
        if not confirmed:
            return {
                "error": True,
                "message": "Email send requires explicit confirmation",
                "suggestion": "Set confirmed=True after user voice confirmation"
            }
        
        logger.warning(f"Sending draft: {draft_id} (CONFIRMED)")
        
        # Only Gmail API supports draft sending
        # For SMTP, we need different approach
        if self._check_api_availability():
            return await self.gmail_api.send_draft(draft_id, confirmed=True)
        else:
            return {
                "error": True,
                "message": "Draft sending via SMTP not supported",
                "suggestion": "Use send_email method instead"
            }
    
    async def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Send email directly (REQUIRES CONFIRMATION)
        
        Args:
            to: Recipients
            subject: Subject
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
            confirmed: Confirmation flag (MUST be True)
            
        Returns:
            dict: Send status
        """
        # CRITICAL: Never auto-send without confirmation
        if not confirmed:
            return {
                "error": True,
                "message": "Email send requires explicit confirmation",
                "suggestion": "Set confirmed=True after user voice confirmation"
            }
        
        logger.warning(f"Sending email (CONFIRMED): {subject}")
        
        # Try API first, fallback to SMTP
        if self._check_api_availability():
            # Create draft then send
            draft_result = await self.gmail_api.create_draft(to, subject, body, cc, bcc)
            
            if draft_result.get("error"):
                # API failed, use SMTP
                return await self.smtp.send_email(to, subject, body, cc, bcc, confirmed=True)
            
            # Send draft
            return await self.gmail_api.send_draft(draft_result["draft_id"], confirmed=True)
        else:
            # Use SMTP directly
            return await self.smtp.send_email(to, subject, body, cc, bcc, confirmed=True)
    
    # ==================== LABEL OPERATIONS ====================
    
    async def mark_as_read(self, email_id: str) -> Dict[str, Any]:
        """
        Mark email as read (API only)
        
        Args:
            email_id: Email ID
            
        Returns:
            dict: Status
        """
        if self._check_api_availability():
            return await self.gmail_api.mark_as_read(email_id)
        else:
            return {
                "error": True,
                "message": "Mark as read not supported via IMAP",
                "suggestion": "Use Gmail API"
            }
    
    async def list_labels(self) -> Dict[str, Any]:
        """
        List Gmail labels (API only)
        
        Returns:
            dict: Label list
        """
        if self._check_api_availability():
            return await self.gmail_api.list_labels()
        else:
            return {
                "error": True,
                "message": "Labels not supported via IMAP",
                "suggestion": "Use Gmail API"
            }
    
    # ==================== STATUS ====================
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status
        
        Returns:
            dict: Connection status
        """
        return {
            "active_method": self.active_method.value if self.active_method else "not_initialized",
            "api_available": self.api_available if self.api_available is not None else "unknown",
            "imap_connected": self.imap.connection is not None
        }
    
    def close(self):
        """Close all connections"""
        self.imap.close()
        logger.info("All connections closed")


if __name__ == "__main__":
    # Test Connection Manager
    import asyncio
    
    async def test():
        manager = ConnectionManager()
        
        print("Testing ConnectionManager...")
        
        # Check status
        status = manager.get_connection_status()
        print(f"\nConnection status: {status}")
        
        # Test fetch
        print("\nFetching latest emails...")
        result = await manager.fetch_latest_email(limit=5)
        
        if not result.get("error"):
            print(f"✓ Fetched {result['count']} emails")
            print(f"  Method: {result.get('connection_method')}")
        else:
            print(f"✗ Error: {result['message']}")
        
        # Close
        manager.close()
        
        print("\nConnectionManager test completed")
    
    asyncio.run(test())
