"""
Text Processing Utilities for Gmail

Email parsing, cleaning, and formatting utilities.
From Gmail Module SRS Section 3.2.
"""

import re
import html
import logging
from typing import List, Tuple
from email.utils import parseaddr, parsedate_to_datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_plain_text_from_html(html_content: str) -> str:
    """
    Extract plain text from HTML email body
    
    Args:
        html_content: HTML content
        
    Returns:
        str: Plain text
    """
    try:
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        return text
        
    except Exception as e:
        logger.error(f"Failed to extract text from HTML: {e}")
        return html_content  # Return original if parsing fails


def parse_email_address(email_str: str) -> Tuple[str, str]:
    """
    Parse email address string into name and email
    
    Args:
        email_str: Email string (e.g., "John Doe <john@example.com>")
        
    Returns:
        tuple: (name, email)
    """
    name, email = parseaddr(email_str)
    return name.strip(), email.strip()


def parse_email_list(email_list_str: str) -> List[str]:
    """
    Parse comma-separated email list
    
    Args:
        email_list_str: Comma-separated emails
        
    Returns:
        list: Email addresses
    """
    if not email_list_str:
        return []
    
    emails = []
    for email_str in email_list_str.split(','):
        name, email = parse_email_address(email_str.strip())
        if email:
            emails.append(email)
    
    return emails


def clean_email_body(body: str, max_length: Optional[int] = None) -> str:
    """
    Clean email body text
    
    Args:
        body: Email body
        max_length: Optional maximum length
        
    Returns:
        str: Cleaned text
    """
    # Remove excessive newlines
    body = re.sub(r'\n{3,}', '\n\n', body)
    
    # Remove leading/trailing whitespace
    body = body.strip()
    
    # Truncate if needed
    if max_length and len(body) > max_length:
        body = body[:max_length] + "..."
    
    return body


def extract_snippet(body: str, length: int = 100) -> str:
    """
    Extract snippet from email body
    
    Args:
        body: Email body
        length: Snippet length
        
    Returns:
        str: Snippet
    """
    # Clean body
    cleaned = clean_email_body(body)
    
    # Take first N characters
    if len(cleaned) <= length:
        return cleaned
    
    # Find last space before length
    snippet = cleaned[:length]
    last_space = snippet.rfind(' ')
    
    if last_space > 0:
        snippet = snippet[:last_space]
    
    return snippet + "..."


def remove_email_quotes(body: str) -> str:
    """
    Remove quoted text from email body
    
    Args:
        body: Email body
        
    Returns:
        str: Body without quotes
    """
    lines = body.split('\n')
    clean_lines = []
    
    for line in lines:
        # Skip lines that start with > (quote marker)
        if line.strip().startswith('>'):
            continue
        
        # Skip lines that look like forwarded messages
        if re.match(r'^-+\s*Forwarded message\s*-+', line, re.IGNORECASE):
            break
        
        # Skip lines that look like original messages
        if re.match(r'^On .+ wrote:', line):
            break
        
        clean_lines.append(line)
    
    return '\n'.join(clean_lines).strip()


def format_email_for_display(from_: str, subject: str, date: str, body: str, max_body_length: int = 500) -> str:
    """
    Format email for TTS display
    
    Args:
        from_: Sender
        subject: Subject
        date: Date string
        body: Body text
        max_body_length: Maximum body length
        
    Returns:
        str: Formatted email text
    """
    name, email = parse_email_address(from_)
    sender = name if name else email
    
    # Clean and truncate body
    clean_body = clean_email_body(body, max_body_length)
    
    formatted = f"""
From: {sender}
Subject: {subject}
Date: {date}

{clean_body}
""".strip()
    
    return formatted


if __name__ == "__main__":
    # Test text processing
    print("Testing text processing utilities...")
    
    # Test HTML extraction
    html = "<p>Hello <b>world</b>!</p><script>alert('test')</script>"
    text = extract_plain_text_from_html(html)
    print(f"HTML to text: {text}")
    
    # Test email parsing
    email_str = "John Doe <john@example.com>"
    name, email = parse_email_address(email_str)
    print(f"Parsed: name='{name}', email='{email}'")
    
    # Test snippet
    long_text = "This is a very long email body that needs to be truncated to a shorter snippet for display purposes."
    snippet = extract_snippet(long_text, 30)
    print(f"Snippet: {snippet}")
    
    print("\nText processing test completed")
