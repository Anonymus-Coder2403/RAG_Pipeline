"""
Production Configuration Management
Centralized config with environment-specific settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""

    # Project paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    PDF_DIR = DATA_DIR / "pdf"
    VECTOR_STORE_DIR = DATA_DIR / "vector_store"
    UPLOAD_DIR = DATA_DIR / "uploads"  # Temp storage for user uploads

    # Ensure directories exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # RAG Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))

    # LLM Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))

    # File Upload Configuration
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
    MAX_FILES_PER_SESSION = int(os.getenv("MAX_FILES_PER_SESSION", "5"))

    # Session Configuration
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    USE_SESSION_COLLECTIONS = os.getenv("USE_SESSION_COLLECTIONS", "true").lower() == "true"

    # Performance
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Security
    ENABLE_VIRUS_SCAN = os.getenv("ENABLE_VIRUS_SCAN", "false").lower() == "true"
    SANITIZE_FILENAMES = os.getenv("SANITIZE_FILENAMES", "true").lower() == "true"

    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """Validate critical configuration"""
        if not cls.GEMINI_API_KEY:
            return False, "GEMINI_API_KEY not found in environment variables"

        if not cls.VECTOR_STORE_DIR.exists():
            return False, f"Vector store directory not found: {cls.VECTOR_STORE_DIR}"

        return True, None

    @classmethod
    def get_summary(cls) -> dict:
        """Get configuration summary (safe for logging)"""
        return {
            "embedding_model": cls.EMBEDDING_MODEL,
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "top_k": cls.TOP_K_RESULTS,
            "gemini_model": cls.GEMINI_MODEL,
            "max_file_size_mb": cls.MAX_FILE_SIZE_MB,
            "session_collections": cls.USE_SESSION_COLLECTIONS,
            "log_level": cls.LOG_LEVEL,
        }


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ENABLE_VIRUS_SCAN = True


# Select config based on environment
ENV = os.getenv("ENVIRONMENT", "development").lower()
config = ProductionConfig if ENV == "production" else DevelopmentConfig
