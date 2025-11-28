"""
SMTP Handler

Fallback method for sending emails using SMTP protocol.
From Gmail Module SRS Section 3.3.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import List, Dict, Any, Optional

from ..auth.credentials_store import get_credential_store
from ...config import Config

logger = logging.getLogger(__name__)


class SMTPHandler:
    """
    SMTP operations handler (fallback method)
    
    Features:
    - Send emails via SMTP
    - Requires confirmation (never auto-send)
    """
    
    def __init__(self):
        self.credential_store = get_credential_store()
        logger.info("SMTPHandler initialized")
    
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
        Send email via SMTP (REQUIRES CONFIRMATION)
        
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
        
        try:
            # Get credentials
            creds = self.credential_store.retrieve_credential("smtp")
            
            if not creds:
                # Try IMAP credentials (same for Gmail)
                creds = self.credential_store.retrieve_credential("imap")
            
            if not creds:
                return {"error": True, "message": "No SMTP credentials found"}
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = creds["email"]
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            logger.warning(f"Sending email via SMTP (CONFIRMED): {subject}")
            
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()  # Secure connection
                server.login(creds["email"], creds["password"])
                
                # Send
                all_recipients = to + (cc or []) + (bcc or [])
                server.send_message(msg, from_addr=creds["email"], to_addrs=all_recipients)
            
            logger.info(f"Email sent via SMTP: {subject}")
            
            return {
                "status": "sent",
                "to": to,
                "subject": subject,
                "method": "smtp"
            }
            
        except Exception as e:
            logger.error(f"SMTP send failed: {e}")
            return {"error": True, "message": str(e)}
    
    async def create_draft(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create draft (SMTP doesn't support drafts, returns draft data only)
        
        Args:
            to: Recipients
            subject: Subject
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
            
        Returns:
            dict: Draft info (not actually saved to server)
        """
        logger.info(f"Creating draft (SMTP mode): {subject}")
        
        # SMTP doesn't support drafts
        # We'll just return the draft data
        # The Connection Manager can store this locally if needed
        
        import uuid
        draft_id = str(uuid.uuid4())
        
        return {
            "draft_id": draft_id,
            "to": to,
            "subject": subject,
            "body": body,
            "cc": cc or [],
            "bcc": bcc or [],
            "method": "smtp",
            "note": "SMTP drafts are not saved to server"
        }


if __name__ == "__main__":
    # Test SMTP handler
    import asyncio
    
    async def test():
        handler = SMTPHandler()
        
        print("Testing SMTPHandler...")
        print("Note: Requires SMTP credentials to be stored")
        print("Note: Will not actually send without confirmed=True")
        
        # Test create draft
        print("\nCreating draft...")
        result = await handler.create_draft(
            to=["test@example.com"],
            subject="Test Email",
            body="This is a test email"
        )
        
        if not result.get("error"):
            print(f"✓ Draft created: {result['draft_id']}")
        else:
            print(f"✗ Error: {result['message']}")
        
        print("\nSMTPHandler test completed")
    
    asyncio.run(test())
