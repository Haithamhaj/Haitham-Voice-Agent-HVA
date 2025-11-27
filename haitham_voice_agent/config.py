"""
HVA Configuration Management

Central configuration for the Haitham Voice Agent system.
Loads environment variables, sets paths, and defines system constants.
"""

import os
from pathlib import Path
from typing import Optional
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
    # Gemini model for analysis, summarization, translation
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # GPT model for actions, plans, tools, classification
    GPT_MODEL: str = "gpt-4o"
    
    # Embedding model for Memory module
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # ==================== VOICE SETTINGS ====================
    # Supported languages
    SUPPORTED_LANGUAGES = ["ar", "en"]
    
    # STT settings
    STT_LANGUAGE_AR: str = "ar-SA"
    STT_LANGUAGE_EN: str = "en-US"
    
    # TTS settings (macOS voices)
    TTS_VOICE_AR: str = "Majed"
    TTS_VOICE_EN: str = "Samantha"
    
    # Alternative English voice
    TTS_VOICE_EN_ALT: str = "Alex"
    
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
  - Gemini: {cls.GEMINI_MODEL}
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
