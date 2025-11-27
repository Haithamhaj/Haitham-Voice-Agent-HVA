# 📧 SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## HVA Gmail Integration Module

**Version:** 1.0 (Complete - Performance Optimized)  
**Author:** Haitham  
**Target Platform:** macOS (Apple Silicon)  
**Parent System:** Haitham Voice Agent (HVA)  
**Language:** English  
**Status:** Ready for Implementation

---

## TABLE OF CONTENTS

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Architecture Design](#3-architecture-design)
4. [Functional Requirements](#4-functional-requirements)
5. [Performance Requirements](#5-performance-requirements)
6. [Security & Privacy](#6-security--privacy)
7. [Error Handling](#7-error-handling)
8. [Implementation Constraints](#8-implementation-constraints)
9. [Testing Requirements](#9-testing-requirements)
10. [Acceptance Criteria](#10-acceptance-criteria)
11. [Builder Instructions](#11-builder-instructions)

---

## 1. INTRODUCTION

### 1.1 Purpose

This SRS defines the **complete technical specification** for integrating Gmail into HVA using a **hybrid approach**:

- **Gmail API** (primary) for drafts, labels, search, and rich features
- **IMAP/SMTP** (fallback) for universal email support and reading

This module enables voice-controlled email operations with:
- ✅ **High performance** (< 2s for most operations)
- ✅ **Reliability** (no AppleScript fragility)
- ✅ **Rich features** (labels, drafts, threads)
- ✅ **Privacy-first** (local credentials, no cloud dependencies)
- ✅ **Fallback support** (works with any email provider via IMAP)

### 1.2 Why Not AppleScript?

| Issue | AppleScript | Gmail API + IMAP |
|-------|-------------|------------------|
| **Reliability** | ❌ Breaks with macOS updates | ✅ Stable APIs |
| **Performance** | ❌ Slow (3-5s per operation) | ✅ Fast (< 2s) |
| **Features** | ❌ Limited | ✅ Full Gmail features |
| **Portability** | ❌ macOS Mail only | ✅ Any email provider |
| **Debugging** | ❌ Opaque errors | ✅ Clear error messages |

### 1.3 Scope

**In Scope:**
- Gmail API for primary operations
- IMAP/SMTP for fallback and non-Gmail accounts
- Draft creation and management
- Email reading, searching, summarization
- Label management
- Thread handling
- Attachment listing
- Smart reply generation (via LLM)

**Out of Scope:**
- Automatic sending (requires explicit user confirmation)
- Calendar integration (future SRS)
- Contact management (future SRS)
- Email filtering rules
- Spam management

### 1.4 Definitions

- **Gmail API**: Google's official REST API for Gmail
- **IMAP**: Internet Message Access Protocol (reading)
- **SMTP**: Simple Mail Transfer Protocol (sending)
- **Draft**: Unsent email stored on server
- **Label**: Gmail's equivalent of folders
- **Thread**: Conversation containing multiple emails
- **OAuth 2.0**: Secure authentication flow for Gmail API

---

## 2. SYSTEM OVERVIEW

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HVA Voice Interface                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Gmail Module (gmail_integration.py)             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Connection Manager (Auto-Select)           │   │
│  │  • Tries Gmail API first                             │   │
│  │  • Falls back to IMAP/SMTP if API unavailable       │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      │                                        │
│         ┌────────────┴────────────┐                          │
│         ▼                         ▼                          │
│  ┌─────────────┐          ┌─────────────┐                   │
│  │ Gmail API   │          │ IMAP/SMTP   │                   │
│  │ Handler     │          │ Handler     │                   │
│  └─────────────┘          └─────────────┘                   │
└──────────┬───────────────────────┬────────────────────────┘
           │                       │
           ▼                       ▼
    ┌──────────────┐      ┌──────────────┐
    │ Gmail Server │      │ IMAP Server  │
    │ (API calls)  │      │ (IMAP/SMTP)  │
    └──────────────┘      └──────────────┘
```

### 2.2 Component Responsibilities

#### 2.2.1 Connection Manager
- Auto-detects best connection method
- Manages credentials securely
- Handles authentication flow
- Switches between API and IMAP seamlessly

#### 2.2.2 Gmail API Handler
- Executes Gmail-specific operations
- Manages OAuth tokens
- Handles rate limiting
- Provides rich features (labels, drafts, threads)

#### 2.2.3 IMAP/SMTP Handler
- Universal email support
- Reading emails via IMAP
- Sending via SMTP
- Works with any provider (Gmail, Outlook, custom)

---

## 3. ARCHITECTURE DESIGN

### 3.1 Module Structure

```
haitham_voice_agent/
  tools/
    gmail/
      __init__.py
      connection_manager.py     # Auto-selects API vs IMAP
      gmail_api_handler.py      # Gmail API operations
      imap_handler.py           # IMAP operations
      smtp_handler.py           # SMTP operations
      auth/
        oauth_flow.py           # OAuth 2.0 for Gmail API
        credentials_store.py    # Secure credential storage
      models/
        email_message.py        # Unified email data model
        draft.py                # Draft representation
        label.py                # Label/folder representation
      utils/
        text_processing.py      # Email parsing, cleaning
        attachment_handler.py   # Attachment metadata
      config.py                 # Configuration constants
      exceptions.py             # Custom exceptions
  tests/
    test_gmail_integration.py
```

### 3.2 Unified Email Model

All operations return a **consistent data model** regardless of API vs IMAP:

```python
@dataclass
class EmailMessage:
    """Unified email representation"""
    id: str                    # Message ID
    thread_id: str             # Thread/conversation ID
    from_: str                 # Sender email
    to: List[str]              # Recipients
    cc: List[str]              # CC recipients
    subject: str               # Subject line
    body_text: str             # Plain text body
    body_html: Optional[str]   # HTML body (if available)
    date: datetime             # Sent/received date
    labels: List[str]          # Gmail labels or IMAP folders
    is_unread: bool            # Read status
    has_attachments: bool      # Attachment flag
    attachments: List[Attachment]  # Attachment metadata
    snippet: str               # First 100 chars preview
    raw_headers: Dict          # Email headers
```

### 3.3 Connection Strategy

```python
class ConnectionManager:
    """
    Intelligent connection manager that auto-selects best method
    
    Priority:
    1. Gmail API (if credentials exist and valid)
    2. IMAP/SMTP (fallback)
    """
    
    def __init__(self):
        self.gmail_api = None
        self.imap_handler = None
        self.smtp_handler = None
        self.active_handler = None
        
    async def initialize(self):
        """
        Auto-detect and initialize best connection method
        """
        # Try Gmail API first
        if self._has_gmail_credentials():
            try:
                self.gmail_api = await GmailAPIHandler.initialize()
                self.active_handler = "gmail_api"
                logger.info("Gmail API initialized successfully")
                return
            except Exception as e:
                logger.warning(f"Gmail API init failed: {e}, falling back to IMAP")
        
        # Fallback to IMAP/SMTP
        self.imap_handler = await IMAPHandler.initialize()
        self.smtp_handler = await SMTPHandler.initialize()
        self.active_handler = "imap_smtp"
        logger.info("IMAP/SMTP initialized successfully")
```

---

## 4. FUNCTIONAL REQUIREMENTS

### 4.1 Core Email Operations

#### FR-E1: Read Latest Emails

**Description:** Retrieve the N most recent emails from inbox

**Inputs:**
```python
{
  "limit": int,           # Number of emails (default: 10, max: 50)
  "label": str,           # Gmail label or IMAP folder (default: "INBOX")
  "unread_only": bool,    # Filter unread only (default: False)
  "include_body": bool    # Include full body or just snippet (default: False)
}
```

**Output:**
```python
{
  "emails": List[EmailMessage],
  "total_count": int,
  "has_more": bool
}
```

**Performance Target:** < 2 seconds for 10 emails

**Implementation Notes:**
- Gmail API: Use `users.messages.list` with `maxResults`
- IMAP: Use `SEARCH` + `FETCH` with appropriate flags

---

#### FR-E2: Search Emails

**Description:** Search emails by query

**Inputs:**
```python
{
  "query": str,          # Search query (Gmail syntax or keywords)
  "limit": int,          # Max results (default: 20)
  "label": str,          # Scope to label/folder
  "date_from": date,     # Filter by date range
  "date_to": date
}
```

**Query Examples:**
- `"from:john@example.com"`
- `"subject:invoice"`
- `"has:attachment"`
- `"is:unread"`

**Output:** Same as FR-E1

**Performance Target:** < 3 seconds

**Implementation Notes:**
- Gmail API: Native query syntax support
- IMAP: Translate to IMAP SEARCH syntax

---

#### FR-E3: Get Email by ID

**Description:** Retrieve full email details by ID

**Inputs:**
```python
{
  "email_id": str,
  "include_html": bool   # Include HTML body (default: False)
}
```

**Output:** Single `EmailMessage` object

**Performance Target:** < 1 second

---

#### FR-E4: Create Draft

**Description:** Create email draft (not sent)

**Inputs:**
```python
{
  "to": List[str],
  "cc": List[str],       # Optional
  "subject": str,
  "body": str,
  "body_type": str,      # "plain" or "html" (default: "plain")
  "reply_to_id": str     # Optional: if replying to email
}
```

**Output:**
```python
{
  "draft_id": str,
  "message_id": str,
  "status": "created"
}
```

**Performance Target:** < 1.5 seconds

**Implementation Notes:**
- Gmail API: Use `users.drafts.create`
- IMAP: Store in "Drafts" folder

---

#### FR-E5: Update Draft

**Description:** Modify existing draft

**Inputs:**
```python
{
  "draft_id": str,
  # Same fields as FR-E4 (all optional, only update provided fields)
}
```

**Output:** Updated draft metadata

**Performance Target:** < 1.5 seconds

---

#### FR-E6: List Drafts

**Description:** Get all drafts

**Inputs:**
```python
{
  "limit": int    # Max results (default: 10)
}
```

**Output:** List of draft metadata

**Performance Target:** < 2 seconds

---

#### FR-E7: Delete Draft

**Description:** Delete draft permanently

**Inputs:**
```python
{
  "draft_id": str
}
```

**Output:**
```python
{
  "status": "deleted",
  "draft_id": str
}
```

**Performance Target:** < 1 second

---

#### FR-E8: Send Draft (with Confirmation)

**Description:** Send a draft after explicit user confirmation

**Inputs:**
```python
{
  "draft_id": str
}
```

**Flow:**
1. Read draft content
2. Generate preview via TTS:
   - "I will send email to [recipient]"
   - "Subject: [subject]"
   - "Body preview: [first 50 words]"
3. Ask: **"Do you confirm sending this email?"**
4. If confirmed → send via Gmail API or SMTP
5. If rejected → cancel and inform user

**Output:**
```python
{
  "status": "sent",
  "message_id": str,
  "sent_at": datetime
}
```

**Performance Target:** < 2 seconds (after confirmation)

**Safety Rules:**
- ❌ NEVER send without explicit voice confirmation
- ❌ NEVER send automatically based on voice command alone
- ✅ ALWAYS read recipient, subject, and preview before sending

---

#### FR-E9: Mark as Read/Unread

**Description:** Change read status

**Inputs:**
```python
{
  "email_id": str,
  "mark_as": str    # "read" or "unread"
}
```

**Output:** Status confirmation

**Performance Target:** < 1 second

---

#### FR-E10: Apply Label / Move to Folder

**Description:** Organize emails

**Inputs:**
```python
{
  "email_id": str,
  "label": str,         # Gmail label or IMAP folder name
  "action": str         # "add" or "move" (move removes from current)
}
```

**Output:** Status confirmation

**Performance Target:** < 1 second

---

#### FR-E11: List Labels / Folders

**Description:** Get available labels/folders

**Inputs:** None

**Output:**
```python
{
  "labels": List[str],
  "system_labels": List[str],    # INBOX, SENT, DRAFTS, etc.
  "custom_labels": List[str]     # User-created
}
```

**Performance Target:** < 1 second

---

### 4.2 LLM-Enhanced Operations

These operations combine email data with LLM processing.

#### FR-L1: Summarize Email

**Description:** Generate concise summary of email(s)

**Inputs:**
```python
{
  "email_id": str,              # Single email, OR
  "thread_id": str,             # Entire thread
  "summary_length": str         # "brief" | "detailed" (default: "brief")
}
```

**Processing Flow:**
1. Fetch email(s) via Gmail API or IMAP
2. Extract text content
3. Route to **Gemini** for summarization
4. Return structured summary

**Output:**
```python
{
  "summary": str,
  "key_points": List[str],      # Bullet points
  "action_items": List[str],    # Extracted tasks (if any)
  "sentiment": str              # "positive" | "neutral" | "negative"
}
```

**Performance Target:** < 5 seconds

---

#### FR-L2: Generate Smart Reply

**Description:** Generate draft replies using LLM

**Inputs:**
```python
{
  "email_id": str,
  "reply_type": str,            # "brief" | "detailed" | "formal" | "casual"
  "key_points": List[str],      # Optional: points to address
  "tone": str                   # Optional: "professional" | "friendly"
}
```

**Processing Flow:**
1. Fetch original email
2. Extract context (sender, subject, body)
3. Route to **GPT-4o** with reply generation prompt
4. Generate draft
5. Create draft via FR-E4
6. Return draft ID for review

**Output:**
```python
{
  "draft_id": str,
  "preview": str,               # First 100 words
  "status": "draft_created"
}
```

**Performance Target:** < 4 seconds

**Safety:**
- Never sends automatically
- Always creates draft for user review
- User must explicitly send via FR-E8

---

#### FR-L3: Extract Action Items from Thread

**Description:** Extract tasks and deadlines from email conversation

**Inputs:**
```python
{
  "thread_id": str
}
```

**Processing Flow:**
1. Fetch all messages in thread
2. Route to **Gemini** for analysis
3. Extract tasks with structured format

**Output:**
```python
{
  "action_items": [
    {
      "task": str,
      "assignee": str,          # Extracted from email
      "deadline": date,         # If mentioned
      "priority": str,          # "high" | "medium" | "low"
      "source_email_id": str
    }
  ],
  "decisions": List[str],       # Key decisions made
  "next_steps": List[str]
}
```

**Performance Target:** < 6 seconds for 10-message thread

---

#### FR-L4: Translate Email

**Description:** Translate email to target language

**Inputs:**
```python
{
  "email_id": str,
  "target_language": str        # "ar" | "en" | "es" | etc.
}
```

**Processing Flow:**
1. Fetch email
2. Route to **Gemini** for translation
3. Return translated content

**Output:**
```python
{
  "original_body": str,
  "translated_body": str,
  "detected_language": str
}
```

**Performance Target:** < 4 seconds

---

### 4.3 Voice Command Mapping

| Voice Command (English) | Voice Command (Arabic) | Function |
|-------------------------|------------------------|----------|
| "Read my latest emails" | "اقرأ آخر الإيميلات" | FR-E1 |
| "Search emails from John" | "ابحث عن إيميلات من جون" | FR-E2 |
| "Summarize this email" | "لخص هذا الإيميل" | FR-L1 |
| "Create a draft reply" | "اكتب رد مسودة" | FR-L2 |
| "Create email to [person]" | "اكتب إيميل إلى [شخص]" | FR-E4 |
| "Show my drafts" | "اعرض المسودات" | FR-E6 |
| "Send draft" | "أرسل المسودة" | FR-E8 (with confirmation) |
| "Mark as read" | "علّم كمقروء" | FR-E9 |
| "Move to archive" | "انقل للأرشيف" | FR-E10 |

---

## 5. PERFORMANCE REQUIREMENTS

### 5.1 Response Time Targets

| Operation | Target | Acceptable | Maximum |
|-----------|--------|------------|---------|
| Read 10 emails | < 2s | < 3s | 5s |
| Search emails | < 3s | < 4s | 6s |
| Get single email | < 1s | < 1.5s | 2s |
| Create draft | < 1.5s | < 2s | 3s |
| Send email | < 2s | < 3s | 4s |
| Summarize email | < 5s | < 7s | 10s |
| Generate reply | < 4s | < 6s | 8s |

### 5.2 Caching Strategy

To achieve performance targets, implement aggressive caching:

```python
class EmailCache:
    """
    Multi-layer caching for Gmail operations
    """
    
    def __init__(self):
        # Layer 1: In-memory cache (LRU)
        self.memory_cache = LRUCache(maxsize=100)
        
        # Layer 2: Disk cache (for larger objects)
        self.disk_cache_path = "~/.hva/email_cache/"
        
        # Layer 3: Metadata cache (for search results)
        self.metadata_cache = {}
    
    def cache_email(self, email: EmailMessage, ttl: int = 300):
        """Cache email for 5 minutes by default"""
        self.memory_cache[email.id] = {
            "data": email,
            "cached_at": datetime.now(),
            "ttl": ttl
        }
    
    def get_cached_email(self, email_id: str) -> Optional[EmailMessage]:
        """Retrieve from cache if fresh"""
        cached = self.memory_cache.get(email_id)
        if cached and self._is_fresh(cached):
            return cached["data"]
        return None
```

**Caching Rules:**
- Email content: 5 minutes TTL
- Search results: 2 minutes TTL
- Labels list: 10 minutes TTL
- Draft list: 1 minute TTL (frequently changes)
- Summaries: 30 minutes TTL
- Invalidate cache on: send, delete, move operations

### 5.3 Batch Operations

For operations on multiple emails:

```python
async def mark_multiple_as_read(email_ids: List[str]):
    """
    Batch operation: mark multiple emails as read
    Uses Gmail API batchModify (10x faster than individual calls)
    """
    if using_gmail_api:
        # Single API call for up to 1000 emails
        await gmail_api.batch_modify(
            ids=email_ids,
            add_labels=[],
            remove_labels=["UNREAD"]
        )
    else:
        # IMAP: use single STORE command
        await imap.store(email_ids, '+FLAGS', '\\Seen')
```

### 5.4 Connection Pooling

```python
class IMAPConnectionPool:
    """
    Maintain persistent IMAP connections
    Avoids reconnection overhead (1-2s per connection)
    """
    
    def __init__(self, pool_size: int = 3):
        self.pool = asyncio.Queue(maxsize=pool_size)
        self._initialize_pool()
    
    async def get_connection(self):
        """Get connection from pool"""
        return await self.pool.get()
    
    async def return_connection(self, conn):
        """Return connection to pool"""
        await self.pool.put(conn)
```

---

## 6. SECURITY & PRIVACY

### 6.1 Credential Storage

**Gmail API Credentials:**
```
~/.hva/credentials/
  gmail_oauth_token.json       # OAuth token (encrypted)
  gmail_client_secret.json     # OAuth client credentials
```

**IMAP/SMTP Credentials:**
```
~/.hva/credentials/
  email_credentials.json       # Encrypted storage
```

**Encryption:**
```python
from cryptography.fernet import Fernet
import keyring  # macOS Keychain integration

class CredentialStore:
    """
    Secure credential storage using macOS Keychain
    """
    
    def __init__(self):
        # Generate or retrieve encryption key from Keychain
        self.key = keyring.get_password("HVA", "encryption_key")
        if not self.key:
            self.key = Fernet.generate_key()
            keyring.set_password("HVA", "encryption_key", self.key)
        
        self.cipher = Fernet(self.key)
    
    def store_credential(self, service: str, credential: dict):
        """Encrypt and store credential"""
        encrypted = self.cipher.encrypt(json.dumps(credential).encode())
        keyring.set_password("HVA", service, encrypted.decode())
    
    def retrieve_credential(self, service: str) -> dict:
        """Decrypt and retrieve credential"""
        encrypted = keyring.get_password("HVA", service)
        if encrypted:
            decrypted = self.cipher.decrypt(encrypted.encode())
            return json.loads(decrypted)
        return None
```

### 6.2 OAuth 2.0 Flow (Gmail API)

**First-time setup:**
1. User runs: `hva setup-gmail`
2. System opens browser with OAuth consent screen
3. User authorizes HVA
4. System stores refresh token securely
5. Token auto-refreshes before expiry

**Implementation:**
```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly'
]

class GmailAuthManager:
    async def authenticate(self):
        """
        OAuth 2.0 flow for Gmail API
        """
        creds = None
        token_path = self.credential_store.token_path
        
        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # Refresh if expired
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # New auth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/client_secret.json', SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
```

### 6.3 Security Rules

**Must Always:**
- ✅ Encrypt credentials at rest
- ✅ Use macOS Keychain for encryption keys
- ✅ Never log email content or credentials
- ✅ Auto-refresh OAuth tokens before expiry
- ✅ Require confirmation before sending
- ✅ Clear sensitive data from memory after use

**Must Never:**
- ❌ Store passwords in plain text
- ❌ Send emails without confirmation
- ❌ Log full email bodies
- ❌ Share credentials between users
- ❌ Cache authentication tokens in plain text

### 6.4 Rate Limiting

**Gmail API Limits:**
- 250 quota units per user per second
- 1,000,000,000 quota units per day

**Mitigation:**
```python
class RateLimiter:
    def __init__(self, max_requests_per_second: int = 10):
        self.max_requests = max_requests_per_second
        self.requests = deque()
    
    async def acquire(self):
        """
        Rate limit API calls to stay under quota
        """
        now = time.time()
        
        # Remove old requests
        while self.requests and self.requests[0] < now - 1:
            self.requests.popleft()
        
        # Wait if at limit
        if len(self.requests) >= self.max_requests:
            sleep_time = 1 - (now - self.requests[0])
            await asyncio.sleep(sleep_time)
        
        self.requests.append(time.time())
```

---

## 7. ERROR HANDLING

### 7.1 Error Types

```python
class GmailModuleError(Exception):
    """Base exception for Gmail module"""
    pass

class AuthenticationError(GmailModuleError):
    """OAuth or IMAP login failed"""
    pass

class ConnectionError(GmailModuleError):
    """Network or server connection failed"""
    pass

class QuotaExceededError(GmailModuleError):
    """Gmail API quota exceeded"""
    pass

class EmailNotFoundError(GmailModuleError):
    """Requested email does not exist"""
    pass

class DraftCreationError(GmailModuleError):
    """Failed to create draft"""
    pass

class SendingError(GmailModuleError):
    """Failed to send email"""
    pass
```

### 7.2 Error Response Format

All errors return structured JSON:

```python
{
  "error": true,
  "error_type": "AuthenticationError",
  "message": "OAuth token expired. Please re-authenticate.",
  "details": {
    "service": "gmail_api",
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "suggestion": "Run 'hva setup-gmail' to re-authenticate",
  "recoverable": true
}
```

### 7.3 Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class GmailOperations:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ConnectionError)
    )
    async def fetch_email(self, email_id: str):
        """
        Auto-retry on connection errors
        Exponential backoff: 2s, 4s, 8s
        """
        # Implementation
```

### 7.4 Fallback Strategy

```python
async def read_emails(self, limit: int = 10):
    """
    Automatic fallback: Gmail API → IMAP
    """
    try:
        # Try Gmail API first
        if self.active_handler == "gmail_api":
            return await self.gmail_api.list_messages(limit)
    except (AuthenticationError, QuotaExceededError) as e:
        logger.warning(f"Gmail API failed: {e}, falling back to IMAP")
        
        # Fallback to IMAP
        if not self.imap_handler:
            self.imap_handler = await IMAPHandler.initialize()
        
        return await self.imap_handler.list_messages(limit)
```

---

## 8. IMPLEMENTATION CONSTRAINTS

### 8.1 Technology Stack

**Required Libraries:**
```txt
# Gmail API
google-api-python-client==2.108.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.0

# IMAP/SMTP
imap-tools==1.7.1
aiosmtplib==3.0.1

# Security
cryptography==41.0.7
keyring==24.3.0

# Utilities
pydantic==2.5.3
tenacity==8.2.3
```

### 8.2 Configuration File

```python
# tools/gmail/config.py

from pydantic import BaseModel

class GmailConfig(BaseModel):
    """Gmail module configuration"""
    
    # Connection settings
    preferred_method: str = "gmail_api"  # or "imap"
    enable_fallback: bool = True
    
    # Performance
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    connection_pool_size: int = 3
    max_requests_per_second: int = 10
    
    # Paths
    credentials_dir: str = "~/.hva/credentials/"
    cache_dir: str = "~/.hva/email_cache/"
    
    # Gmail API settings
    oauth_scopes: list = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    # IMAP settings (fallback)
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    imap_use_ssl: bool = True
    
    # SMTP settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_use_tls: bool = True
    
    # Defaults
    default_email_limit: int = 10
    max_email_limit: int = 50
    default_summary_length: str = "brief"
```

### 8.3 Environment Variables

```bash
# Required for Gmail API
export GMAIL_CLIENT_SECRET_PATH="~/.hva/credentials/client_secret.json"

# Required for IMAP/SMTP fallback
export EMAIL_ADDRESS="user@gmail.com"
export EMAIL_PASSWORD="app-specific-password"

# Optional
export HVA_GMAIL_DEBUG="false"
export HVA_GMAIL_CACHE_ENABLED="true"
```

### 8.4 File Structure

```
tools/gmail/
├── __init__.py
├── connection_manager.py       # Main orchestrator
├── gmail_api_handler.py        # Gmail API implementation
├── imap_handler.py             # IMAP implementation
├── smtp_handler.py             # SMTP implementation
├── config.py                   # Configuration
├── exceptions.py               # Custom exceptions
│
├── auth/
│   ├── __init__.py
│   ├── oauth_flow.py           # OAuth 2.0 flow
│   └── credentials_store.py    # Secure storage
│
├── models/
│   ├── __init__.py
│   ├── email_message.py        # Unified email model
│   ├── draft.py                # Draft model
│   ├── label.py                # Label model
│   └── attachment.py           # Attachment model
│
├── utils/
│   ├── __init__.py
│   ├── cache.py                # Caching layer
│   ├── rate_limiter.py         # Rate limiting
│   ├── text_processing.py     # Email parsing
│   └── batch_operations.py    # Batch utilities
│
└── llm_integration/
    ├── __init__.py
    ├── summarizer.py           # Email summarization (Gemini)
    └── reply_generator.py      # Smart replies (GPT)
```

---

## 9. TESTING REQUIREMENTS

### 9.1 Unit Tests

**Required Test Coverage: ≥ 85%**

```python
# tests/test_gmail_integration.py

import pytest
from tools.gmail import ConnectionManager, GmailAPIHandler, IMAPHandler

class TestConnectionManager:
    """Test connection initialization and fallback"""
    
    @pytest.mark.asyncio
    async def test_gmail_api_initialization(self):
        """Test Gmail API connects successfully"""
        manager = ConnectionManager()
        await manager.initialize()
        assert manager.active_handler == "gmail_api"
    
    @pytest.mark.asyncio
    async def test_fallback_to_imap(self, mock_failed_oauth):
        """Test automatic fallback to IMAP when Gmail API fails"""
        manager = ConnectionManager()
        await manager.initialize()
        assert manager.active_handler == "imap_smtp"
    
    @pytest.mark.asyncio
    async def test_credential_loading(self):
        """Test credentials load from secure storage"""
        manager = ConnectionManager()
        creds = await manager._load_credentials()
        assert creds is not None

class TestEmailOperations:
    """Test core email functions"""
    
    @pytest.mark.asyncio
    async def test_read_latest_emails(self, mock_gmail_api):
        """Test reading latest emails returns correct format"""
        result = await mock_gmail_api.list_messages(limit=5)
        assert len(result["emails"]) == 5
        assert all(isinstance(e, EmailMessage) for e in result["emails"])
    
    @pytest.mark.asyncio
    async def test_search_emails(self, mock_gmail_api):
        """Test email search with query"""
        result = await mock_gmail_api.search("from:test@example.com")
        assert result["total_count"] >= 0
    
    @pytest.mark.asyncio
    async def test_create_draft(self, mock_gmail_api):
        """Test draft creation"""
        draft = await mock_gmail_api.create_draft(
            to=["recipient@example.com"],
            subject="Test",
            body="Test body"
        )
        assert draft["status"] == "created"
        assert "draft_id" in draft

class TestCaching:
    """Test caching layer"""
    
    def test_cache_stores_email(self, email_cache):
        """Test email caching"""
        email = EmailMessage(id="123", ...)
        email_cache.cache_email(email)
        cached = email_cache.get_cached_email("123")
        assert cached.id == "123"
    
    def test_cache_expiry(self, email_cache):
        """Test cache TTL expiration"""
        email = EmailMessage(id="456", ...)
        email_cache.cache_email(email, ttl=1)
        time.sleep(2)
        cached = email_cache.get_cached_email("456")
        assert cached is None

class TestLLMIntegration:
    """Test LLM-enhanced operations"""
    
    @pytest.mark.asyncio
    async def test_email_summarization(self, mock_gemini):
        """Test email summarization via Gemini"""
        summary = await summarize_email("email_id_123")
        assert "summary" in summary
        assert "key_points" in summary
    
    @pytest.mark.asyncio
    async def test_reply_generation(self, mock_gpt):
        """Test smart reply generation"""
        draft = await generate_smart_reply(
            email_id="email_id_123",
            reply_type="brief"
        )
        assert "draft_id" in draft
```

### 9.2 Integration Tests

```python
class TestGmailAPIIntegration:
    """Integration tests with real Gmail API (test account)"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_email_workflow(self):
        """Test complete workflow: read → reply → send"""
        manager = ConnectionManager()
        await manager.initialize()
        
        # 1. Read latest email
        emails = await manager.read_emails(limit=1)
        assert len(emails["emails"]) > 0
        
        # 2. Generate reply
        draft = await manager.create_reply_draft(
            email_id=emails["emails"][0].id,
            body="Test reply"
        )
        assert draft["status"] == "created"
        
        # 3. Verify draft was created
        drafts = await manager.list_drafts()
        assert any(d["id"] == draft["draft_id"] for d in drafts["drafts"])
        
        # 4. Clean up (delete draft)
        await manager.delete_draft(draft["draft_id"])
```

### 9.3 Performance Tests

```python
class TestPerformance:
    """Performance benchmarks"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_read_emails_latency(self, benchmark):
        """Test email reading meets < 2s target"""
        manager = ConnectionManager()
        await manager.initialize()
        
        result = benchmark(
            lambda: asyncio.run(manager.read_emails(limit=10))
        )
        
        assert result.stats["mean"] < 2.0  # < 2 seconds
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_hit_performance(self, benchmark):
        """Test cached reads are < 100ms"""
        manager = ConnectionManager()
        await manager.initialize()
        
        # Prime cache
        await manager.read_emails(limit=10)
        
        # Benchmark cached read
        result = benchmark(
            lambda: asyncio.run(manager.read_emails(limit=10))
        )
        
        assert result.stats["mean"] < 0.1  # < 100ms
```

---

## 10. ACCEPTANCE CRITERIA

The Gmail module is **complete and correct** when:

### 10.1 Functional Criteria

- [ ] **FR-E1 to FR-E11:** All core email operations work correctly
- [ ] **FR-L1 to FR-L4:** All LLM-enhanced operations work correctly
- [ ] **Gmail API:** Successful OAuth flow and API operations
- [ ] **IMAP/SMTP:** Fallback works when Gmail API unavailable
- [ ] **Unified Model:** All operations return consistent `EmailMessage` format
- [ ] **Voice Commands:** All listed voice commands trigger correct functions

### 10.2 Performance Criteria

- [ ] Read 10 emails: **< 2 seconds** (95th percentile)
- [ ] Search emails: **< 3 seconds** (95th percentile)
- [ ] Create draft: **< 1.5 seconds** (95th percentile)
- [ ] Summarize email: **< 5 seconds** (95th percentile)
- [ ] Generate reply: **< 4 seconds** (95th percentile)
- [ ] Cache hit rate: **> 60%** for repeated operations

### 10.3 Security Criteria

- [ ] **Credentials:** Stored encrypted in macOS Keychain
- [ ] **OAuth:** Token auto-refreshes before expiry
- [ ] **No Logs:** Email content never logged
- [ ] **Confirmation:** Sending requires explicit voice confirmation
- [ ] **Isolation:** No credential sharing between users

### 10.4 Reliability Criteria

- [ ] **Fallback:** Auto-switches to IMAP if Gmail API fails
- [ ] **Retry:** Auto-retries transient network errors (3x with backoff)
- [ ] **Error Handling:** All errors return structured JSON
- [ ] **No Crashes:** Handles all edge cases gracefully
- [ ] **Rate Limiting:** Respects Gmail API quota limits

### 10.5 Testing Criteria

- [ ] **Unit Tests:** ≥ 85% code coverage
- [ ] **Integration Tests:** All workflows tested end-to-end
- [ ] **Performance Tests:** All latency targets validated
- [ ] **Manual Tests:** ≥ 20 voice commands tested successfully

---

## 11. BUILDER INSTRUCTIONS

### 11.1 Pre-Implementation Checklist

**Before writing ANY code, the builder MUST:**

1. **Read this entire SRS document**
2. **Verify understanding of:**
   - Gmail API vs IMAP/SMTP differences
   - OAuth 2.0 flow
   - Security requirements
   - Performance targets
   - Fallback strategy

3. **Prepare environment:**
   ```bash
   # Create project structure
   mkdir -p tools/gmail/{auth,models,utils,llm_integration}
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Obtain Gmail API credentials:**
   - Go to Google Cloud Console
   - Create new project: "HVA Gmail Integration"
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `client_secret.json`
   - Store in `~/.hva/credentials/`

5. **Create implementation plan:**
   - Produce `GMAIL_MODULE_IMPLEMENTATION_PLAN.md`
   - List all modules to build
   - Define build order
   - Estimate time per module
   - Wait for user approval before coding

### 11.2 Implementation Order

**Phase 1: Foundation (Week 1)**
1. `models/email_message.py` - Define data models
2. `config.py` - Configuration management
3. `exceptions.py` - Custom exceptions
4. `auth/credentials_store.py` - Secure storage
5. `auth/oauth_flow.py` - OAuth 2.0 flow

**Phase 2: Gmail API (Week 1-2)**
1. `gmail_api_handler.py` - Core Gmail API wrapper
2. `utils/cache.py` - Caching layer
3. `utils/rate_limiter.py` - Rate limiting
4. Test Gmail API operations

**Phase 3: IMAP/SMTP (Week 2)**
1. `imap_handler.py` - IMAP operations
2. `smtp_handler.py` - SMTP operations
3. Test fallback mechanism

**Phase 4: Integration (Week 2-3)**
1. `connection_manager.py` - Orchestration layer
2. `llm_integration/summarizer.py` - Email summarization
3. `llm_integration/reply_generator.py` - Smart replies
4. Integration with main HVA

**Phase 5: Testing & Polish (Week 3)**
1. Write comprehensive tests
2. Performance optimization
3. Documentation
4. User testing

### 11.3 Development Guidelines

**Code Style:**
```python
# Use type hints everywhere
async def read_emails(self, limit: int = 10) -> Dict[str, Any]:
    """
    Read latest emails from inbox
    
    Args:
        limit: Maximum number of emails to retrieve (1-50)
    
    Returns:
        Dictionary containing emails and metadata
    
    Raises:
        ConnectionError: If unable to connect to server
        AuthenticationError: If credentials invalid
    """
    pass

# Use structured logging
logger.info(
    "email_read_requested",
    limit=limit,
    handler=self.active_handler,
    cache_hit=cache_hit
)

# Use Pydantic for validation
from pydantic import BaseModel, validator

class EmailRequest(BaseModel):
    limit: int = 10
    
    @validator('limit')
    def validate_limit(cls, v):
        if not 1 <= v <= 50:
            raise ValueError('limit must be between 1 and 50')
        return v
```

**Error Handling:**
```python
# Always use structured errors
try:
    result = await self.gmail_api.fetch_email(email_id)
except GoogleAPIError as e:
    raise ConnectionError(
        message=f"Failed to fetch email: {e}",
        details={"email_id": email_id, "service": "gmail_api"},
        suggestion="Check network connection and try again",
        recoverable=True
    )
```

**Async/Await:**
```python
# Use async for all I/O operations
async def fetch_multiple_emails(self, email_ids: List[str]):
    """Fetch multiple emails concurrently"""
    tasks = [self.fetch_email(id) for id in email_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

### 11.4 Testing Requirements

**Run tests before each commit:**
```bash
# Unit tests
pytest tests/test_gmail_integration.py -v

# Integration tests
pytest tests/test_gmail_integration.py -v -m integration

# Performance tests
pytest tests/test_gmail_integration.py -v -m performance

# Coverage report
pytest --cov=tools.gmail --cov-report=html
```

### 11.5 Documentation

**Each module must include:**
1. Module docstring explaining purpose
2. Function docstrings with:
   - Description
   - Args (with types)
   - Returns (with type)
   - Raises (all exceptions)
   - Examples
3. Inline comments for complex logic
4. README.md with:
   - Setup instructions
   - Usage examples
   - Troubleshooting guide

### 11.6 Final Checklist

Before marking as complete:

- [ ] All functional requirements implemented
- [ ] All performance targets met
- [ ] All security requirements satisfied
- [ ] Test coverage ≥ 85%
- [ ] No hardcoded credentials
- [ ] Error messages user-friendly
- [ ] Logging comprehensive
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] Manual testing passed (≥ 20 commands)

---

## APPENDIX A: Gmail API Quick Reference

### Common Operations

**List Messages:**
```python
service.users().messages().list(
    userId='me',
    maxResults=10,
    q='is:unread',  # Optional query
    labelIds=['INBOX']
).execute()
```

**Get Message:**
```python
service.users().messages().get(
    userId='me',
    id=message_id,
    format='full'  # or 'metadata', 'minimal', 'raw'
).execute()
```

**Create Draft:**
```python
draft = {
    'message': {
        'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
    }
}
service.users().drafts().create(
    userId='me',
    body=draft
).execute()
```

**Send Draft:**
```python
service.users().drafts().send(
    userId='me',
    body={'id': draft_id}
).execute()
```

**Batch Modify:**
```python
service.users().messages().batchModify(
    userId='me',
    body={
        'ids': [message_id_1, message_id_2],
        'removeLabelIds': ['UNREAD'],
        'addLabelIds': ['IMPORTANT']
    }
).execute()
```

---

## APPENDIX B: IMAP Command Reference

**Connect:**
```python
import imaplib
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email, password)
```

**List Folders:**
```python
status, folders = mail.list()
```

**Select Folder:**
```python
mail.select('INBOX')
```

**Search:**
```python
status, messages = mail.search(None, 'UNSEEN')  # Unread
status, messages = mail.search(None, 'FROM', 'user@example.com')
status, messages = mail.search(None, 'SUBJECT', 'invoice')
```

**Fetch:**
```python
status, data = mail.fetch(message_id, '(RFC822)')  # Full message
status, data = mail.fetch(message_id, '(BODY.PEEK[TEXT])')  # Body only
```

**Mark as Read:**
```python
mail.store(message_id, '+FLAGS', '\\Seen')
```

---

## APPENDIX C: Performance Optimization Checklist

- [ ] **Connection pooling:** Reuse IMAP connections
- [ ] **Batch operations:** Use `batchModify` for multiple emails
- [ ] **Caching:** Cache emails, search results, labels (with TTL)
- [ ] **Parallel fetching:** Use `asyncio.gather()` for multiple emails
- [ ] **Lazy loading:** Fetch body only when needed (metadata first)
- [ ] **Compression:** Enable IMAP compression if supported
- [ ] **Prefetching:** Predict next action and prefetch data
- [ ] **Index building:** Build local search index for common queries
- [ ] **Rate limiting:** Respect API limits to avoid throttling

---

## APPENDIX D: Troubleshooting Guide

### Issue: "OAuth token expired"
**Solution:**
```bash
hva setup-gmail  # Re-run OAuth flow
```

### Issue: "IMAP connection failed"
**Solution:**
1. Check email/password
2. Verify App Password (for Gmail)
3. Check network connection
4. Try port 993 (SSL) or 143 (STARTTLS)

### Issue: "Gmail API quota exceeded"
**Solution:**
1. Wait for quota reset (daily limit)
2. Enable caching to reduce API calls
3. Fall back to IMAP temporarily

### Issue: "Email not found"
**Solution:**
- Email may have been deleted
- Check email ID is correct
- Refresh folder list

---

**END OF SRS**

---

## 📝 SUMMARY

This SRS defines a **complete, production-ready Gmail integration** for HVA with:

✅ **Hybrid approach:** Gmail API + IMAP/SMTP  
✅ **High performance:** < 2s for most operations  
✅ **Security:** Encrypted credentials, OAuth 2.0  
✅ **Reliability:** Auto-fallback, retry logic, error handling  
✅ **LLM integration:** Summarization, smart replies  
✅ **Voice-first:** Natural language commands in Arabic & English  

**Ready for implementation by Antigravity Agent or development team.**

---

**Document Status:** ✅ Complete  
**Version:** 1.0  
**Date:** 2025-11-27  
**Approved for Implementation:** Pending