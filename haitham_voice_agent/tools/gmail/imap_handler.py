"""
IMAP Handler

Fallback method for Gmail operations using IMAP protocol.
From Gmail Module SRS Section 3.3.
"""

import imaplib
import email
from email.header import decode_header
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from ..models.email_message import EmailMessage, Attachment
from ..auth.credentials_store import get_credential_store
from ..utils.text_processing import (
    extract_plain_text_from_html,
    parse_email_list,
    extract_snippet
)
from ...config import Config

logger = logging.getLogger(__name__)


class IMAPHandler:
    """
    IMAP operations handler (fallback method)
    
    Features:
    - Email fetching and searching via IMAP
    - Connection pooling
    - Maps to unified EmailMessage model
    """
    
    def __init__(self):
        self.credential_store = get_credential_store()
        self.connection = None
        self.last_connection_time = 0
        self.connection_timeout = 300  # 5 minutes
        
        logger.info("IMAPHandler initialized")
    
    def _get_connection(self) -> Optional[imaplib.IMAP4_SSL]:
        """
        Get or create IMAP connection with pooling
        
        Returns:
            IMAP4_SSL: Connection or None
        """
        try:
            # Check if existing connection is still valid
            if self.connection:
                elapsed = time.time() - self.last_connection_time
                if elapsed < self.connection_timeout:
                    # Test connection
                    try:
                        self.connection.noop()
                        logger.debug("Reusing existing IMAP connection")
                        return self.connection
                    except:
                        logger.debug("Existing connection invalid, reconnecting...")
                        self.connection = None
            
            # Get credentials
            creds = self.credential_store.retrieve_credential("imap")
            
            if not creds:
                logger.error("No IMAP credentials found")
                logger.info("Please store IMAP credentials first")
                return None
            
            # Connect
            logger.info(f"Connecting to IMAP server: {Config.IMAP_SERVER}")
            
            connection = imaplib.IMAP4_SSL(Config.IMAP_SERVER, Config.IMAP_PORT)
            connection.login(creds["email"], creds["password"])
            
            self.connection = connection
            self.last_connection_time = time.time()
            
            logger.info("IMAP connection established")
            return connection
            
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            return None
    
    async def fetch_latest_email(self, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch latest emails via IMAP
        
        Args:
            limit: Number of emails to fetch
            
        Returns:
            dict: Email list with metadata
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {"error": True, "message": "IMAP connection not available"}
            
            # Select INBOX
            conn.select('INBOX')
            
            # Search for all messages
            status, messages = conn.search(None, 'ALL')
            
            if status != 'OK':
                return {"error": True, "message": "IMAP search failed"}
            
            # Get message IDs (newest first)
            message_ids = messages[0].split()
            message_ids.reverse()
            
            # Limit results
            message_ids = message_ids[:limit]
            
            # Fetch emails
            emails = []
            for msg_id in message_ids:
                email_obj = await self._fetch_email_by_id(conn, msg_id)
                if email_obj:
                    emails.append(email_obj)
            
            logger.info(f"Fetched {len(emails)} emails via IMAP")
            
            return {
                "emails": [email.to_dict() for email in emails],
                "count": len(emails)
            }
            
        except Exception as e:
            logger.error(f"IMAP fetch failed: {e}")
            return {"error": True, "message": str(e)}
    
    async def _fetch_email_by_id(self, conn: imaplib.IMAP4_SSL, msg_id: bytes) -> Optional[EmailMessage]:
        """
        Fetch single email by ID
        
        Args:
            conn: IMAP connection
            msg_id: Message ID
            
        Returns:
            EmailMessage: Parsed email or None
        """
        try:
            # Fetch message
            status, msg_data = conn.fetch(msg_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            # Parse email
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Parse to EmailMessage model
            return self._parse_email_message(email_message, msg_id.decode())
            
        except Exception as e:
            logger.error(f"Failed to fetch email {msg_id}: {e}")
            return None
    
    def _parse_email_message(self, msg: email.message.Message, msg_id: str) -> EmailMessage:
        """
        Parse email.message.Message to EmailMessage model
        
        Args:
            msg: Python email message
            msg_id: Message ID
            
        Returns:
            EmailMessage: Unified email model
        """
        # Decode subject
        subject = self._decode_header(msg.get('Subject', ''))
        
        # Parse addresses
        from_ = msg.get('From', '')
        to = parse_email_list(msg.get('To', ''))
        cc = parse_email_list(msg.get('Cc', ''))
        bcc = parse_email_list(msg.get('Bcc', ''))
        
        # Parse date
        date_str = msg.get('Date', '')
        try:
            from email.utils import parsedate_to_datetime
            date = parsedate_to_datetime(date_str)
        except:
            date = datetime.now()
        
        # Extract body
        body_text = ""
        body_html = None
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments for now
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append(Attachment(
                            filename=self._decode_header(filename),
                            mime_type=content_type,
                            size=len(part.get_payload(decode=True) or b"")
                        ))
                    continue
                
                # Get body
                if content_type == "text/plain":
                    try:
                        body_text = part.get_payload(decode=True).decode()
                    except:
                        pass
                elif content_type == "text/html":
                    try:
                        body_html = part.get_payload(decode=True).decode()
                    except:
                        pass
        else:
            # Not multipart
            content_type = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True).decode()
                if content_type == "text/html":
                    body_html = payload
                    body_text = extract_plain_text_from_html(payload)
                else:
                    body_text = payload
            except:
                pass
        
        # If no plain text, extract from HTML
        if not body_text and body_html:
            body_text = extract_plain_text_from_html(body_html)
        
        # Generate snippet
        snippet = extract_snippet(body_text)
        
        # Check flags (IMAP doesn't have labels like Gmail)
        # We'll use a simple approach: check if message is in INBOX
        labels = ["INBOX"]
        is_unread = True  # Default to unread (IMAP doesn't easily expose this)
        
        # Create EmailMessage
        email_obj = EmailMessage(
            id=msg_id,
            thread_id=msg_id,  # IMAP doesn't have thread concept
            from_=from_,
            to=to,
            cc=cc,
            bcc=bcc,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            snippet=snippet,
            date=date,
            labels=labels,
            is_unread=is_unread,
            is_starred=False,
            is_important=False,
            has_attachments=len(attachments) > 0,
            attachments=attachments,
            source="imap"
        )
        
        return email_obj
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ""
        
        try:
            decoded_parts = decode_header(header)
            decoded_str = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_str += part
            
            return decoded_str
        except:
            return header
    
    async def search_emails(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search emails via IMAP
        
        Args:
            query: Search query (simplified, not Gmail syntax)
            limit: Maximum results
            
        Returns:
            dict: Search results
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {"error": True, "message": "IMAP connection not available"}
            
            # Select INBOX
            conn.select('INBOX')
            
            # Convert query to IMAP search criteria
            # Simple implementation: search in subject and from
            search_criteria = f'(OR SUBJECT "{query}" FROM "{query}")'
            
            # Search
            status, messages = conn.search(None, search_criteria)
            
            if status != 'OK':
                return {"error": True, "message": "IMAP search failed"}
            
            # Get message IDs
            message_ids = messages[0].split()
            message_ids.reverse()
            message_ids = message_ids[:limit]
            
            # Fetch emails
            emails = []
            for msg_id in message_ids:
                email_obj = await self._fetch_email_by_id(conn, msg_id)
                if email_obj:
                    emails.append(email_obj)
            
            logger.info(f"Found {len(emails)} emails via IMAP search")
            
            return {
                "query": query,
                "emails": [email.to_dict() for email in emails],
                "count": len(emails)
            }
            
        except Exception as e:
            logger.error(f"IMAP search failed: {e}")
            return {"error": True, "message": str(e)}
    
    async def get_email_by_id(self, email_id: str) -> Dict[str, Any]:
        """
        Get specific email by ID
        
        Args:
            email_id: Email ID
            
        Returns:
            dict: Email data
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {"error": True, "message": "IMAP connection not available"}
            
            conn.select('INBOX')
            
            email_obj = await self._fetch_email_by_id(conn, email_id.encode())
            
            if email_obj:
                return email_obj.to_dict()
            else:
                return {"error": True, "message": f"Email not found: {email_id}"}
                
        except Exception as e:
            logger.error(f"Failed to get email: {e}")
            return {"error": True, "message": str(e)}
    
    def close(self):
        """Close IMAP connection"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("IMAP connection closed")
            except:
                pass
            finally:
                self.connection = None


if __name__ == "__main__":
    # Test IMAP handler
    import asyncio
    
    async def test():
        handler = IMAPHandler()
        
        print("Testing IMAPHandler...")
        print("Note: Requires IMAP credentials to be stored")
        
        # Test fetch
        print("\nFetching latest emails...")
        result = await handler.fetch_latest_email(limit=5)
        
        if not result.get("error"):
            print(f"✓ Fetched {result['count']} emails")
        else:
            print(f"✗ Error: {result['message']}")
        
        # Close connection
        handler.close()
        
        print("\nIMAPHandler test completed")
    
    asyncio.run(test())
