"""
Email Message Data Model

Unified email representation for both Gmail API and IMAP.
From Gmail Module SRS Section 3.2.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from email.utils import parseaddr


@dataclass
class Attachment:
    """Email attachment metadata"""
    filename: str
    mime_type: str
    size: int
    attachment_id: Optional[str] = None  # Gmail API attachment ID


@dataclass
class EmailMessage:
    """
    Unified email representation
    Works with both Gmail API and IMAP responses
    """
    # Core identifiers
    id: str                           # Message ID
    thread_id: str                    # Thread/conversation ID
    
    # Headers
    from_: str                        # Sender email
    to: List[str]                     # Recipients
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    subject: str = ""
    
    # Content
    body_text: str = ""               # Plain text body
    body_html: Optional[str] = None   # HTML body (if available)
    snippet: str = ""                 # First 100 chars preview
    
    # Metadata
    date: datetime = field(default_factory=datetime.now)
    labels: List[str] = field(default_factory=list)  # Gmail labels or IMAP folders
    is_unread: bool = True
    is_starred: bool = False
    is_important: bool = False
    
    # Attachments
    has_attachments: bool = False
    attachments: List[Attachment] = field(default_factory=list)
    
    # Raw data
    raw_headers: Dict[str, str] = field(default_factory=dict)
    
    # Source
    source: str = "gmail_api"  # "gmail_api" or "imap"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "from": self.from_,
            "to": self.to,
            "cc": self.cc,
            "bcc": self.bcc,
            "subject": self.subject,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "snippet": self.snippet,
            "date": self.date.isoformat(),
            "labels": self.labels,
            "is_unread": self.is_unread,
            "is_starred": self.is_starred,
            "is_important": self.is_important,
            "has_attachments": self.has_attachments,
            "attachments": [
                {
                    "filename": att.filename,
                    "mime_type": att.mime_type,
                    "size": att.size
                }
                for att in self.attachments
            ],
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailMessage':
        """Create from dictionary"""
        # Parse date
        date = datetime.fromisoformat(data["date"]) if isinstance(data.get("date"), str) else data.get("date", datetime.now())
        
        # Parse attachments
        attachments = [
            Attachment(
                filename=att["filename"],
                mime_type=att["mime_type"],
                size=att["size"]
            )
            for att in data.get("attachments", [])
        ]
        
        return cls(
            id=data["id"],
            thread_id=data["thread_id"],
            from_=data["from"],
            to=data.get("to", []),
            cc=data.get("cc", []),
            bcc=data.get("bcc", []),
            subject=data.get("subject", ""),
            body_text=data.get("body_text", ""),
            body_html=data.get("body_html"),
            snippet=data.get("snippet", ""),
            date=date,
            labels=data.get("labels", []),
            is_unread=data.get("is_unread", True),
            is_starred=data.get("is_starred", False),
            is_important=data.get("is_important", False),
            has_attachments=data.get("has_attachments", False),
            attachments=attachments,
            source=data.get("source", "gmail_api")
        )
    
    def get_sender_name(self) -> str:
        """Extract sender name from email address"""
        name, email = parseaddr(self.from_)
        return name if name else email
    
    def get_sender_email(self) -> str:
        """Extract sender email address"""
        name, email = parseaddr(self.from_)
        return email


@dataclass
class Draft:
    """Email draft representation"""
    draft_id: str
    message: EmailMessage
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "draft_id": self.draft_id,
            "message": self.message.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Label:
    """Gmail label or IMAP folder"""
    id: str
    name: str
    type: str = "user"  # "system" or "user"
    message_count: int = 0
    unread_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "message_count": self.message_count,
            "unread_count": self.unread_count
        }
