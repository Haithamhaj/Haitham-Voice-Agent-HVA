"""
Gmail API Handler

Primary method for Gmail operations using Gmail API.
From Gmail Module SRS Sections 3.3, 4.1-4.6.
"""

import base64
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

from googleapiclient.errors import HttpError

from ..models.email_message import EmailMessage, Draft, Label, Attachment
from ..auth.oauth_flow import get_oauth_flow
from ..utils.text_processing import (
    extract_plain_text_from_html,
    parse_email_address,
    parse_email_list,
    extract_snippet
)
from ...config import Config

logger = logging.getLogger(__name__)


class GmailAPIHandler:
    """
    Gmail API operations handler
    
    Features:
    - Email operations (fetch, search, read)
    - Draft operations (create, update, delete, send)
    - Label operations
    - Caching for performance
    - Rate limiting
    """
    
    def __init__(self):
        self.oauth_flow = get_oauth_flow()
        self.service = None
        self.cache = {}  # Simple in-memory cache
        self.last_request_time = 0
        self.rate_limit_delay = 1.0 / Config.GMAIL_API_RATE_LIMIT  # seconds between requests
        
        logger.info("GmailAPIHandler initialized")
    
    def _ensure_service(self) -> bool:
        """
        Ensure Gmail API service is available
        
        Returns:
            bool: True if service is ready
        """
        if self.service is None:
            self.service = self.oauth_flow.build_service()
        
        return self.service is not None
    
    def _rate_limit(self):
        """Apply rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _get_cached(self, key: str, ttl: int) -> Optional[Any]:
        """
        Get cached value if not expired
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            Cached value or None
        """
        if key in self.cache:
            cached_time, value = self.cache[key]
            if time.time() - cached_time < ttl:
                logger.debug(f"Cache hit: {key}")
                return value
        
        return None
    
    def _set_cached(self, key: str, value: Any):
        """Set cached value"""
        self.cache[key] = (time.time(), value)
    
    async def fetch_latest_email(self, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch latest emails
        
        Args:
            limit: Number of emails to fetch
            
        Returns:
            dict: Email list with metadata
        """
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Gmail API service not available"}
            
            # Check cache
            cache_key = f"latest_{limit}"
            cached = self._get_cached(cache_key, Config.EMAIL_CACHE_TTL)
            if cached:
                return cached
            
            # Rate limit
            self._rate_limit()
            
            # Fetch messages
            logger.info(f"Fetching latest {limit} emails...")
            
            results = self.service.users().messages().list(
                userId='me',
                maxResults=limit,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            
            # Fetch full message details
            emails = []
            for msg in messages:
                email = await self._get_message_details(msg['id'])
                if email:
                    emails.append(email)
            
            result = {
                "emails": [email.to_dict() for email in emails],
                "count": len(emails)
            }
            
            # Cache result
            self._set_cached(cache_key, result)
            
            logger.info(f"Fetched {len(emails)} emails")
            return result
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return {
                "error": True,
                "message": f"Gmail API error: {e.status_code}",
                "suggestion": "Check API credentials and quotas"
            }
        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            return {"error": True, "message": str(e)}
    
    async def _get_message_details(self, message_id: str) -> Optional[EmailMessage]:
        """
        Get full message details
        
        Args:
            message_id: Message ID
            
        Returns:
            EmailMessage: Email object or None
        """
        try:
            # Check cache
            cache_key = f"msg_{message_id}"
            cached = self._get_cached(cache_key, Config.EMAIL_CACHE_TTL)
            if cached:
                return cached
            
            # Rate limit
            self._rate_limit()
            
            # Fetch message
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Parse message
            email = self._parse_message(message)
            
            # Cache
            self._set_cached(cache_key, email)
            
            return email
            
        except Exception as e:
            logger.error(f"Failed to get message {message_id}: {e}")
            return None
    
    def _parse_message(self, message: Dict[str, Any]) -> EmailMessage:
        """
        Parse Gmail API message to EmailMessage
        
        Args:
            message: Gmail API message dict
            
        Returns:
            EmailMessage: Parsed email
        """
        # Extract headers
        headers = {}
        for header in message['payload'].get('headers', []):
            headers[header['name'].lower()] = header['value']
        
        # Parse date
        date_str = headers.get('date', '')
        try:
            from email.utils import parsedate_to_datetime
            date = parsedate_to_datetime(date_str)
        except:
            date = datetime.now()
        
        # Extract body
        body_text = ""
        body_html = None
        
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body_text = self._decode_body(part['body'].get('data', ''))
                elif part['mimeType'] == 'text/html':
                    body_html = self._decode_body(part['body'].get('data', ''))
        else:
            body_data = message['payload']['body'].get('data', '')
            if message['payload']['mimeType'] == 'text/html':
                body_html = self._decode_body(body_data)
                body_text = extract_plain_text_from_html(body_html)
            else:
                body_text = self._decode_body(body_data)
        
        # If no plain text, extract from HTML
        if not body_text and body_html:
            body_text = extract_plain_text_from_html(body_html)
        
        # Extract snippet
        snippet = message.get('snippet', extract_snippet(body_text))
        
        # Parse labels
        labels = message.get('labelIds', [])
        
        # Check flags
        is_unread = 'UNREAD' in labels
        is_starred = 'STARRED' in labels
        is_important = 'IMPORTANT' in labels
        
        # Parse attachments
        has_attachments = False
        attachments = []
        
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part.get('filename'):
                    has_attachments = True
                    attachments.append(Attachment(
                        filename=part['filename'],
                        mime_type=part['mimeType'],
                        size=part['body'].get('size', 0),
                        attachment_id=part['body'].get('attachmentId')
                    ))
        
        # Create EmailMessage
        email = EmailMessage(
            id=message['id'],
            thread_id=message['threadId'],
            from_=headers.get('from', ''),
            to=parse_email_list(headers.get('to', '')),
            cc=parse_email_list(headers.get('cc', '')),
            bcc=parse_email_list(headers.get('bcc', '')),
            subject=headers.get('subject', '(No Subject)'),
            body_text=body_text,
            body_html=body_html,
            snippet=snippet,
            date=date,
            labels=labels,
            is_unread=is_unread,
            is_starred=is_starred,
            is_important=is_important,
            has_attachments=has_attachments,
            attachments=attachments,
            raw_headers=headers,
            source="gmail_api"
        )
        
        return email
    
    def _decode_body(self, data: str) -> str:
        """Decode base64url encoded body"""
        if not data:
            return ""
        
        try:
            # Gmail uses base64url encoding
            decoded = base64.urlsafe_b64decode(data).decode('utf-8')
            return decoded
        except Exception as e:
            logger.error(f"Failed to decode body: {e}")
            return ""
    
    async def search_emails(
        self,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search emails using Gmail search syntax
        
        Args:
            query: Gmail search query (e.g., "from:john@example.com")
            limit: Maximum results
            
        Returns:
            dict: Search results
        """
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Gmail API service not available"}
            
            # Check cache
            cache_key = f"search_{query}_{limit}"
            cached = self._get_cached(cache_key, Config.SEARCH_CACHE_TTL)
            if cached:
                return cached
            
            # Rate limit
            self._rate_limit()
            
            logger.info(f"Searching emails: {query}")
            
            # Search
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()
            
            messages = results.get('messages', [])
            
            # Fetch details
            emails = []
            for msg in messages:
                email = await self._get_message_details(msg['id'])
                if email:
                    emails.append(email)
            
            result = {
                "query": query,
                "emails": [email.to_dict() for email in emails],
                "count": len(emails)
            }
            
            # Cache
            self._set_cached(cache_key, result)
            
            logger.info(f"Found {len(emails)} emails")
            return result
            
        except HttpError as e:
            logger.error(f"Search failed: {e}")
            return {"error": True, "message": f"Search failed: {e.status_code}"}
        except Exception as e:
            logger.error(f"Search failed: {e}")
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
            email = await self._get_message_details(email_id)
            
            if email:
                return email.to_dict()
            else:
                return {"error": True, "message": f"Email not found: {email_id}"}
                
        except Exception as e:
            logger.error(f"Failed to get email: {e}")
            return {"error": True, "message": str(e)}
    
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
        Create email draft
        
        Args:
            to: Recipients
            subject: Subject
            body: Email body
            cc: CC recipients
            bcc: BCC recipients
            
        Returns:
            dict: Draft info with draft_id
        """
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Gmail API service not available"}
            
            # Create MIME message
            message = MIMEText(body)
            message['to'] = ', '.join(to)
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)
            
            # Encode
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Rate limit
            self._rate_limit()
            
            # Create draft
            logger.info(f"Creating draft: {subject}")
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()
            
            logger.info(f"Draft created: {draft['id']}")
            
            return {
                "draft_id": draft['id'],
                "message_id": draft['message']['id'],
                "to": to,
                "subject": subject
            }
            
        except HttpError as e:
            logger.error(f"Failed to create draft: {e}")
            return {"error": True, "message": f"Failed to create draft: {e.status_code}"}
        except Exception as e:
            logger.error(f"Failed to create draft: {e}")
            return {"error": True, "message": str(e)}
    
    async def list_drafts(self, limit: int = 10) -> Dict[str, Any]:
        """
        List email drafts
        
        Args:
            limit: Maximum drafts to return
            
        Returns:
            dict: Draft list
        """
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Gmail API service not available"}
            
            # Check cache
            cache_key = f"drafts_{limit}"
            cached = self._get_cached(cache_key, Config.DRAFTS_CACHE_TTL)
            if cached:
                return cached
            
            # Rate limit
            self._rate_limit()
            
            logger.info("Listing drafts...")
            
            # List drafts
            results = self.service.users().drafts().list(
                userId='me',
                maxResults=limit
            ).execute()
            
            drafts = results.get('drafts', [])
            
            result = {
                "drafts": [
                    {
                        "draft_id": draft['id'],
                        "message_id": draft['message']['id']
                    }
                    for draft in drafts
                ],
                "count": len(drafts)
            }
            
            # Cache
            self._set_cached(cache_key, result)
            
            logger.info(f"Found {len(drafts)} drafts")
            return result
            
        except HttpError as e:
            logger.error(f"Failed to list drafts: {e}")
            return {"error": True, "message": f"Failed to list drafts: {e.status_code}"}
        except Exception as e:
            logger.error(f"Failed to list drafts: {e}")
            return {"error": True, "message": str(e)}
    
    async def delete_draft(self, draft_id: str) -> Dict[str, Any]:
        """
        Delete draft
        
        Args:
            draft_id: Draft ID
            
        Returns:
            dict: Status
        """
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Gmail API service not available"}
            
            # Rate limit
            self._rate_limit()
            
            logger.info(f"Deleting draft: {draft_id}")
            
            # Delete
            self.service.users().drafts().delete(
                userId='me',
                id=draft_id
            ).execute()
            
            logger.info(f"Draft deleted: {draft_id}")
            
            return {
                "status": "deleted",
                "draft_id": draft_id
            }
            
        except HttpError as e:
            logger.error(f"Failed to delete draft: {e}")
            return {"error": True, "message": f"Failed to delete draft: {e.status_code}"}
        except Exception as e:
            logger.error(f"Failed to delete draft: {e}")
            return {"error": True, "message": str(e)}
    
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
        
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Gmail API service not available"}
            
            # Rate limit
            self._rate_limit()
            
            logger.warning(f"Sending draft: {draft_id} (CONFIRMED)")
            
            # Send
            sent = self.service.users().drafts().send(
                userId='me',
                body={'id': draft_id}
            ).execute()
            
            logger.info(f"Draft sent: {draft_id}")
            
            return {
                "status": "sent",
                "draft_id": draft_id,
                "message_id": sent['id']
            }
            
        except HttpError as e:
            logger.error(f"Failed to send draft: {e}")
            return {"error": True, "message": f"Failed to send draft: {e.status_code}"}
        except Exception as e:
            logger.error(f"Failed to send draft: {e}")
            return {"error": True, "message": str(e)}
    
    # ==================== LABEL OPERATIONS ====================
    
    async def mark_as_read(self, email_id: str) -> Dict[str, Any]:
        """
        Mark email as read
        
        Args:
            email_id: Email ID
            
        Returns:
            dict: Status
        """
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Gmail API service not available"}
            
            # Rate limit
            self._rate_limit()
            
            logger.info(f"Marking as read: {email_id}")
            
            # Remove UNREAD label
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return {
                "status": "marked_read",
                "email_id": email_id
            }
            
        except HttpError as e:
            logger.error(f"Failed to mark as read: {e}")
            return {"error": True, "message": f"Failed to mark as read: {e.status_code}"}
        except Exception as e:
            logger.error(f"Failed to mark as read: {e}")
            return {"error": True, "message": str(e)}
    
    async def apply_label(self, email_id: str, label_name: str) -> Dict[str, Any]:
        """
        Apply label to email
        
        Args:
            email_id: Email ID
            label_name: Label name
            
        Returns:
            dict: Status
        """
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Gmail API service not available"}
            
            # Get label ID
            labels = await self.list_labels()
            label_id = None
            
            for label in labels.get('labels', []):
                if label['name'].lower() == label_name.lower():
                    label_id = label['id']
                    break
            
            if not label_id:
                return {"error": True, "message": f"Label not found: {label_name}"}
            
            # Rate limit
            self._rate_limit()
            
            logger.info(f"Applying label '{label_name}' to {email_id}")
            
            # Apply label
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            return {
                "status": "label_applied",
                "email_id": email_id,
                "label": label_name
            }
            
        except HttpError as e:
            logger.error(f"Failed to apply label: {e}")
            return {"error": True, "message": f"Failed to apply label: {e.status_code}"}
        except Exception as e:
            logger.error(f"Failed to apply label: {e}")
            return {"error": True, "message": str(e)}
    
    async def list_labels(self) -> Dict[str, Any]:
        """
        List all Gmail labels
        
        Returns:
            dict: Label list
        """
        try:
            if not self._ensure_service():
                return {"error": True, "message": "Gmail API service not available"}
            
            # Check cache
            cache_key = "labels"
            cached = self._get_cached(cache_key, Config.LABELS_CACHE_TTL)
            if cached:
                return cached
            
            # Rate limit
            self._rate_limit()
            
            logger.info("Listing labels...")
            
            # List labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            result = {
                "labels": [
                    {
                        "id": label['id'],
                        "name": label['name'],
                        "type": label.get('type', 'user')
                    }
                    for label in labels
                ],
                "count": len(labels)
            }
            
            # Cache
            self._set_cached(cache_key, result)
            
            logger.info(f"Found {len(labels)} labels")
            return result
            
        except HttpError as e:
            logger.error(f"Failed to list labels: {e}")
            return {"error": True, "message": f"Failed to list labels: {e.status_code}"}
        except Exception as e:
            logger.error(f"Failed to list labels: {e}")
            return {"error": True, "message": str(e)}


if __name__ == "__main__":
    # Test Gmail API handler
    import asyncio
    
    async def test():
        handler = GmailAPIHandler()
        
        print("Testing GmailAPIHandler...")
        
        if not handler._ensure_service():
            print("✗ Gmail API service not available")
            print("Please set up OAuth credentials first")
            return
        
        print("✓ Gmail API service ready")
        
        # Test fetch latest
        print("\nFetching latest emails...")
        result = await handler.fetch_latest_email(limit=5)
        
        if not result.get("error"):
            print(f"✓ Fetched {result['count']} emails")
            if result['count'] > 0:
                email = result['emails'][0]
                print(f"  Latest: {email['subject']}")
        else:
            print(f"✗ Error: {result['message']}")
        
        print("\nGmailAPIHandler test completed")
    
    asyncio.run(test())
