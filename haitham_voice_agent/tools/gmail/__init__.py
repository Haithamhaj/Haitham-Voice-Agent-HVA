"""Gmail module package"""

from .connection_manager import ConnectionManager
from .gmail_api_handler import GmailAPIHandler
from .imap_handler import IMAPHandler
from .smtp_handler import SMTPHandler
from .models.email_message import EmailMessage, Draft, Label, Attachment

__all__ = [
    "ConnectionManager",
    "GmailAPIHandler",
    "IMAPHandler",
    "SMTPHandler",
    "EmailMessage",
    "Draft",
    "Label",
    "Attachment"
]
