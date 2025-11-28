"""
Email LLM Prompts Configuration

Centralized prompt templates for email LLM operations.
Allows easy customization of tone and style.
"""

# ==================== SUMMARIZATION PROMPTS (Gemini) ====================

SUMMARIZE_EMAIL_PROMPT = """
Summarize the following email concisely and professionally.

Email:
{email_text}

Provide a clear summary that captures:
- Main topic/purpose
- Key points
- Any requests or action items mentioned

Keep the summary brief (2-3 sentences).
"""

SUMMARIZE_EMAIL_DETAILED_PROMPT = """
Provide a detailed summary of the following email.

Email:
{email_text}

Include:
1. **Main Topic**: What is this email about?
2. **Key Points**: List the main points discussed
3. **Action Items**: Any tasks or requests mentioned
4. **Sentiment**: Overall tone (professional, urgent, casual, etc.)

Format as structured sections.
"""

SUMMARIZE_THREAD_PROMPT = """
Summarize the following email thread/conversation.

Thread:
{thread_text}

Provide:
1. **Thread Topic**: Overall subject
2. **Participants**: Who is involved
3. **Key Decisions**: Any decisions made
4. **Action Items**: Tasks assigned or pending
5. **Current Status**: Where the conversation stands

Keep it concise but comprehensive.
"""

# ==================== ACTION EXTRACTION PROMPTS (Gemini) ====================

EXTRACT_ACTIONS_PROMPT = """
Extract all action items and tasks from the following email.

Email:
{email_text}

For each action item, identify:
- Task description
- Assignee (if mentioned)
- Deadline (if mentioned)
- Priority (if mentioned or inferred)

Format as a structured list. If no action items found, return "No action items detected."
"""

EXTRACT_ACTIONS_THREAD_PROMPT = """
Extract all action items from the following email thread.

Thread:
{thread_text}

For each action item:
- Task description
- Who mentioned it
- Assignee (if specified)
- Deadline (if mentioned)
- Status (pending, completed, discussed)

Group by status and priority.
"""

# ==================== SMART REPLY PROMPTS (GPT) ====================

GENERATE_REPLY_PROMPT = """
Generate a professional email reply to the following email.

Original Email:
From: {from_email}
Subject: {subject}
Body:
{body}

Reply Style: {style}
Tone: {tone}

Generate a {reply_type} reply that:
- Addresses the main points
- Is professional and clear
- Matches the requested tone
- Is concise

Return ONLY the reply body text, no subject line.
"""

GENERATE_REPLY_STYLES = {
    "professional": "formal and business-appropriate",
    "casual": "friendly but professional",
    "brief": "very concise and to the point",
    "detailed": "thorough and comprehensive"
}

GENERATE_REPLY_TONES = {
    "positive": "enthusiastic and positive",
    "neutral": "balanced and objective",
    "apologetic": "understanding and apologetic",
    "grateful": "appreciative and thankful"
}

GENERATE_REPLY_TYPES = {
    "accept": "accepting the request or invitation",
    "decline": "politely declining",
    "acknowledge": "acknowledging receipt",
    "request_info": "requesting more information",
    "general": "general response"
}

# ==================== TRANSLATION PROMPTS (Gemini) ====================

TRANSLATE_EMAIL_PROMPT = """
Translate the following email to {target_language}.

Email:
{email_text}

Requirements:
- Maintain professional tone
- Preserve formatting
- Keep technical terms accurate
- Ensure cultural appropriateness

Provide only the translated text.
"""

LANGUAGE_NAMES = {
    "ar": "Arabic",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese",
    "ja": "Japanese"
}

# ==================== SENTIMENT ANALYSIS PROMPTS (Gemini) ====================

ANALYZE_SENTIMENT_PROMPT = """
Analyze the sentiment and tone of the following email.

Email:
{email_text}

Provide:
1. **Overall Sentiment**: (Positive/Neutral/Negative)
2. **Tone**: (Professional/Casual/Urgent/Friendly/etc.)
3. **Urgency Level**: (High/Medium/Low)
4. **Key Emotions**: Any notable emotions expressed

Be concise and objective.
"""

# ==================== HELPER FUNCTIONS ====================

def get_reply_style_description(style: str) -> str:
    """Get description for reply style"""
    return GENERATE_REPLY_STYLES.get(style, "professional and clear")


def get_reply_tone_description(tone: str) -> str:
    """Get description for reply tone"""
    return GENERATE_REPLY_TONES.get(tone, "balanced and objective")


def get_reply_type_description(reply_type: str) -> str:
    """Get description for reply type"""
    return GENERATE_REPLY_TYPES.get(reply_type, "general response")


def get_language_name(lang_code: str) -> str:
    """Get full language name from code"""
    return LANGUAGE_NAMES.get(lang_code, lang_code)
