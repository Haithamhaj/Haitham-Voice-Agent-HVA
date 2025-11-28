"""Gmail utils package"""

from .text_processing import (
    extract_plain_text_from_html,
    parse_email_address,
    parse_email_list,
    clean_email_body,
    extract_snippet,
    remove_email_quotes,
    format_email_for_display
)

__all__ = [
    "extract_plain_text_from_html",
    "parse_email_address",
    "parse_email_list",
    "clean_email_body",
    "extract_snippet",
    "remove_email_quotes",
    "format_email_for_display"
]
