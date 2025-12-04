"""
HVA Configuration Management

Central configuration for the Haitham Voice Agent system.
Loads environment variables, sets paths, and defines system constants.
"""

import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class for HVA"""
    
    # ==================== API KEYS ====================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Optional: Google Sheets credentials for Memory module
    GOOGLE_SHEETS_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    
    # ==================== PATHS ====================
    # Base directory for HVA data
    HVA_HOME: Path = Path.home() / ".hva"
    
    # Subdirectories
    CREDENTIALS_DIR: Path = HVA_HOME / "credentials"
    CACHE_DIR: Path = HVA_HOME / "cache"
    LOGS_DIR: Path = HVA_HOME / "logs"
    MEMORY_DIR: Path = HVA_HOME / "memory"
    
    # Ensure directories exist
    @classmethod
    def ensure_directories(cls):
        """Create all required directories if they don't exist"""
        for directory in [cls.HVA_HOME, cls.CREDENTIALS_DIR, cls.CACHE_DIR, 
                         cls.LOGS_DIR, cls.MEMORY_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    # ==================== LLM MODELS ====================
    # Gemini model is resolved dynamically via resolve_gemini_model()
    
    # GPT model for actions, plans, tools, classification
    GPT_MODEL: str = "gpt-5"
    
    # Embedding model for Memory module
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # ==================== MODEL MAPPING ====================
    # Logical model names → actual API model strings
    # This allows us to upgrade models in ONE place without touching routing logic
    MODEL_MAPPING = {
        "logical.nano":        "gpt-5-mini",       # Keep nano fast
        "logical.nano-plus":   "gpt-5-mini",       
        "logical.mini":        "gpt-5",            # UPGRADED: Main workhorse is now Premium (User Request)
        "logical.premium":     "gpt-5",            # High intelligence (Standard)
        "logical.thinking":    "gpt-5-thinking",   # Reasoning model
        "logical.doc-gemini":  "logical.gemini.pro", # Delegate to Gemini mapping
    }
    
    @classmethod
    def resolve_model(cls, logical_name: str) -> str:
        """
        Resolve a logical model name to the actual API model string.
        If the logical name is unknown, fall back to a safe default.
        
        Args:
            logical_name: Logical model name (e.g., "logical.mini")
            
        Returns:
            str: Actual API model string (e.g., "gpt-4o")
        """
        mapped = cls.MODEL_MAPPING.get(logical_name, cls.MODEL_MAPPING["logical.mini"])
        # If mapped value is another logical name (e.g. logical.doc-gemini -> logical.gemini.pro),
        # resolve it using the appropriate resolver
        if mapped.startswith("logical.gemini"):
            return cls.resolve_gemini_model(mapped)
        return mapped
    
    # ==================== GEMINI MAPPING ====================
    # Gemini-specific logical model mapping (initialized at startup)
    # This is populated by calling resolve_gemini_mapping() from tools.gemini
    GEMINI_MAPPING: Dict[str, str] = {}
    
    @classmethod
    def init_gemini_mapping(cls):
        """
        Initialize Gemini model mapping by discovering available models.
        Should be called once at startup.
        """
        try:
            from haitham_voice_agent.tools.gemini.model_discovery import resolve_gemini_mapping
            cls.GEMINI_MAPPING = resolve_gemini_mapping()
        except Exception as e:
            import logging
            logging.warning(f"Failed to initialize Gemini mapping: {e}. Using fallbacks.")
            # Safe fallbacks
            cls.GEMINI_MAPPING = {
                "logical.gemini.flash": "gemini-2.0-flash-exp",
                "logical.gemini.pro": "gemini-2.0-flash-exp",
            }
    
    @classmethod
    def resolve_gemini_model(cls, logical_name: str) -> str:
        """
        Resolve a Gemini logical model name to the actual API model string.
        If the logical name is unknown, fall back to Pro (quality first).
        
        Args:
            logical_name: Logical Gemini model name (e.g., "logical.gemini.flash")
            
        Returns:
            str: Actual API model string (e.g., "gemini-2.0-flash-exp")
        """
        # Ensure mapping is initialized
        if not cls.GEMINI_MAPPING:
            cls.init_gemini_mapping()
        
        # Return mapped value or fallback to Pro
        return cls.GEMINI_MAPPING.get(
            logical_name,
            cls.GEMINI_MAPPING.get("logical.gemini.pro", "gemini-2.0-flash-exp")
        )
    
    # ==================== VOICE SETTINGS ====================
    # Supported languages
    SUPPORTED_LANGUAGES = ["ar", "en"]
    
    # Ollama Settings (Local Intelligence)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")  # Optimized for speed/accuracy balance
    
    # STT settings
    STT_LANGUAGE_AR: str = "ar-SA"
    STT_LANGUAGE_EN: str = "en-US"
    
    # ==================== VOICE & WHISPER CONFIG ====================
    
    # Whisper Model Profiles (faster-whisper)
    # Names correspond to official Whisper models: tiny, base, small, medium, large-v2, large-v3
    WHISPER_MODEL_NAMES = {
        "realtime": "large-v3",   # High quality for interactive commands (with fallback to medium)
        "session":  "large-v3",   # Heaviest model for long recordings
    }

    # ==================== STT ROUTER CONFIG ====================
    W2V2_AR_MODEL_NAME: str = "jonatasgrosman/wav2vec2-large-xlsr-53-arabic"
    
    STT_ROUTER_CONFIG = {
        "offline_mode": False,  # Changed to False to allow Google Cloud
        "lang_detect": {
            "max_seconds": 5.0,
            "min_confidence": 0.6
        },
        "english": {
            "backend": "whisper_en"
        },
        "arabic": {
            "primary_backend": "google_cloud", # Updated to match reality
            "min_valid_chars": 8,
            "require_arabic_chars": True,
            "min_confidence": 0.7,
            "log_rejections": True,
        }
    }
    
    # Strict STT Filtering Configuration
    STT_STRICT_CONFIG = {
        "min_confidence": 0.50,   # Lowered for better acceptance (was 0.70)
        "min_length": 6,          # Minimum characters
        "max_realtime_seconds": 10.0  # Threshold for treating as long speech/note
    }

    # Arabic Normalization Configuration
    AR_NORMALIZATION = {
        "enabled": True,
        "mode_command": {
            "enabled": True,
            "max_chars": 200,
            "model_logical": "logical.nano", # Maps to gpt-4o-mini
            "temperature": 0.1
        },
        "mode_session": {
            "enabled": False,           # IMPORTANT: disabled by default
            "max_chars": 2000,
            "model_logical": "logical.nano",
            "temperature": 0.1
        },
        "min_ar_chars": 10,
        "min_length_for_correction": 10
    }
    
    # VAD / Recognition defaults for Command Mode
    VOICE_VAD_CONFIG = {
        "pause_threshold": 0.8,   # Faster turn-taking (was 1.0)
        "energy_threshold": 300,  # Initial energy threshold
        "dynamic_energy_threshold": True,
    }
    
    # Session recording directory
    VOICE_SESSION_DIR: Path = HVA_HOME / "sessions"
    
    # TTS settings (macOS voices)
    TTS_VOICE_AR: str = "Majed"
    TTS_VOICE_EN: str = "Samantha"
    
    # Alternative English voice
    TTS_VOICE_EN_ALT: str = "Alex"

    # Detailed TTS Configuration
    TTS_CONFIG = {
        "ar": {
            "voice": "Majed",
            "rate": 150  # Slower for clarity
        },
        "en": {
            "voice": "Samantha",
            "rate": 180  # Standard rate
        }
    }
    
    # ==================== AUDIO FEEDBACK SETTINGS ====================
    # Enable/Disable Text-to-Speech (Visual Mode: False)
    TTS_ENABLED: bool = False
    
    # Enable/Disable Sound Effects (Ping, Success, Error)
    SOUND_EFFECTS_ENABLED: bool = True
    
    # macOS System Sounds (using afplay)
    SOUNDS = {
        "start_listening": "/System/Library/Sounds/Tink.aiff",
        "processing": "/System/Library/Sounds/Pop.aiff",
        "success": "/System/Library/Sounds/Glass.aiff",
        "error": "/System/Library/Sounds/Basso.aiff",
        "notification": "/System/Library/Sounds/Ping.aiff"
    }
    
    # ==================== PERFORMANCE SETTINGS ====================
    # Timeouts (seconds)
    STT_TIMEOUT: int = 10
    LLM_TIMEOUT: int = 30
    GMAIL_API_TIMEOUT: int = 10
    
    # Cache TTL (seconds)
    EMAIL_CACHE_TTL: int = 300  # 5 minutes
    SEARCH_CACHE_TTL: int = 120  # 2 minutes
    LABELS_CACHE_TTL: int = 600  # 10 minutes
    DRAFTS_CACHE_TTL: int = 60   # 1 minute
    SUMMARY_CACHE_TTL: int = 1800  # 30 minutes
    
    # ==================== GMAIL SETTINGS ====================
    # Gmail API scopes
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    # Calendar API scopes
    CALENDAR_SCOPES = [
        'https://www.googleapis.com/auth/calendar'
    ]
    
    # Drive API scopes
    DRIVE_SCOPES = [
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Gmail API rate limiting (requests per second)
    GMAIL_API_RATE_LIMIT: int = 10
    
    # IMAP/SMTP settings (fallback)
    IMAP_SERVER: str = "imap.gmail.com"
    IMAP_PORT: int = 993
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    
    # Connection pool size for IMAP
    IMAP_POOL_SIZE: int = 3
    
    # ==================== MEMORY SETTINGS ====================
    # SQLite database path
    MEMORY_DB_PATH: Path = MEMORY_DIR / "hva_memory.db"
    
    # Vector DB settings
    VECTOR_DB_TYPE: str = "chroma"  # or "faiss"
    VECTOR_DB_PATH: Path = MEMORY_DIR / "vector_db"
    
    # Knowledge graph path
    KNOWLEDGE_GRAPH_PATH: Path = MEMORY_DIR / "knowledge_graph.pkl"
    
    # Classification confidence threshold
    CLASSIFICATION_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Semantic search similarity threshold
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.7
    
    # Number of related memories to include
    MAX_RELATED_MEMORIES: int = 3
    
    # Retraining frequency (number of corrections)
    CLASSIFIER_RETRAIN_FREQUENCY: int = 50
    
    # ==================== SECURITY SETTINGS ====================
    # Encryption key name in macOS Keychain
    KEYCHAIN_SERVICE: str = "HVA"
    KEYCHAIN_ENCRYPTION_KEY: str = "encryption_key"
    
    # Sensitivity levels for memory
    MEMORY_SENSITIVITY_LEVELS = ["public", "private", "confidential"]
    
    # ==================== LOGGING SETTINGS ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = LOGS_DIR / "hva.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ==================== SYSTEM SETTINGS ====================
    # System version
    HVA_VERSION: str = "1.0.0"
    
    # Created by
    CREATED_BY: str = f"HVA v{HVA_VERSION}"
    
    # Maximum retries for operations
    MAX_RETRIES: int = 3
    
    # Exponential backoff settings
    RETRY_MIN_WAIT: int = 2
    RETRY_MAX_WAIT: int = 10
    
    # ==================== VALIDATION ====================
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration is present
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        errors = []
        
        # Check required API keys
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is not set")
        
        # Ensure directories exist
        try:
            cls.ensure_directories()
        except Exception as e:
            errors.append(f"Failed to create directories: {e}")
        
        if errors:
            print("Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def get_config_summary(cls) -> str:
        """
        Get a summary of current configuration (for debugging)
        
        Returns:
            str: Configuration summary
        """
        return f"""
HVA Configuration Summary:
==========================
Version: {cls.HVA_VERSION}
HVA Home: {cls.HVA_HOME}

LLM Models:
  - Gemini Flash: {cls.resolve_gemini_model("logical.gemini.flash")}
  - Gemini Pro:   {cls.resolve_gemini_model("logical.gemini.pro")}
  - GPT: {cls.GPT_MODEL}
  - Embeddings: {cls.EMBEDDING_MODEL}

Voice Settings:
  - Languages: {', '.join(cls.SUPPORTED_LANGUAGES)}
  - TTS Arabic: {cls.TTS_VOICE_AR}
  - TTS English: {cls.TTS_VOICE_EN}

Memory:
  - Database: {cls.MEMORY_DB_PATH}
  - Vector DB: {cls.VECTOR_DB_TYPE} at {cls.VECTOR_DB_PATH}

API Keys:
  - OpenAI: {'✓ Set' if cls.OPENAI_API_KEY else '✗ Missing'}
  - Gemini: {'✓ Set' if cls.GEMINI_API_KEY else '✗ Missing'}
  - Sheets: {'✓ Set' if cls.GOOGLE_SHEETS_CREDENTIALS else '✗ Not configured'}
"""


# Initialize directories on import
Config.ensure_directories()


# Convenience function for validation
def validate_config() -> bool:
    """Validate configuration and print summary"""
    is_valid = Config.validate()
    if is_valid:
        print("✓ Configuration is valid")
        print(Config.get_config_summary())
    return is_valid


if __name__ == "__main__":
    # Test configuration
    validate_config()
